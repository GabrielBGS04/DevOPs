from types import SimpleNamespace
import sys
import time

import pytest

from scripts.b1 import laboratorio


@pytest.fixture
def lab(tmp_path, monkeypatch):
    monkeypatch.setattr(laboratorio, 'ROOT', tmp_path)
    instance = laboratorio.Lab()
    instance.document = {'passos': [], 'verificacoes': []}
    instance.destination = tmp_path / 'evidence.json'
    yield instance
    instance.http.close()


def test_missing_last_good_prevents_stopping_a_live_component(lab, monkeypatch):
    commands = []
    monkeypatch.setattr(laboratorio.subprocess, 'run', lambda *args, **kwargs: commands.append(args))
    with pytest.raises(FileNotFoundError, match='last-good'):
        lab.stop('integracoes')
    assert commands == []
    assert lab.stopped == set()


def test_restore_uses_last_good_even_if_latest_pipeline_artifacts_are_missing(lab, tmp_path, monkeypatch):
    stable = tmp_path / 'infra/.runtime/last-good/integracoes'
    stable.mkdir(parents=True)
    (stable / 'app.zip').write_bytes(b'preserved successful artifact')
    (stable / 'source-commit.txt').write_text('commit')
    (stable / 'test-result.txt').write_text('PASS')
    commands = []

    def command(args, **kwargs):
        commands.append(args)
        return SimpleNamespace(returncode=0, stdout='restored', stderr='')

    monkeypatch.setattr(laboratorio.subprocess, 'run', command)
    monkeypatch.setattr(lab, 'health', lambda component: None)
    lab.stopped.add('integracoes')
    lab.restore('integracoes')
    assert commands[0][-2:] == ['-Artifacts', str(stable)]
    assert lab.stopped == set()


def test_core_health_uses_core_port_and_actuator_path(lab, monkeypatch):
    polls = []

    def poll(name, path, predicate, port, **kwargs):
        polls.append((path, port))
        assert predicate({'status': 'UP'})
        return {'status': 'UP'}

    monkeypatch.setattr(lab, 'poll', poll)
    assert lab.health('core') == {'status': 'UP'}
    assert polls == [('/actuator/health', 8080)]


@pytest.mark.parametrize('missing', ['source-commit.txt', 'test-result.txt'])
def test_incomplete_last_good_metadata_prevents_stop(lab, tmp_path, monkeypatch, missing):
    stable = tmp_path / 'infra/.runtime/last-good/integracoes'
    stable.mkdir(parents=True)
    for name in ['app.zip', 'source-commit.txt', 'test-result.txt']:
        if name != missing:
            (stable / name).write_text('successful artifact')
    commands = []
    monkeypatch.setattr(laboratorio.subprocess, 'run', lambda *args, **kwargs: commands.append(args))
    with pytest.raises(FileNotFoundError, match=missing):
        lab.stop('integracoes')
    assert commands == []


def test_helper_returns_without_waiting_for_a_service_inheriting_stdout(lab):
    # Um helper termina, mas o serviço recém-criado mantém os handles herdados.
    helper = ('import subprocess,sys; '
              'subprocess.Popen([sys.executable,"-c","import time;time.sleep(3)"],'
              'close_fds=False); print("helper-complete")')
    started = time.monotonic()
    result = lab.run_command([sys.executable, '-c', helper], timeout=10)
    elapsed = time.monotonic() - started
    assert result.returncode == 0
    assert 'helper-complete' in result.stdout
    assert elapsed < 2
