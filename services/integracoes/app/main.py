import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .gateway import start_gateway
from .storage import Storage


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')


class Notification(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    eventId: str = Field(min_length=1, max_length=200)
    alunoId: int = Field(gt=0)
    cursoId: int = Field(gt=0)
    nota: float = Field(ge=0, le=10, allow_inf_nan=False)


def create_app(database=None):
    # Inicialização fica no lifespan para importar o app sem criar arquivos locais.
    @asynccontextmanager
    async def lifespan(app):
        app.state.storage = Storage(database or os.getenv(
            'B1_DB_PATH', str(Path(__file__).parents[1] / 'data' / 'integracoes.sqlite3')))
        running = None
        if os.getenv('B1_MQTT_ENABLED', 'false').lower() == 'true':
            running = start_gateway(
                app.state.storage, os.getenv('MQTT_HOST', 'localhost'),
                int(os.getenv('MQTT_PORT', '1883')),
                os.getenv('CORE_BASE_URL', 'http://127.0.0.1:8080'),
            )
        try:
            yield
        finally:
            if running:
                gateway, worker = running
                gateway.stopped.set()
                worker.join(timeout=10)
                gateway.broker.disconnect()
                gateway.broker.loop_stop()
                gateway.http.close()

    app = FastAPI(title='B1 Integrações', lifespan=lifespan)

    @app.get('/health')
    def health():
        return {'status': 'ok', 'servico': 'integracoes'}

    @app.post('/notificacoes')
    def notification(request: Notification):
        duplicate = app.state.storage.receive_notification(request.model_dump())
        return {'eventId': request.eventId, 'duplicado': duplicate}

    @app.get('/notificacoes')
    def notifications():
        return app.state.storage.notifications()

    @app.get('/gateway/eventos')
    def gateway_events():
        return app.state.storage.gateway_events()

    return app


app = create_app()
