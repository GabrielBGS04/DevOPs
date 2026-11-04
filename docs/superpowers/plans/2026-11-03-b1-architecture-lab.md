# Plano de implementação do B1 Architecture Lab

> Para execução por agentes: aplicar `superpowers:executing-plans` e implementar as tarefas em sequência. Os checkboxes indicam trabalho pendente; nenhum experimento foi executado pela criação deste documento.

**Goal:** entregar os seis desafios do B1 sobre o MVP da AC1 com decisões rastreáveis e comprovação reproduzível.

**Architecture:** modularizar o Core Java incrementalmente, isolar a política de recompensa e manter um banco relacional. Integrar um FastAPI demonstrativo de IA, um processo Python de integrações e MQTT; demonstrar operação com Jenkins, Prometheus e Grafana.

**Tech Stack:** Java 17, Spring Boot na versão do projeto, Maven Wrapper, JPA, PostgreSQL, H2 para testes, Python/FastAPI/pytest, SQLite para deduplicação no receptor simulado, Mosquitto, Docker Compose, Jenkins, Micrometer, Prometheus e Grafana.

**Spec:** [Especificação do B1](../specs/2026-11-03-b1-design.md).

## Restrições globais

- Base correta: raiz `DEVOPS`, commit remoto verificado `bdb6943`; não usar a cópia interna `DevOPs/`.
- Preservar alterações locais anteriores. Não incluir a cópia interna ou arquivos gerados de `target/` em commits do B1.
- Preservar os endpoints e a regra da AC1: básico, nota ≥ 8,5, bônus de três cursos.
- Core Java/Spring Boot; IA Python; Jenkins, Prometheus e Grafana no desafio de operação.
- Manter a cobertura de 100% por classe já configurada, sem reduzir o limite para contornar testes.
- IA local demonstrativa; sem API paga, cloud ou dispositivo físico obrigatório.
- Todo resultado de teste e print deve vir de execução real. Não marcar tarefa como concluída com base apenas na existência do código.

## Foco de revisão

1. Limite de nota 8,49/8,5 e plano Premium não podem mudar na refatoração: validar nas tarefas 1 e 2.
2. IA lenta, indisponível ou com resposta inválida deve degradar em até dois segundos configurados de timeout HTTP, sem bloquear o Core: tarefa 3.
3. Receptor parado ou reiniciado não pode perder evento confirmado pelo Core nem duplicar o processamento do mesmo evento: tarefa 4.
4. Retransmissão MQTT e reconexão entre recebimento e confirmação HTTP não podem duplicar bônus: tarefa 5.
5. Teste ou build com falha deve impedir deploy; recuperação deve aparecer no monitoramento: tarefa 6.

## Estrutura de trabalho

| Local | Responsabilidade |
| --- | --- |
| `src/main/java/com/example/devops/` | Core e módulos incrementais `curso`, `aluno`, `ranking`, `gamificacao`, `integracao`, além de suporte compartilhado |
| `src/test/java/com/example/devops/` | Regressão, contratos de adapters, integrações HTTP e idempotência |
| `services/ia/` | FastAPI demonstrativo, conteúdo local, testes e Dockerfile |
| `services/integracoes/` | Receptor de notificações, gateway MQTT, testes e Dockerfile |
| `infra/` | Configurações de MQTT, Jenkins e observabilidade |
| `scripts/b1/` | Experimentos reproduzíveis em PowerShell, sem depender de dados previamente existentes |
| `docs/arquitetura/` e `docs/adr/` | Matriz cumulativa, seis decisões e diagramas |
| `docs/evidencias/b1/desafio-01/` a `desafio-06/` | Prints, logs e análise de cada experimento |

Cada tarefa inclui documentação, teste e evidência do próprio desafio. Não é preciso criar todas as pastas técnicas antes de utilizá-las.

## Tarefa 0 — preparar e registrar a situação inicial

**Arquivos:** configurações atuais, testes existentes e evidências em `docs/evidencias/b1/desafio-01/`.

**Entrada:** código da raiz confirmado com a branch `main` do GitHub.

