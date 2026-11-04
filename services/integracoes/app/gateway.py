import json
import logging
import threading

import httpx
import paho.mqtt.client as mqtt


logger = logging.getLogger(__name__)


class Gateway:
    """Um worker por processo: persistir → HTTP Core → persistir sucesso → ACK."""

    def __init__(self, storage, broker, http=None, core_base_url='http://127.0.0.1:8080'):
        self.storage = storage
        self.broker = broker
        self.http = http if http is not None else httpx.Client(timeout=2)
        self.core_url = core_base_url.rstrip('/') + '/api/iot/eventos'
        self.waiting = {}
        self.lock = threading.RLock()
        self.stopped = threading.Event()

    def receive(self, mid: int, qos: int, raw: bytes):
        payload = json.loads(raw)
        if not isinstance(payload, dict) or not isinstance(payload.get('eventId'), str) or not payload['eventId'].strip():
            raise ValueError('eventId é obrigatório')
        event_id = payload['eventId']
        with self.lock:
            already_delivered = self.storage.enqueue(payload)
            if already_delivered:
                self.broker.ack(mid, qos)
                return
            self.waiting.setdefault(event_id, set()).add((mid, qos))
        logger.info('MQTT persistido eventId=%s mid=%s', event_id, mid)

    def deliver_pending(self):
        for payload in self.storage.pending_events():
            if self.stopped.is_set():
                break
            event_id = payload['eventId']
            try:
                response = self.http.post(self.core_url, json=payload, timeout=2)
                response.raise_for_status()
            except httpx.HTTPError as error:
                self.storage.failed(event_id, str(error))
                logger.warning('Core recusou/indisponível; pendência preservada eventId=%s: %s', event_id, error)
                continue
            with self.lock:
                self.storage.delivered(event_id)
                for mid, qos in self.waiting.pop(event_id, set()):
                    self.broker.ack(mid, qos)
            logger.info('Core aceitou; confirmação MQTT eventId=%s', event_id)

    def run(self):
        while not self.stopped.is_set():
            try:
                self.deliver_pending()
            except Exception:
                # Uma falha local não elimina a pendência nem encerra o worker.
                logger.exception('Falha no ciclo durável do gateway')
            self.stopped.wait(5)


def start_gateway(storage, host, port, core_base_url):
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id='b1-gateway', clean_session=False,
        protocol=mqtt.MQTTv311, manual_ack=True,
    )
    gateway = Gateway(storage, client, core_base_url=core_base_url)

    def connected(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe('b1/atividades', qos=1)
            logger.info('MQTT conectado; sessão persistente b1-gateway')

    def received(client, userdata, message):
        try:
            gateway.receive(message.mid, message.qos, message.payload)
        except Exception:
            logger.exception('Mensagem MQTT não confirmada; falha de validação/persistência')

    client.on_connect = connected
    client.on_message = received
    client.reconnect_delay_set(min_delay=1, max_delay=10)
    client.connect_async(host, port, keepalive=30)
    client.loop_start()
    worker = threading.Thread(target=gateway.run, name='mqtt-core-delivery', daemon=True)
    worker.start()
    return gateway, worker
