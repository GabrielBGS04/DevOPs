"""Experimentos locais reais B1. Executar só com pipelines livres: --execute.

O laboratório cria dados próprios e interrompe temporariamente IA/integrações.
Não apaga dados. Sempre tenta restaurar os componentes interrompidos.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import paho.mqtt.client as mqtt


ROOT = Path(__file__).resolve().parents[2]
SP = timezone(timedelta(hours=-3), 'America/Sao_Paulo')


def timestamp():
    return datetime.now(SP).isoformat(timespec='milliseconds')


class Lab:
    def __init__(self):
        self.run_id = datetime.now(SP).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
        self.http = httpx.Client(timeout=10, trust_env=False)
        self.stopped = set()
        self.document = None
        self.destination = None

    def begin(self, challenge):
        self.destination = ROOT / f'docs/evidencias/b1/desafio-{challenge:02d}/execucao.json'
        if self.destination.exists():
            archive = self.destination.with_name('dados-execucao-anterior-' +
                                                datetime.now(SP).strftime('%Y%m%d-%H%M%S') +
                                                '-' + uuid.uuid4().hex[:6] + '.json')
            archive.write_bytes(self.destination.read_bytes())
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                capture_output=True, text=True, check=True).stdout.strip()
        source_hashes = {}
        for directory in ['services/ia/app', 'services/integracoes/app', 'src/main/java']:
            for path in sorted((ROOT / directory).rglob('*')):
                if path.is_file() and path.suffix in {'.py', '.json', '.java'}:
                    source_hashes[str(path.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(path.read_bytes()).hexdigest()
        source_hashes['scripts/b1/laboratorio.py'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.document = {
            'desafio': challenge, 'runId': self.run_id, 'inicio': timestamp(),
            'fuso': 'America/Sao_Paulo (UTC-03:00)', 'commitBase': commit,
            'alteracoesLocais': True, 'sha256Fontes': source_hashes,
            'comando': f'{sys.executable} scripts/b1/laboratorio.py --execute --only {challenge}',
            'estado': 'EM_EXECUCAO', 'passos': [], 'verificacoes': [],
        }
        self.save()

    def save(self):
        self.destination.parent.mkdir(parents=True, exist_ok=True)
        self.destination.write_text(json.dumps(self.document, ensure_ascii=False, indent=2), encoding='utf-8')

    def record(self, name, **data):
        step = {'nome': name, 'data': timestamp(), **data}
        self.document['passos'].append(step)
        self.save()
        print(json.dumps(step, ensure_ascii=False), flush=True)
        return step

    def check(self, name, condition, observed=None):
        self.document['verificacoes'].append({'nome': name, 'passou': bool(condition), 'observado': observed})
        self.save()
        if not condition:
            raise AssertionError(f'{name}: {observed!r}')

    def request(self, name, method, path, payload=None, port=8080, allow_error=False):
        url = f'http://127.0.0.1:{port}{path}'
        started = time.monotonic()
        try:
            response = self.http.request(method, url, json=payload)
            try:
                body = response.json()
            except ValueError:
                body = None
            step = self.record(name, metodo=method, url=url, payload=payload,
                               status=response.status_code, duracaoMs=round((time.monotonic()-started)*1000, 3),
                               resposta=body, respostaRaw=response.text)
            if not allow_error:
                response.raise_for_status()
            return step
        except httpx.RequestError as error:
            step = self.record(name, metodo=method, url=url, payload=payload, status=None,
                               duracaoMs=round((time.monotonic()-started)*1000, 3), erro=repr(error))
            if not allow_error:
                raise
            return step

    def poll(self, name, path, predicate, port=8080, timeout=35):
        deadline = time.monotonic() + timeout
        while True:
            step = self.request(name, 'GET', path, port=port, allow_error=True)
            if step['status'] == 200 and predicate(step.get('resposta')):
                return step['resposta']
            if time.monotonic() >= deadline:
                raise TimeoutError(f'{name}: estado esperado não observado em {timeout}s')
            time.sleep(1)

    def health(self, component):
        port = {'core': 8080, 'ia': 8001, 'integracoes': 8002}[component]
        path = '/actuator/health' if component == 'core' else '/health'
        status = 'UP' if component == 'core' else 'ok'
        return self.poll(f'{component}-saudavel', path, lambda body: body.get('status') == status, port)

    def artifacts(self, component):
        directory = ROOT / f'infra/.runtime/last-good/{component}'
        artifact_name = 'app.jar' if component == 'core' else 'app.zip'
        for name in [artifact_name, 'source-commit.txt', 'test-result.txt']:
            artifact = directory / name
            if not artifact.is_file():
                raise FileNotFoundError(f'Preflight: artefato last-good ausente: {artifact}; nenhum componente deve ser parado')
        return directory

    def run_command(self, command, timeout):
        # Um serviço pode herdar handles do helper. Arquivo evita esperar EOF
        # de um pipe mantido aberto pelo processo de longa duração.
        directory = self.destination.parent / 'comandos'
        directory.mkdir(parents=True, exist_ok=True)
        logfile = directory / f'{self.run_id}-{uuid.uuid4().hex[:8]}.log'
        with logfile.open('w', encoding='utf-8') as output:
            result = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT, timeout=timeout)
        return subprocess.CompletedProcess(command, result.returncode,
            logfile.read_text(encoding='utf-8', errors='replace'), '')

    def stop(self, component):
        # Um pipeline de falha pode ter apagado seu workspace; last-good sobrevive.
        artifacts = self.artifacts(component)
        self.record(f'preflight-restauracao-{component}', artefatos=str(artifacts))
        command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                   str(ROOT / 'scripts/b1/infra-component-stop.ps1'), '-Component', component]
        result = self.run_command(command, timeout=30)
        self.record(f'parar-{component}', comando=command, exitCode=result.returncode,
                    stdout=result.stdout, stderr=result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f'Não foi possível parar {component}: {result.stderr}')
        self.stopped.add(component)
        port = {'core': 8080, 'ia': 8001, 'integracoes': 8002}[component]
        path = '/actuator/health' if component == 'core' else '/health'
        stopped = self.request(f'{component}-indisponivel-confirmado', 'GET', path, port=port, allow_error=True)
        self.check(f'{component} realmente indisponível', stopped['status'] is None, stopped)

    def restore(self, component):
        artifacts = self.artifacts(component)
        command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                   str(ROOT / 'scripts/b1/infra-deploy.ps1'), '-Component', component,
                   '-Artifacts', str(artifacts)]
        result = self.run_command(command, timeout=90)
        self.record(f'restaurar-{component}', comando=command, exitCode=result.returncode,
                    stdout=result.stdout, stderr=result.stderr)
        if result.returncode != 0:
            raise RuntimeError(f'Não foi possível restaurar {component}: {result.stderr}')
        self.health(component)
        self.stopped.discard(component)

    def dataset(self, suffix):
        student = self.request(f'criar-aluno-{suffix}', 'POST', '/api/alunos',
                               {'nome': f'B1 Experimento {self.run_id} {suffix}', 'plano': 'BASICO'})['resposta']
        course = self.request(f'criar-curso-{suffix}', 'POST', '/api/cursos',
                              {'nome': f'B1 Curso {self.run_id} {suffix}'})['resposta']
        self.check('aluno básico inicia sem bônus', student['cursosDisponiveis'] == 0, student)
        return student, course

    def conclusion(self, name, student, course):
        result = self.request(name, 'POST', f"/api/alunos/{student['id']}/concluir-curso",
                              {'cursoId': course['id'], 'nota': 8.5})
        self.check(f'{name}: HTTP200, bônus3 e histórico', result['status'] == 200
                   and result['resposta']['cursosDisponiveis'] == 3
                   and result['resposta']['historico'].get(course['nome']) == 8.5, result['resposta'])
        return result

    def challenge3(self):
        self.health('ia')
        student, course = self.dataset('D3')
        active = self.request('ia-disponivel-recomendacoes', 'GET', f"/api/alunos/{student['id']}/recomendacoes")
        self.check('recomendação disponível ordenada e limitada', active['resposta']['disponivel'] is True
                   and 0 < len(active['resposta']['recomendacoes']) <= 3
                   and [item['id'] for item in active['resposta']['recomendacoes']] == sorted(
                       item['id'] for item in active['resposta']['recomendacoes']), active['resposta'])
        assistant = self.request('ia-disponivel-assistente', 'POST', '/api/assistente',
                                 {'pergunta': 'Como funciona o bônus?'})
        self.check('assistente respondeu conteúdo local e fonte', assistant['resposta']['disponivel'] is True
                   and assistant['resposta']['fonte'] == 'conteudo-local/bonus', assistant['resposta'])
        self.stop('ia')
        try:
            fallback = self.request('ia-indisponivel-recomendacoes', 'GET', f"/api/alunos/{student['id']}/recomendacoes")
            self.check('fallback explícito com lista vazia', fallback['status'] == 200
                       and fallback['resposta'] == {'disponivel': False, 'recomendacoes': []}, fallback)
            fallback_assistant = self.request('ia-indisponivel-assistente', 'POST', '/api/assistente',
                                               {'pergunta': 'Como funciona o bônus?'})
            self.check('assistente degradado', fallback_assistant['status'] == 200
                       and fallback_assistant['resposta']['disponivel'] is False, fallback_assistant)
            self.conclusion('core-conclui-sem-ia', student, course)
        finally:
            self.restore('ia')
        self.document['conclusao'] = ('IA ativa respondeu recomendação e conteúdo local; IA parada produziu HTTP200 '
                                     'degradado e o Core confirmou conclusão com bônus3. Tempos medidos constam nos passos; '
                                     'não se trata de modelo ML ou teste de timeout lento.')

    def challenge4(self):
        self.health('integracoes')
        self.poll('baseline-outbox-vazia', '/api/notificacoes/pendentes', lambda body: body['quantidade'] == 0)
        student, course = self.dataset('D4')
        core_log = ROOT / 'infra/.runtime/core.stdout.log'
        log_offset = core_log.stat().st_size if core_log.exists() else 0
        self.stop('integracoes')
        try:
            synchronous = self.request('sincrono-falha-esperada', 'POST', '/notificacoes', {
                'eventId': f'sincrono-{uuid.uuid4()}', 'alunoId': student['id'], 'cursoId': course['id'], 'nota': 8.5,
            }, port=8002, allow_error=True)
            self.check('notificação síncrona não foi confirmada', synchronous['status'] is None, synchronous)
            self.conclusion('assincrono-conclusao-disponivel', student, course)
            first = self.request('outbox-pendente-imediata', 'GET', '/api/notificacoes/pendentes')
            self.check('uma pendência gravada', first['resposta']['quantidade'] == 1, first['resposta'])
            self.record('aguardar-retentativas', segundos=10)
            time.sleep(10)
            later = self.request('outbox-pendente-apos10s', 'GET', '/api/notificacoes/pendentes')
            self.check('pendência preservada durante falha', later['resposta']['quantidade'] == 1, later['resposta'])
            if core_log.exists():
                with core_log.open('rb') as stream:
                    stream.seek(log_offset)
                    lines = stream.read().decode('utf-8', errors='replace').splitlines()
            else:
                lines = []
            failures = [line for line in lines if 'permanece pendente eventId=' in line]
            failed_ids = sorted(set(re.findall(r'eventId=([^\s]+)', '\n'.join(failures))))
            self.record('log-core-pendencia-retentativas', arquivo=str(core_log.relative_to(ROOT)), linhas=failures, eventIds=failed_ids)
            self.check('log identifica evento persistente', len(failed_ids) == 1 and len(failures) >= 2,
                       {'eventIds': failed_ids, 'falhas': len(failures)})
        finally:
            self.restore('integracoes')
        received = self.poll('receptor-recuperado-evento-entregue', '/notificacoes',
                             lambda body: any(item['alunoId'] == student['id'] and item['cursoId'] == course['id'] for item in body),
                             port=8002, timeout=30)
        matching = [item for item in received if item['alunoId'] == student['id'] and item['cursoId'] == course['id']]
        self.check('mesmo eventId foi entregue uma vez', len(matching) == 1 and matching[0]['eventId'] in failed_ids, matching)
        self.document['eventIdOutbox'] = matching[0]['eventId']
        self.poll('outbox-sem-pendencias-apos-recuperacao', '/api/notificacoes/pendentes', lambda body: body['quantidade'] == 0)
        duplicate = self.request('receptor-deduplica-repeticao', 'POST', '/notificacoes', matching[0], port=8002)
        self.check('receptor confirmou duplicado', duplicate['resposta']['duplicado'] is True, duplicate['resposta'])
        self.document['conclusao'] = ('Com receptor parado, tentativa síncrona falhou, mas conclusão/bônus3 foram confirmados '
                                     'e uma pendência permaneceu por10s com retentativas do mesmo eventId. Após restauração, '
                                     'o mesmo identificador foi recebido uma vez, outbox esvaziou e repetição foi deduplicada. '
                                     'Não comprova atomicidade distribuída ou envio real de mensagem.')

    def publish(self, name, event):
        import threading
        connected = threading.Event()
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                             client_id='b1-lab-' + uuid.uuid4().hex[:10], protocol=mqtt.MQTTv311)
        client.on_connect = lambda client, userdata, flags, reason, properties: connected.set() if reason == 0 else None
        started = time.monotonic()
        client.connect('127.0.0.1', 1883, keepalive=30)
        client.loop_start()
        try:
            if not connected.wait(10):
                raise TimeoutError('Conexão MQTT não confirmada')
            publication = client.publish('b1/atividades', json.dumps(event, ensure_ascii=False).encode(), qos=1)
            publication.wait_for_publish(timeout=10)
            self.check('broker confirmou publicação QoS1', publication.is_published(), publication.rc)
            self.record(name, broker='127.0.0.1:1883', topico='b1/atividades', qos=1,
                        mid=publication.mid, payload=event, duracaoMs=round((time.monotonic()-started)*1000, 3),
                        confirmacao='PUBACK do broker; aceitação pelo Core verificada separadamente')
        finally:
            client.disconnect()
            client.loop_stop()

    def wait_event(self, event_id):
        return self.poll('gateway-confirma-evento-' + event_id, '/gateway/eventos',
                         lambda body: any(item['eventId'] == event_id and item['status'] == 'ENTREGUE' for item in body), port=8002)

    def student_has_one_bonus(self, name, student, course):
        state = self.request(name, 'GET', f"/api/alunos/{student['id']}")['resposta']
        self.check(name + ': bônus3 e uma conclusão', state['cursosDisponiveis'] == 3
                   and state['historico'] == {course['nome']: 8.5}, state)
        return state

    def challenge5(self):
        self.health('integracoes')
        student, course = self.dataset('D5-normal')
        normal = {'eventId': str(uuid.uuid4()), 'tipo': 'CONCLUSAO', 'dispositivoId': 'b1-simulador-local',
                  'alunoId': student['id'], 'cursoId': course['id'], 'nota': 8.5}
        self.publish('mqtt-publicacao-normal', normal)
        self.wait_event(normal['eventId'])
        self.student_has_one_bonus('core-confirmou-mqtt-normal', student, course)
        offline_student, offline_course = self.dataset('D5-offline')
        offline = dict(normal, eventId=str(uuid.uuid4()), alunoId=offline_student['id'], cursoId=offline_course['id'])
        self.stop('integracoes')
        try:
            self.publish('mqtt-publicado-com-gateway-offline', offline)
            unchanged = self.request('core-antes-da-reconexao', 'GET', f"/api/alunos/{offline_student['id']}")['resposta']
            self.check('evento offline ainda não aplicou recompensa', unchanged['cursosDisponiveis'] == 0
                       and unchanged['historico'] == {}, unchanged)
            self.record('janela-gateway-offline', segundos=2)
            time.sleep(2)
        finally:
            self.restore('integracoes')
        self.wait_event(offline['eventId'])
        self.student_has_one_bonus('core-apos-reconexao', offline_student, offline_course)
        self.publish('mqtt-retransmissao-mesmo-eventId', offline)
        time.sleep(2)
        self.student_has_one_bonus('core-apos-retransmissao-mqtt', offline_student, offline_course)
        duplicate = self.request('core-entrada-idempotente-mesmo-eventId', 'POST', '/api/iot/eventos', offline)
        self.check('Core aceitou repetição idempotente', duplicate['status'] == 200 and duplicate['resposta']['aceito'] is True,
                   duplicate['resposta'])
        self.student_has_one_bonus('core-apos-repeticao-direta', offline_student, offline_course)
        # Janela entre receber MQTT e confirmar HTTP: spool deve sobreviver à queda.
        midflight_student, midflight_course = self.dataset('D5-spool')
        midflight = dict(normal, eventId=str(uuid.uuid4()), alunoId=midflight_student['id'], cursoId=midflight_course['id'])
        self.poll('outbox-vazia-antes-reinicio-core', '/api/notificacoes/pendentes', lambda body: body['quantidade'] == 0)
        # Verificar ambos os artefatos antes da primeira interrupção dessa janela.
        self.artifacts('core')
        self.artifacts('integracoes')
        self.stop('core')
        try:
            self.publish('mqtt-recebido-gateway-com-core-offline', midflight)
            pending = self.poll('spool-pendente-core-offline', '/gateway/eventos', lambda body: any(
                item['eventId'] == midflight['eventId'] and item['status'] == 'PENDENTE'
                and item['tentativas'] >= 1 and item['ultimoErro'] for item in body), port=8002)
            captured = next(item for item in pending if item['eventId'] == midflight['eventId'])
            self.record('spool-duravel-antes-queda-gateway', evento=captured)
            self.stop('integracoes')
            self.restore('core')
            before_recovery = self.request('core-reiniciado-antes-recuperar-spool', 'GET', f"/api/alunos/{midflight_student['id']}")['resposta']
            self.check('Core preservou aluno e ainda não recebeu evento pendente', before_recovery['cursosDisponiveis'] == 0
                       and before_recovery['historico'] == {}, before_recovery)
        finally:
            for component in ['core', 'integracoes']:
                if component in self.stopped:
                    self.restore(component)
        self.wait_event(midflight['eventId'])
        self.student_has_one_bonus('core-apos-recuperacao-spool-duravel', midflight_student, midflight_course)
        self.publish('mqtt-retransmissao-apos-recuperacao-spool', midflight)
        self.request('core-repeticao-apos-recuperacao-spool', 'POST', '/api/iot/eventos', midflight)
        self.student_has_one_bonus('spool-recuperado-aplicou-bonus-uma-vez', midflight_student, midflight_course)
        self.document['eventIdNormal'] = normal['eventId']
        self.document['eventIdOffline'] = offline['eventId']
        self.document['eventIdSpool'] = midflight['eventId']
        self.document['conclusao'] = ('QoS1 e gateway ativo entregaram evento normal. Publicação com gateway parado não alterou '
                                     'o Core; após reconexão da sessão persistente, o evento foi entregue e concedeu bônus3. '
                                     'Retransmissão MQTT e repetição direta no Core preservaram uma conclusão e bônus3. '
                                     'Com Core parado, outro evento ficou PENDENTE após tentativa HTTP; gateway também foi parado '
                                     'e reiniciado, recuperou o spool e entregou uma vez após retorno do Core. Demonstra cenário '
                                     'local; não injeta queda na janela exata após commit do Core e antes do PUBACK.')

    def finish(self, error=None):
        self.document['fim'] = timestamp()
        self.document['estado'] = 'FALHOU' if error else 'PASSOU'
        if error:
            self.document['erro'] = repr(error)
        self.save()
        if not error:
            self.update_readme()

    def update_readme(self):
        path = self.destination.with_name('README.md')
        original = path.read_text(encoding='utf-8')
        original = re.sub(r'\*\*Estado:\*\*[^\n]*', '**Estado:** EXPERIMENTO EXECUTADO; capturas de tela verificadas separadamente.', original)
        rows = [
            ('Data e horário', self.document['inicio'] + ' a ' + self.document['fim']),
            ('Commit e alterações locais relevantes', f"Base `{self.document['commitBase']}` com implementação B1 local; SHA256 dos fontes no JSON."),
            ('Dados e condições iniciais', f"Dados exclusivos da execução `{self.run_id}`; aluno BASICO inicialmente sem bônus."),
            ('Comando ou requisição exata', f"`services/ia/.venv/Scripts/python.exe scripts/b1/laboratorio.py --execute --only {self.document['desafio']}`"),
            ('Resultado observado', f"{len(self.document['verificacoes'])} verificações reais aprovadas; HTTP, payloads, erros provocados, IDs e duração registrados em [execucao.json](execucao.json)."),
            ('Conclusão e limites', self.document['conclusao']),
            ('Logs e relatórios de apoio', '[Execução estruturada integral](execucao.json), incluindo comandos de parada/restauração e hashes dos fontes.'),
        ]
        block = '## Registro da execução\n\n| Campo | Registro |\n| --- | --- |\n'
        block += '\n'.join(f'| {label} | {value} |' for label, value in rows) + '\n\n'
        before = original.split('## Registro da execução')[0]
        tail = original.split('Após salvar cada PNG', 1)
        path.write_text(before + block + ('Após salvar cada PNG' + tail[1] if len(tail) == 2 else ''), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Executar interrupções temporárias autorizadas no laboratório local')
    parser.add_argument('--only', choices=['3', '4', '5', 'all'], default='all')
    args = parser.parse_args()
    if not args.execute:
        parser.error('Passe --execute somente depois de confirmar que os pipelines estão livres.')
    lab = Lab()
    try:
        challenges = [3, 4, 5] if args.only == 'all' else [int(args.only)]
        for challenge in challenges:
            lab.begin(challenge)
            try:
                getattr(lab, f'challenge{challenge}')()
            except Exception as error:
                lab.finish(error)
                raise
            else:
                lab.finish()
                print(f'DESAFIO {challenge}: PASSOU — {lab.destination}', flush=True)
    finally:
        restore_errors = []
        for component in ['core', 'ia', 'integracoes']:
            if component in lab.stopped:
                try:
                    lab.restore(component)
                except Exception as error:
                    restore_errors.append((component, repr(error)))
        lab.http.close()
        if restore_errors:
            raise RuntimeError(f'Restauração exige atenção: {restore_errors}')


if __name__ == '__main__':
    main()
