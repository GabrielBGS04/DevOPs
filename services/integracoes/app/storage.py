"""Persistência local do receptor simulado e da recuperação do gateway."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class Storage:
    def __init__(self, database):
        self.database = str(database)
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript('''
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS notifications (
                    event_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS mqtt_events (
                    event_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    delivered INTEGER NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    delivered_at TEXT
                );
            ''')

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.database, timeout=10)
        try:
            connection.execute('PRAGMA synchronous=FULL')
            with connection:
                yield connection
        finally:
            connection.close()

    def receive_notification(self, payload: dict) -> bool:
        with self.connect() as connection:
            cursor = connection.execute(
                'INSERT OR IGNORE INTO notifications(event_id,payload) VALUES (?,?)',
                (payload['eventId'], json.dumps(payload, ensure_ascii=False)),
            )
            return cursor.rowcount == 0

    def notifications(self) -> list[dict]:
        with self.connect() as connection:
            return [json.loads(row[0]) for row in connection.execute(
                'SELECT payload FROM notifications ORDER BY received_at,event_id')]

    def enqueue(self, payload: dict) -> bool:
        with self.connect() as connection:
            connection.execute(
                'INSERT OR IGNORE INTO mqtt_events(event_id,payload) VALUES (?,?)',
                (payload['eventId'], json.dumps(payload, ensure_ascii=False)),
            )
            return bool(connection.execute(
                'SELECT delivered FROM mqtt_events WHERE event_id=?',
                (payload['eventId'],),
            ).fetchone()[0])

    def pending_events(self) -> list[dict]:
        with self.connect() as connection:
            return [json.loads(row[0]) for row in connection.execute(
                'SELECT payload FROM mqtt_events WHERE delivered=0 ORDER BY received_at,event_id')]

    def delivered(self, event_id: str):
        with self.connect() as connection:
            connection.execute('''
                UPDATE mqtt_events SET delivered=1, delivered_at=CURRENT_TIMESTAMP,
                    attempts=attempts+1, last_error=NULL WHERE event_id=?
            ''', (event_id,))

    def failed(self, event_id: str, error: str):
        with self.connect() as connection:
            connection.execute('''
                UPDATE mqtt_events SET attempts=attempts+1,last_error=? WHERE event_id=?
            ''', (error, event_id))

    def gateway_events(self) -> list[dict]:
        with self.connect() as connection:
            rows = connection.execute('''
                SELECT event_id,delivered,attempts,last_error,received_at,delivered_at
                FROM mqtt_events ORDER BY received_at,event_id
            ''').fetchall()
        return [{
            'eventId': event_id, 'status': 'ENTREGUE' if delivered else 'PENDENTE',
            'tentativas': attempts, 'ultimoErro': error,
            'recebidoEm': received_at, 'entregueEm': delivered_at,
        } for event_id, delivered, attempts, error, received_at, delivered_at in rows]
