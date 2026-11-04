# Infraestrutura B1

O laboratório executado usa processos Windows portáveis reais em loopback: Java 25 executa o Jenkins 2.580.2; Mosquitto 2.0.22 recebe MQTT com persistência; Prometheus 3.7.3 coleta o Core; Grafana 12.3.0 consulta o Prometheus. O Core mantém `java.version=17`. `tools/` contém os downloads oficiais, e `infra/.runtime/` contém PIDs, logs, banco do Jenkins, séries temporais e dados locais; ambos são ignorados no Git.

## Reproduzir no Windows

Pré-requisitos: Java compatível com Jenkins, 7-Zip, acesso à rede para os downloads, Maven Wrapper do repositório e o ambiente Python `services/ia/.venv` instalado com as dependências dos dois serviços.

```powershell
.\scripts\b1\infra-download.ps1
.\scripts\b1\infra-start.ps1
.\scripts\b1\infra-jenkins.ps1 -Component ia
.\scripts\b1\infra-jenkins.ps1 -Component ia -ControlledFailure
```

- Jenkins: http://127.0.0.1:8081 — jobs `b1-core`, `b1-ia`, `b1-integracoes`.
- Grafana: http://127.0.0.1:3000/d/b1-operacao — dashboard provisionado, atualização de cinco segundos.
- Prometheus: http://127.0.0.1:9090 — coleta a cada cinco segundos.
- Mosquitto: `127.0.0.1:1883`, tópico de negócio `b1/atividades`, QoS 1.

Jenkins e Grafana dispensam login exclusivamente neste laboratório ligado a `127.0.0.1`. MQTT anônimo também aceita conexões somente em loopback. Não reutilizar essa configuração em host público. Jenkins conserva proteção CSRF, executa os Jenkinsfiles no sandbox Groovy e desliga o listener de agentes inbound (`slaveAgentPort=-1`). A auditoria de TCP/UDP dos processos e filhos está em `evidencias/listeners-loopback.json`: somente as sete portas locais previstas, sem endpoints UDP. Nenhuma credencial pessoal é necessária. A execução nativa não requer instalação de serviço ou administrador do Windows. No agente Codex, os downloads e o lançamento do Jenkins precisaram de execução fora do sandbox: a política de rede bloqueou downloads e a política de processos bloqueou `taskkill` durante o redeploy. O Jenkins iniciado nesse contexto permite que os jobs parem e restaurem seus próprios processos.

Cada pipeline copia os fontes para seu workspace descartável, executa testes reais e gera um artefato nativo (JAR ou ZIP), arquiva o SHA-256 e reinicia somente o componente correspondente. `FALHA_CONTROLADA=true` acrescenta um teste JUnit/pytest que falha nessa cópia. A falha aborta a execução antes dos estágios Build e Deploy. O arquivo `deployed-at.txt` só muda após health HTTP 200. Após saúde confirmada, o pacote e os metadados são preservados em `infra/.runtime/last-good/<componente>`, fora do workspace apagado no próximo teste; os experimentos devem restaurar por esse caminho. O helper valida a presença do pacote, commit e aprovação dos testes antes de parar o serviço. O commit de origem é registrado; os fontes do laboratório ainda não commitados devem ser identificados como árvore de trabalho modificada nas evidências.

Esta prova executa Jenkins e deploy nativo, pois não há engine Docker disponível. Ela não comprova build/deploy de imagens nem execução com PostgreSQL: essa etapa do plano original continua sendo uma limitação. `docker-compose.lab.yml` fornece alternativa com perfis `iot`, `observabilidade` e `ci`, ainda não executada neste ambiente. O agente do Jenkins em containers precisa de ferramentas e acesso explícito ao engine antes de executar pipelines de imagem.

Para parar apenas a infraestrutura: `.\scripts\b1\infra-stop.ps1`. Os processos dos três executáveis usam PIDs `infra/.runtime/core.pid`, `ia.pid` e `integracoes.pid`; o script `infra-deploy.ps1` valida saúde e reinicia cada componente. Os dados persistem em `infra/.runtime/` entre reinícios.
