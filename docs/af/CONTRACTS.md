# SkillPath AI — contratos propostos para integração

Versão inicial `v1`. Na fundação, o gateway reserva `/api/af` e seus subcaminhos e responde `503` com o código `AF_EM_PREPARACAO`. Os contratos a seguir definem o comportamento a implementar nas fases individuais.

## Identidade, formato e erros

- JSON UTF-8. Campos com nomes em português e `camelCase`. Datas em UTC no formato RFC 3339. IDs de job, evento, correlação, plano e ação são UUIDs.
- `alunoId` e `cursoId` são inteiros positivos do Core, com valores representáveis com exatidão pelo cliente JavaScript. A AF resolve a identidade do colaborador pelo vínculo entre o `sub` autenticado e o aluno no Core. `alunoId` no payload identifica o recurso e deve passar pela verificação de titularidade.
- Cada serviço público valida o token assinado apresentado em `Authorization: Bearer <token>`, incluindo emissor, audiência e expiração. RF02, RF03 e RF04 exigem usuário vinculado ao aluno. RF05 exige escopo de treinamento e as consultas retornam apenas jobs do solicitante. Uma identidade técnica com escopo dedicado e delegação verificável identifica chamadas internas. O gateway não aceita cabeçalhos de identidade vindos do navegador como prova de autorização.
- O gateway gera um `X-Request-Id` para cada requisição pública e repassa o valor aos serviços. O Core cria o `correlationId` do job e o mantém durante toda a execução. Logs usam esses identificadores e omitem tokens, conteúdo sensível e dados pessoais.
- Os erros usam `application/problem+json`, com `status`, `code`, `title`, `requestId` e, quando aplicável, `violations` com objetos `{ "field": "...", "code": "..." }`. O cliente toma decisões pelo `code`.

```json
{
  "status": 422,
  "code": "COMPETENCIAS_INVALIDAS",
  "title": "Verifique os valores das competências",
  "requestId": "c5c3adffc3e6483b9d05acbfbcce4c5e",
  "violations": [{ "field": "competencias[0].pontuacao", "code": "FORA_DO_INTERVALO" }]
}
```

| Código HTTP | Uso |
| --- | --- |
| `400` | JSON inválido, UUID inválido ou parâmetro obrigatório ausente. |
| `401` | Credencial ausente, inválida ou expirada. |
| `403` | Escopo insuficiente ou aluno informado fora da autorização do usuário. |
| `404` | Aluno ou recurso inexistente. Jobs e ações de outro titular também retornam `404`. |
| `409` | Chave idempotente reaproveitada com outros dados, ação expirada ou decisão incompatível com o estado. |
| `422` | Estrutura correta com campos inválidos, código de competência desconhecido ou conjunto de dados incompatível. |
| `429` | Limite de solicitações ou de concorrência atingido. |
| `502` | Dependência respondeu fora do contrato. |
| `503` | Dependência ou modelo indisponível, ou API ainda em preparação. |
| `504` | Orçamento de tempo da chamada síncrona excedido. |

As rotas do B1 preservam seus formatos e códigos, incluindo o fallback das rotas demonstrativas da IA.

## Superfície pública

| Método e caminho | Destino | Entrada | Sucesso |
| --- | --- | --- | --- |
| `POST /api/af/competencias/classificar` | Core | `{ alunoId, competencias }` | `200` com resultado e versão do modelo |
| `POST /api/af/treinamentos` | Core | `{ datasetId, datasetVersao }` e `Idempotency-Key` | `202` em `QUEUED` na criação. `200` com o estado atual em repetição válida. Ambos retornam `Location`. |
| `GET /api/af/treinamentos` | Core | `page`, `size` e `status`, opcionais | `200` com página de jobs do solicitante |
| `GET /api/af/treinamentos/{id}` | Core | UUID do job | `200` com estado atual |
| `POST /api/af/recomendacoes` | Spring AI | `{ alunoId, objetivo, limite? }` | `200` com recomendações e fontes |
| `POST /api/af/agente/planejar` | Spring AI | `{ alunoId, objetivo }` | `201` com plano e ações pendentes de decisão |
| `POST /api/af/agente/acoes/{id}/autorizar` | Spring AI | `{ decisao, versao }` e `Idempotency-Key` | `200` com decisão e resultado disponível |

