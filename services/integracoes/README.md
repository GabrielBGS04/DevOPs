# Integrações B1

Um processo FastAPI reúne o receptor simulado de notificações e o gateway MQTT. SQLite preserva eventos recebidos, pendências e entregas entre reinícios. O banco do Core permanece privado ao Core.

Na raiz do repositório, com Python 3.12 e dependências instaladas no ambiente virtual:

```powershell
python -m venv services/integracoes/.venv
services/integracoes/.venv/Scripts/python.exe -m pip install -r services/integracoes/requirements-dev.txt
services/integracoes/.venv/Scripts/python.exe -m pytest services/integracoes/tests -v
$env:B1_MQTT_ENABLED = 'true'
$env:MQTT_HOST = '127.0.0.1'
$env:CORE_BASE_URL = 'http://127.0.0.1:8080'
services/integracoes/.venv/Scripts/python.exe -m uvicorn services.integracoes.app.main:app --host 127.0.0.1 --port 8002
```

No ambiente efetivamente testado, os dois serviços compartilham `services/ia/.venv`, que contém também Paho MQTT. Portanto, o mesmo executável `services/ia/.venv/Scripts/python.exe` pode executar os comandos acima depois de instalar também `services/integracoes/requirements-dev.txt`.

| Rota | Contrato |
| --- | --- |
| `GET /health` | `{"status":"ok","servico":"integracoes"}` |
| `POST /notificacoes` | Entrada: `{"eventId":"evt-1","alunoId":1,"cursoId":2,"nota":8.5}`. Saída: `{"eventId":"evt-1","duplicado":false}`; repetição retorna `duplicado:true` |
| `GET /notificacoes` | Lista os eventos únicos persistidos, mantendo o payload recebido originalmente |
| `GET /gateway/eventos` | Estado durável de cada evento MQTT: `eventId`, `status` (`PENDENTE`/`ENTREGUE`), `tentativas`, `ultimoErro`, `recebidoEm` e `entregueEm` |

O receptor usa chave primária SQLite no `eventId`, com gravação transacional e unicidade mesmo em requisições concorrentes. Nota deve ser finita entre 0 e 10; IDs devem ser positivos. Corpo inválido retorna 422 sem gravar. É uma simulação de recebimento, sem envio real de e-mail ou mensagem.

| Variável | Padrão |
| --- | --- |
| `B1_DB_PATH` | `services/integracoes/data/integracoes.sqlite3`; no contêiner: `/data/integracoes.sqlite3` |
| `B1_MQTT_ENABLED` | `false`; habilitar explicitamente com `true` |
| `MQTT_HOST` | `localhost` |
| `MQTT_PORT` | `1883` |
| `CORE_BASE_URL` | `http://127.0.0.1:8080` |

O gateway Paho usa MQTT 3.1.1, client ID estável `b1-gateway`, `clean_session=false`, subscrição QoS 1 em `b1/atividades` e `manual_ack=true`. O publicador deve usar QoS 1, e o Mosquitto deve habilitar persistência. Um único processo de integrações deve usar esse client ID.

Fluxo: persistir payload em SQLite → worker envia `POST /api/iot/eventos` → receber HTTP 2xx → persistir entrega → emitir PUBACK. A confirmação MQTT nunca ocorre só porque o evento foi gravado no spool. Falhas de conexão e respostas HTTP de erro mantêm a pendência e o worker tenta novamente a cada cinco segundos, com timeout HTTP de dois segundos por tentativa. Eventos rejeitados pelo Core permanecem pendentes para diagnóstico; mensagens JSON inválidas não são confirmadas. Os logs incluem `eventId` para correlação.

O spool permite recuperação mesmo se o processo cair antes da confirmação HTTP. O Core deve deduplicar `eventId` transacionalmente: uma queda depois da aceitação no Core e antes do registro de entrega local pode causar uma nova chamada HTTP. Depois do registro de entrega local, uma reentrega MQTT recebe ACK sem nova chamada ao Core. SQLite e volume do broker devem ser preservados; o laboratório não oferece atomicidade distribuída nem retenção ilimitada apropriada a produção.

Os sete testes cobrem deduplicação após reinício, concorrência, validação, ACK posterior à aceitação, HTTP 503, conexão indisponível, recuperação de pendência persistida e consulta da transição de falha para entrega. `tests/evidence` contém execuções reais RED/GREEN. Os testes HTTP do gateway usam transporte controlado; não substituem o experimento separado com Mosquitto real.

`Dockerfile` possui alvos `test` e `runtime`. O `Jenkinsfile` espera agente com label `docker` e engine/Compose local; testes antecedem build e deploy exclusivo de `integracoes`, com imagem `b1-integracoes:${B1_IMAGE_TAG}`. A execução nativa do laboratório é configurada separadamente na infraestrutura.
