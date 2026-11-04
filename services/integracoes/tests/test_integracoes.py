import json
from concurrent.futures import ThreadPoolExecutor

import httpx
from fastapi.testclient import TestClient

from services.integracoes.app.main import create_app
from services.integracoes.app.storage import Storage
from services.integracoes.app.gateway import Gateway


NOTIFICATION = {'eventId': 'evt-1', 'alunoId': 1, 'cursoId': 2, 'nota': 8.5}
EVENT = dict(NOTIFICATION, tipo='CONCLUSAO', dispositivoId='simulador-1')


def test_receiver_deduplicates_after_process_restart(tmp_path):
    database = tmp_path / 'recebidos.sqlite3'
    with TestClient(create_app(database)) as client:
        assert client.post('/notificacoes', json=NOTIFICATION).json() == {
            'eventId': 'evt-1', 'duplicado': False}
    with TestClient(create_app(database)) as restarted:
        assert restarted.post('/notificacoes', json=NOTIFICATION).json() == {
            'eventId': 'evt-1', 'duplicado': True}
        assert restarted.get('/notificacoes').json() == [NOTIFICATION]


def test_concurrent_duplicates_are_processed_once(tmp_path):
    with TestClient(create_app(tmp_path / 'concurrent.sqlite3')) as client:
        with ThreadPoolExecutor(max_workers=6) as executor:
            replies = list(executor.map(
                lambda _: client.post('/notificacoes', json=NOTIFICATION).json(), range(12)))
        assert sum(not r['duplicado'] for r in replies) == 1
        assert len(client.get('/notificacoes').json()) == 1


def test_receiver_rejects_invalid_notification_without_persisting(tmp_path):
    with TestClient(create_app(tmp_path / 'validation.sqlite3')) as client:
        invalid = dict(NOTIFICATION, nota=11)
        assert client.post('/notificacoes', json=invalid).status_code == 422
        assert client.get('/notificacoes').json() == []
        assert client.get('/health').json() == {'status': 'ok', 'servico': 'integracoes'}


class BrokerConnection:
    def __init__(self):
        self.acks = []

    def ack(self, mid, qos):
        self.acks.append((mid, qos))
        return 0


def test_gateway_defers_ack_until_core_accepts_and_preserves_failed_event(tmp_path):
    requests = []

    def core(request):
        requests.append(json.loads(request.content))
        return httpx.Response(503)

    storage = Storage(tmp_path / 'gateway.sqlite3')
    broker = BrokerConnection()
    with httpx.Client(transport=httpx.MockTransport(core)) as http:
        gateway = Gateway(storage, broker, http=http)
        gateway.receive(42, 1, json.dumps(EVENT).encode())
        assert broker.acks == []
        gateway.deliver_pending()
    assert requests == [EVENT]
    assert broker.acks == []
    assert storage.pending_events() == [EVENT]


def test_gateway_recovers_pending_after_restart_and_deduplicates_redelivery(tmp_path):
    database = tmp_path / 'restart.sqlite3'
    before_restart = Storage(database)
    before_restart.enqueue(EVENT)
    requests = []

    def core(request):
        assert request.url.path == '/api/iot/eventos'
        requests.append(json.loads(request.content))
        return httpx.Response(200, json={'eventId': 'evt-1', 'duplicado': False})

    storage = Storage(database)
    broker = BrokerConnection()
    with httpx.Client(transport=httpx.MockTransport(core)) as http:
        gateway = Gateway(storage, broker, http=http)
        gateway.receive(43, 1, json.dumps(EVENT).encode())
        gateway.deliver_pending()
        assert storage.pending_events() == []
        assert broker.acks == [(43, 1)]
        gateway.receive(44, 1, json.dumps(EVENT).encode())
        gateway.deliver_pending()
    assert requests == [EVENT]
    assert broker.acks == [(43, 1), (44, 1)]


def test_gateway_connection_error_keeps_durable_pending(tmp_path):
    def offline(request):
        raise httpx.ConnectError('Core offline', request=request)

    storage = Storage(tmp_path / 'offline.sqlite3')
    broker = BrokerConnection()
    with httpx.Client(transport=httpx.MockTransport(offline)) as http:
        gateway = Gateway(storage, broker, http=http)
        gateway.receive(45, 1, json.dumps(EVENT).encode())
        gateway.deliver_pending()
    assert storage.pending_events() == [EVENT]
    assert broker.acks == []


def test_gateway_status_exposes_failure_then_delivery(tmp_path):
    with TestClient(create_app(tmp_path / 'status.sqlite3')) as client:
        storage = client.app.state.storage
        storage.enqueue(EVENT)
        with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503))) as http:
            Gateway(storage, BrokerConnection(), http=http).deliver_pending()
        pending = client.get('/gateway/eventos')
        assert pending.status_code == 200
        assert pending.json()[0]['eventId'] == 'evt-1'
        assert pending.json()[0]['status'] == 'PENDENTE'
        assert pending.json()[0]['tentativas'] == 1
        assert '503' in pending.json()[0]['ultimoErro']
        with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200))) as http:
            Gateway(storage, BrokerConnection(), http=http).deliver_pending()
        delivered = client.get('/gateway/eventos').json()[0]
        assert delivered['status'] == 'ENTREGUE'
        assert delivered['tentativas'] == 2
        assert delivered['ultimoErro'] is None
        assert delivered['entregueEm'] is not None