## RF02 — classificação

Cada competência tem `codigo` estável em maiúsculas, com 1 a 64 caracteres ASCII de `A–Z`, `0–9` ou sublinhado, e `pontuacao` numérica finita entre 0 e 100. Aceitar de 1 a 50 competências, sem códigos repetidos. O catálogo de códigos e a ordem dos atributos fazem parte da versão do modelo. O conjunto exigido pelo modelo é validado antes da inferência.

```json
{
  "alunoId": 7,
  "competencias": [{ "codigo": "JAVA", "pontuacao": 82 }]
}
```

O Core verifica o aluno e chama `POST http://ml:8000/internal/v1/classificacoes` com credencial técnica e cabeçalho de rastreio. O corpo contém apenas `{ "competencias": [...] }`. FastAPI devolve o exemplo abaixo. O Core preserva os resultados e acrescenta `alunoId` à resposta pública.

```json
{
  "modeloVersao": "competencias-v1",
  "classificacoes": [
    { "codigo": "JAVA", "nivel": "AVANCADO", "confianca": 0.92 }
  ]
}
```

`nivel` admite `INICIANTE`, `INTERMEDIARIO` ou `AVANCADO`. `confianca` é um número finito entre 0 e 1. Deve existir um item por código recebido, na mesma ordem. O orçamento inicial do cliente Core é de 1,5 s totais, com conexão de até 300 ms e sem retentativa síncrona. O ensaio do RNF01 mede a latência pelo gateway e pode exigir ajuste.

## RF03 — recomendações

`objetivo` é texto de 1 a 1000 caracteres após remover espaços das pontas. `limite` aceita inteiro entre 1 e 10, com padrão 3. O Spring AI consulta `GET http://app:8080/internal/v1/alunos/{alunoId}/contexto-ia` com credencial técnica e delegação do titular. O Core devolve apenas `{ alunoId, cursosConcluidosIds, cursos: [{ cursoId, nome }] }`. O histórico legado persiste nomes e aceita cursos homônimos. O adaptador precisa registrar o ID nas novas conclusões e tratar entradas antigas ambíguas sem inferir IDs.

```json
{
  "alunoId": 7,
  "objetivo": "Melhorar práticas de testes automatizados",
  "limite": 3
}
```

```json
{
  "status": "FUNDAMENTADO",
  "recomendacoes": [
    {
      "cursoId": 12,
      "justificativa": "O curso cobre os cenários de regressão previstos no guia.",
      "fontes": [
        { "documentoId": "guia-qa", "versao": "1", "trechoId": "qa-17", "pagina": 4 }
      ]
    }
  ]
}
```

Cada curso deve existir no catálogo elegível e referenciar ao menos um trecho recuperado e permitido. `pagina` é opcional quando a fonte não tem paginação. Contexto insuficiente retorna `200` com `status: "SEM_EVIDENCIA"` e lista vazia. Falhas do provedor usam os erros de dependência. Ingestão, licença de uso, versionamento de corpus e verificação de citações ficam na fase de RF03.

## RF04 — planejamento e autorização

O planejamento recebe `{ alunoId, objetivo }`, com a mesma validação de objetivo do RF03. Responde com `planoId` e uma lista de propostas. Cada proposta traz dados imutáveis para exibição, efeito esperado e expiração definida no servidor.

```json
{
  "planoId": "4f5042bc-c675-449d-961f-3f6fab532f55",
  "acoes": [
    {
      "acaoId": "826bda15-cb69-4126-b242-2d8b5fe4e95c",
      "versao": 1,
      "tipo": "REGISTRAR_META_ESTUDO",
      "parametros": { "cursoId": 12 },
      "efeito": "Registrar a meta de estudar o curso selecionado",
      "status": "PENDENTE_AUTORIZACAO",
      "expiraEm": "2026-12-01T14:30:00Z"
    }
  ]
}
```