**Saída:** baseline identificado, ambiente validado e print da organização anterior.

- [ ] Registrar commit, branch, status Git, versões de Java e Maven Wrapper.
- [ ] Capturar `desafio-01/01-camadas-antes.png` antes de mover classes. Mostrar o caminho da raiz e os pacotes em camadas.
- [ ] Executar `.\mvnw.cmd clean verify`; guardar log e os relatórios necessários fora de `target/`. Critério: testes sem falhas e `BUILD SUCCESS`, incluindo a verificação de cobertura.
- [ ] Validar Docker Desktop/engine e `docker compose version`; preparar o ambiente se indisponível, documentando o procedimento.
- [ ] Confirmar que o Compose atual sobe app e PostgreSQL. Preservar volumes com dados do usuário.

## Tarefa 1 — modularização e ranking

**Arquivos:** módulo `curso`, novo módulo `ranking`, imports afetados em `Aluno`/serviços/testes e documentação ADR-001/C4 Container.

**Interfaces:** preservar `POST/GET /api/cursos`; produzir `GET /api/ranking` com `alunoId`, `nome`, `cursosConcluidos`, `pontos`. A leitura de alunos para ranking deve passar por uma interface pública de consulta, sem importar repositórios internos.

- [ ] Escrever testes de ranking vazio, pontuação de 100 por entrada no histórico, ordem decrescente e desempate por ID crescente.
- [ ] Executar os testes novos e confirmar falha pela ausência do comportamento.
- [ ] Agrupar curso em `api`, `application`, `domain`, `internal/persistence`; manter nomes de entidade/tabela e contratos HTTP.
- [ ] Implementar o ranking didático especificado, com consulta projetada. Não incluir moedas ou regras dos ZIPs que mudem a AC1.
- [ ] Rodar `.\mvnw.cmd clean verify`; confirmar a regressão de alunos/cursos/conclusão e cobertura exigida.
- [ ] Gerar relatório de dependências antes/depois com imports de produção da funcionalidade e explicação das fronteiras. Capturar a árvore posterior e o endpoint com dados de teste identificáveis.
- [ ] Comparar as três alternativas do enunciado no ADR-001. Registrar limitações de escala e atualizar o C4 Container.
- [ ] Preencher a seção do desafio no registro cumulativo e conferir os três prints previstos no guia. Commit da tarefa com seleção explícita de arquivos do B1, após revisão.

## Tarefa 2 — política de bônus e adapters

**Arquivos:** módulo `gamificacao` para regra e caso de uso; interfaces de acesso a alunos/cursos; adapters JPA em produção e memória em testes; testes e ADR-002/C4 Component.

**Interfaces:** política pura `int calcularBonus(Plano plano, double nota)`; retornos: `3` para BASICO com nota ≥ 8,5 e `0` para os demais casos válidos. Validar plano presente e nota finita entre 0 e 10. O caso de conclusão continua registrando histórico e persistindo a alteração atomicamente.

- [ ] Escrever testes da política para BASICO 8,49 → 0; 8,5 → 3; 10 → 3; PREMIUM 10 → 0; nota fora do intervalo, NaN/infinito e plano ausente → erro sem alterar estado.
- [ ] Executar e confirmar a falha inicial da política extraída.
- [ ] Extrair a regra sem dependências Spring/JPA, fazendo `Aluno` reutilizá-la. Evitar duplicar a regra no serviço.
- [ ] Refatorar somente o acesso necessário ao caso de conclusão para interfaces e criar os adapters em memória e JPA.
- [ ] Executar um contrato comum nos dois adapters: criar/consultar aluno e curso, concluir com nota 8,5 e verificar histórico e bônus 3; nota 7,0 mantém bônus 0.
- [ ] Executar a suíte completa com `.\mvnw.cmd clean verify`; comprovar que os testes da política funcionam sem subir Spring.
- [ ] Documentar a inversão concreta e seu custo no ADR-002, atualizar o C4 Component e capturar os três prints. Commit da tarefa após revisão.

## Tarefa 3 — serviço Python e degradação

