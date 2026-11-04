# Execução do plano B1 Architecture Lab

Plano: plans/2026-11-03-b1-architecture-lab.md. Autorização do usuário: implementar os seis desafios, capturar prints reais e inseri-los no Word.

## Estado inicial

- Base GitHub/local confirmada: bdb6943, main. Cópia interna DevOPs preservada.
- Baseline executado em 03/11/2026: 45 testes, zero falhas/erros; clean verify e cobertura 100% por classe aprovados. Log em ../evidencias/b1/desafio-01/baseline-testes.log.
- Branch local de trabalho: codex/b1-architecture-lab.

## Decisões de execução

- Usar a pasta confirmada pelo usuário e branch local, preservando alterações prévias, sem criar nova cópia/worktree nem publicar no GitHub automaticamente.
- Paralelizar componentes independentes conforme skill dispatching-parallel-agents: Python, infraestrutura e integrações Java; alterações em arquivos distintos.
- Docker indisponível na conferência inicial: preparar execução nativa e portável de Jenkins, MQTT e monitoramento, mantendo configurações de containers. O banco do laboratório poderá usar H2 em arquivo, relacional, mantendo PostgreSQL para Compose. Registrar a tecnologia efetivamente executada no relatório.
- O documento final será uma cópia preenchida do enunciado com decisões e evidências por desafio; preservar o original em Downloads.

## Tarefas

- Preparação: baseline executado.
- Desafios 1/2: implementados e verificados. Ranking com projeção no banco; curso encapsula repositório; regra pura e adapters memória/JPA. Verificação final: 80 testes Java e 100% em 38 classes.
- Desafios 3/4/5: implementados e experimentados em 04/11/2026. JSONs PASSOU: 7, 9 e 20 verificações, respectivamente. Serviços restaurados após os testes.
- Desafio 6: Jenkins real, Core #3, IA #8 e integrações #4 com sucesso. IA #9 falhou por teste controlado e bloqueou deploy preservando last-good. Prometheus e Grafana registraram IA 0→2 e pendências 0→1→0.
- Python: 19 testes aprovados após corrigir a espera em pipes de subprocessos de longa duração.
- Capturas: 18 JPEGs reais com manifesto de hashes e datas. Word final: 39 páginas, seis resoluções e seis diagramas, com 18 prints incorporados; todas as páginas inspecionadas e original preservado.

## Revisão independente e correções verificadas

- Porta inbound aleatória do Jenkins foi desativada (`slaveAgentPort=-1`); auditoria registrou apenas listeners de loopback. O serviço HTTP já estava ligado a 127.0.0.1.
- Corrida na inbox IoT reproduzida em RED: `merge` com ID atribuído permitia bônus 6. Corrigido para INSERT incondicional com `persist/flush` em adapter Repository; teste determinístico e suíte final GREEN.
- Chamada HTTP da IA passou a ocorrer sem transação JPA aberta. Resposta disponível do assistente exige conteúdo e fonte não vazios; testes RED/GREEN.
- Artefatos aprovados agora persistem fora do workspace descartável do Jenkins. Validação ocorre antes de parar serviço; teste controlado preservou a release anterior e sua saúde.
- Experimento MQTT ampliado: Core indisponível após recebimento, spool PENDENTE com tentativa HTTP, reinício do gateway e recuperação com um único bônus.
- Roteiro de restauração usa log em arquivo em vez de capturar pipe herdado pelo serviço. Teste de regressão com processo filho real passou.

## Limites mantidos

- Laboratório de instância única e dados sintéticos; não certifica escala de 100 mil usuários, operação multiworker, ML/RAG real, execução Docker ou operação PostgreSQL.
- Os fontes e as evidências são versionados localmente; publicação no GitHub será informada conforme efetivamente realizada, sem declarar sincronização inexistente.