1. Spring AI valida a proposta contra a lista de ações permitidas, valida parâmetros e persiste ação, versão, titular, aluno, expiração e representação canônica dos parâmetros. A criação do plano é somente leitura quanto aos dados de negócio.
2. O navegador apresenta o efeito e envia `{ "decisao": "AUTORIZAR", "versao": 1 }` ou `{ "decisao": "RECUSAR", "versao": 1 }`, com `Idempotency-Key`. A decisão é explícita e vale apenas para a ação apresentada. O servidor revalida titular, escopo, versão, estado e validade e grava a decisão atomicamente.
3. O Spring AI executa somente após aprovação registrada, por chamada técnica a `POST http://app:8080/internal/v1/agente/efeitos`. O corpo contém `{ acaoId, versao, alunoId, tipo, parametros, expiraEm }`. A chamada usa `acaoId` como chave de execução e apresenta identidade técnica e uma autorização assinada para o Core com titular, aluno, ação, versão, tipo, hash dos parâmetros e validade. O Core valida titular, recurso e conteúdo da autorização e grava efeito e chave na mesma transação. O modelo e os documentos recuperados ficam sem acesso direto à operação de escrita.
4. A resposta pública final é `{ acaoId, status, resultado? }`, com `EXECUTADA` e referência do efeito, ou `RECUSADA`. Uma falha transitória após aprovação preserva `AUTORIZADA`. A mesma decisão e chave consultam ou retomam a execução sem duplicar efeitos. Ações vencidas retornam `409 ACAO_EXPIRADA`. O Core pode devolver um efeito já confirmado pela mesma chave após a expiração, sempre após validar o titular. Auditoria registra quem decidiu, qual ação e versão estavam em vigor, quando e qual foi o resultado.

## RF05 — API de treinamento

O POST recebe `{ "datasetId": "competencias-academico", "datasetVersao": "1" }`. O Core valida o par contra um catálogo permitido, com ambos os campos de 1 a 64 caracteres. O conjunto de dados é versionado e acessível ao worker por configuração interna. O Core grava o job e o evento na outbox na mesma transação e retorna `202` com `Location: /api/af/treinamentos/{id}`.

```json
{
  "id": "e8f7ceec-cb4b-4dd9-8b41-fc9242bffdf8",
  "correlationId": "e7da0553-d624-46a7-b594-c7c3a8b4cf59",
  "datasetId": "competencias-academico",
  "datasetVersao": "1",
  "status": "QUEUED",
  "criadoEm": "2026-12-01T14:00:00Z",
  "atualizadoEm": "2026-12-01T14:00:00Z"
}
```

O GET individual usa o mesmo formato. `COMPLETED` inclui `modeloVersao` e `FAILED` inclui `falha: { codigo, mensagem }` sem exceções internas. A lista usa `{ items, page, size, total }`, com página iniciando em 0, tamanho de 1 a 100 e padrão 20. Filtra por um estado conhecido quando `status` é informado. Ordena por `criadoEm` e `id` decrescentes.

`Idempotency-Key` tem 1 a 128 caracteres ASCII visíveis e é obrigatória nos POSTs de treinamento e decisão. O escopo abrange titular, operação e identificador da ação quando presente. Repetir com corpo semanticamente igual retorna o mesmo job ou decisão, incluindo seu estado atual. Corpo diferente com a mesma chave retorna `409 IDEMPOTENCIA_CONFLITANTE`. Persistir a chave junto do recurso impõe unicidade mesmo sob concorrência. Manter a chave pelo menos durante toda a retenção do recurso.

## RabbitMQ — treinamento e atualizações

Exchange durável `skillpath.af.training.v1` do tipo `topic`. Mensagens persistentes em JSON. Usar `eventId` como `message_id` AMQP e propagar `correlationId` na propriedade `correlation_id`. As filas duráveis abaixo têm retentativas limitadas e encaminhamento de mensagens inválidas ou esgotadas à fila de falhas correspondente, com alerta de operação.

| Chave de roteamento | Fila | Publica | Consome |
| --- | --- | --- | --- |
| `training.requested` | `skillpath.af.training.requests.v1` | Dispatcher da outbox do Core | `ml-worker` |
| `training.status.updated` | `skillpath.af.training.status.v1` | Dispatcher da outbox do worker | Core |