**Arquivos:** `services/ia/`, cliente HTTP/configuração/rotas no módulo `integracao` do Core, testes e ADR-003/C4 Container.

**Interfaces:** Core `GET /api/alunos/{id}/recomendacoes` e `POST /api/assistente` com `pergunta`; respostas distinguem `disponivel=true/false`. FastAPI recebe os dados necessários por HTTP; não acessa o banco do Core.

- [ ] Testar recomendação de até três cursos ausentes do histórico, resposta do conteúdo local e pergunta sem correspondência.
- [ ] Testar no Core IA normal, resposta inválida, conexão recusada e timeout: falha devolve lista vazia/mensagem de indisponibilidade com `disponivel=false`.
- [ ] Implementar os dois fluxos no mesmo serviço FastAPI, com timeout HTTP de dois segundos no Core. Não executar retentativas na thread da requisição.
- [ ] Acrescentar serviços `core` e `ia` ao Compose sem quebrar o banco existente. Registrar portas e variáveis efetivamente usadas.
- [ ] Disponibilizar `scripts/b1/desafio-03.ps1`: criar dados próprios, chamar IA ativa, parar somente `ia`, repetir consulta e concluir um curso; restaurar o serviço ao terminar.
- [ ] Executar a suíte Java e `python -m pytest -v` no ambiente Python do serviço. Validar os quatro modos do cliente HTTP.
- [ ] Executar o experimento real e guardar respostas/tempos. Capturar sucesso, degradação e Core funcionando com IA parada.
- [ ] Atualizar ADR-003 e C4, discutir ML/RAG juntos versus separados e declarar os limites da simulação. Commit da tarefa após revisão.

## Tarefa 4 — comunicação síncrona e assíncrona

**Arquivos:** outbox e worker no Core, receptor HTTP em `services/integracoes/`, testes e ADR-004/C4 Container/sequência.

**Interfaces:** evento de conclusão com identificador estável, aluno, curso e nota. Persistir evento e conclusão na mesma transação. Receptor Python confirma eventos e deduplica pelo identificador persistido em SQLite.

- [ ] Escrever teste de transação: conclusão com nota 8,5 grava bônus 3 e um evento pendente; rollback não deixa evento órfão.
- [ ] Escrever teste de entrega: HTTP indisponível mantém pendência; confirmação marca entrega; repetir o mesmo identificador não duplica processamento no receptor, inclusive após reinício.
- [ ] Implementar outbox e worker com timeout de dois segundos, polling de cinco segundos e identificador preservado nas retentativas. Usar processamento único no laboratório.
- [ ] Criar receptor de notificações simuladas com consulta dos eventos recebidos para conferência. Inicialmente usar um processo de integrações.
- [ ] Criar `scripts/b1/desafio-04.ps1` com comparação síncrona, conclusão assíncrona durante falha e recuperação do receptor. Não associar a chamada síncrona ao endpoint essencial.
- [ ] Rodar testes Java/Python e experimento real; registrar o mesmo evento pendente e posteriormente entregue, com timestamps.
- [ ] Comparar polling/outbox com broker dedicado, explicando custos e limites. Se discutir RabbitMQ/Kafka, relacioná-los aos requisitos, sem adicioná-los apenas para demonstração.
- [ ] Atualizar ADR-004, diagrama de sequência e os três prints. Commit da tarefa após revisão.

## Tarefa 5 — IoT e MQTT

**Arquivos:** `infra/mqtt/`, gateway no processo de integrações, entrada/inbox idempotente do Core, testes, simulador e ADR-005/C4 Container.

**Interfaces:** tópico `b1/atividades`; Core `POST /api/iot/eventos` com `eventId`, `tipo`, `dispositivoId`, `alunoId`, `cursoId`, `nota`. Tipos e tratamento estão fixados na especificação.