```json
{
  "schemaVersion": 1,
  "eventId": "aa25cb56-6048-49a9-a84e-dd32c1851830",
  "type": "training.requested",
  "jobId": "e8f7ceec-cb4b-4dd9-8b41-fc9242bffdf8",
  "correlationId": "e7da0553-d624-46a7-b594-c7c3a8b4cf59",
  "occurredAt": "2026-12-01T14:00:00Z",
  "payload": { "datasetId": "competencias-academico", "datasetVersao": "1" }
}
```

```json
{
  "schemaVersion": 1,
  "eventId": "52c65084-fb74-4e7f-8318-f1b11e3c221e",
  "type": "training.status.updated",
  "jobId": "e8f7ceec-cb4b-4dd9-8b41-fc9242bffdf8",
  "correlationId": "e7da0553-d624-46a7-b594-c7c3a8b4cf59",
  "occurredAt": "2026-12-01T14:00:04Z",
  "payload": { "revision": 1, "status": "RUNNING" }
}
```

- **Estados.** Criação gera `QUEUED` na revisão 0. O worker grava `RUNNING` na revisão 1 e emite `COMPLETED` com `modeloVersao` ou `FAILED` com `falha` na revisão 2. Estados terminais são imutáveis. Retentativas internas de execução mantêm `RUNNING`.
- **Publicação.** As outboxes só marcam eventos como entregues após confirmação do broker e ausência de retorno por falta de rota. Retentativas mantêm `eventId` e conteúdo.
- **Consumo.** O worker confirma o pedido após gravar recebimento em armazenamento durável, com unicidade por `jobId`. Um ciclo recuperável de processamento retoma jobs pendentes ou com lease vencido e invalida tentativas antigas antes que publiquem resultado. A gravação da versão publicada e a atualização terminal são idempotentes por job. A notificação do estado é registrada junto com a mudança local.
- **Aplicação de status.** O Core verifica `jobId`, `correlationId` e revisão. Registra `eventId` e aplica a transição na mesma transação. Mensagens fora de ordem ficam em inbox durável até a revisão anterior chegar. Uma lacuna persistente gera alerta para reconciliar ou reenviar o evento com o mesmo identificador. Duplicatas idênticas são confirmadas sem nova transição. Conflitos de revisão e mensagens inválidas seguem para tratamento de falhas.

## Serviços, portas e rotas

| Serviço Docker | Endereço interno | Situação e responsabilidade |
| --- | --- | --- |
| `gateway` | `http://gateway:80` | Fundação. Origem pública local `http://127.0.0.1:8088`. |
| `app` | `http://app:8080` | Core existente. Destino atual do proxy legado e futuro de competências e treinamentos. |
| `db` | `db:5432` | PostgreSQL existente. Esquemas AF e pgvector na fase de integração. |
| `ia` | `http://ia:8001` | IA demonstrativa B1 acessada pelo Core. |
| `integracoes` | `http://integracoes:8002` | Notificações B1 e ponte MQTT, com volume SQLite. |
| `mqtt` | `mqtt:1883` | Mosquitto B1 para o tópico `b1/atividades`. |
| `spring-ai` | `http://spring-ai:8081` | Proposto. Recomendações e agente, acessíveis pelo gateway. |
| `ml` | `http://ml:8000` | Proposto. HTTP interno de inferência, acessado pelo Core. |
| `ml-worker` | Rede interna, sem porta HTTP | Proposto. Consumidor de jobs, com a mesma imagem de `ml`. |
| `rabbitmq` | `amqp://rabbitmq:5672` | Proposto. Mensageria interna de treinamento. |
| `ollama` | `http://ollama:11434` | Proposto. Modelos de chat e embeddings selecionáveis por configuração. |

Rotas `/internal` ficam fora da superfície pública e exigem credencial própria mesmo na rede interna. Na fundação, aplicações e portas diretas anteriores devem ser usadas em laboratório local. O plano de integração prevê restringir a publicação de portas e encaminhar cada rota AF ao destino da tabela quando houver implementação validada.