- [ ] Testar evento de conclusão duas vezes com mesmo ID: uma aplicação de bônus 3 e uma entrada lógica do evento.
- [ ] Testar presença/início sem recompensa, entrada inválida sem efeitos e erro de persistência sem confirmação indevida do recebimento.
- [ ] Implementar inbox transacional com unicidade de identificador e reutilizar o caso de conclusão da tarefa 2.
- [ ] Configurar Mosquitto com QoS 1 no fluxo, sessão persistente e volume. Usar confirmação MQTT posterior à aceitação HTTP no gateway.
- [ ] Criar simulador e `scripts/b1/desafio-05.ps1` com publicação normal, gateway desconectado/reconectado e retransmissão do mesmo evento. Guardar o identificador em todas as etapas.
- [ ] Rodar testes e laboratório com Mosquitto real; comprovar entrega após reconexão e recompensa sem duplicação.
- [ ] Atualizar ADR-005 e C4 com dispositivo, broker, gateway e Core. Explicar por que outro broker interno não foi necessário para a hipótese demonstrada.
- [ ] Preencher os três prints e os logs de publicação/recepção/consulta. Commit da tarefa após revisão.

## Tarefa 6 — Jenkins e observabilidade

**Arquivos:** Jenkinsfiles por executável; configuração do agente; `infra/observabilidade/`; métricas no Core; perfis Compose; testes e ADR-006/C4 Deployment.

**Interfaces:** pipelines `core`, `ia`, `integracoes` com teste → build de imagem → atualização local do componente; Core `/actuator/health` e `/actuator/prometheus`; Grafana provisionado com datasource e dashboard versionados.

- [ ] Configurar agente Jenkins com ferramentas e acesso ao engine de containers do laboratório. Registrar configuração reproduzível e armazenamento dos relatórios.
- [ ] Criar pipelines por componente. Teste ou build falho aborta os estágios posteriores; usar imagens identificadas pelo commit.
- [ ] Preservar testes/cobertura Java e rodar pytest nos dois componentes Python antes do build.
- [ ] Acrescentar Micrometer/Prometheus ao Core e métricas `b1_ia_falhas_total` e `b1_notificacoes_pendentes`, além das métricas HTTP. Não colocar identificadores de usuário/evento nas labels.
- [ ] Provisionar scrape do Core no Prometheus e painel Grafana com duração/erros HTTP, falhas da IA e pendências de notificação.
- [ ] Executar o pipeline normal no Jenkins e uma execução controlada que falhe no teste, confirmando que deploy não ocorre. Usar uma cópia temporária de teste no workspace descartável do agente, sem manter falha no código final.
- [ ] Rodar `scripts/b1/desafio-06.ps1`: carga pequena controlada, IA parada/restaurada e receptor parado/restaurado. Aguardar pelo menos dois ciclos de scrape antes de capturar os dados.
- [ ] Capturar os três prints no Jenkins/Grafana e guardar consultas/resultados do Prometheus. Relacionar a variação às decisões de tolerância e recuperação.
- [ ] Atualizar ADR-006, C4 Deployment e visão Container final. Commit da tarefa após revisão.

## Fechamento da entrega

- [ ] Conferir até três ASRs por desafio e pelo menos duas alternativas reais; usar as três alternativas onde o enunciado as enumera.
- [ ] Atualizar `docs/arquitetura/README.md` com RF/RNF, FURPS+ quando pertinente, matriz cumulativa de ASRs, RPCs e links para ADRs/C4/evidências.
- [ ] Informar a equipe real, link do repositório e síntese das decisões a levar para a AF.
- [ ] Confirmar 18 prints reais previstos no guia, legíveis e associados ao commit/comando correspondente. Capturas adicionais são permitidas quando melhorarem a comprovação.
- [ ] Confrontar cada afirmação de sucesso com log, teste ou execução correspondente. Descrever limitações e qualquer etapa ainda pendente.
- [ ] Revisar a seleção de arquivos antes de commit/push; preservar a cópia interna e alterações preexistentes fora da entrega.

## Roteiro dos prints

O [guia de comprovação](../../evidencias/b1/README.md) explica o conteúdo de cada captura, a ordem e o destino. A única captura disponível imediatamente, antes da implementação, é a estrutura original do Desafio 1. Os resultados dos demais desafios serão preenchidos durante a execução.
