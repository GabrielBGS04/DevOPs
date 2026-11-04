"""Gera o registro arquitetural e os diagramas reproduzíveis do laboratório."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
DESAFIOS = [
    dict(n=1, titulo="Drivers e evolução do Core", rf="RF01 Ranking; RF02 Conquistas e funcionalidades da AC1.",
         rnfs="Manutenibilidade, desempenho, escalabilidade, testabilidade e complexidade operacional.",
         asrs=[("Manutenibilidade", "Agrupar curso e ranking por capacidade localiza alterações e explicita fronteiras."),
               ("Testabilidade", "Preservar contratos HTTP e testar o comportamento antes/depois permite reorganização incremental."),
               ("Complexidade operacional", "Manter um processo Core e banco relacional evita infraestrutura distribuída sem evidência de necessidade.")],
         rpc="Core Java/Spring Boot, legado AC1, banco relacional e equipe de seis desenvolvedores no cenário. A equipe real identificada no repositório tem Gabriel Baldi e Higor Aranda.",
         alternativas=[("Monólito em camadas", "Mudança inicial pequena; capacidades permanecem espalhadas por pastas técnicas."),
                       ("Monólito modular", "Maior coesão e fronteiras explícitas; exige disciplina de dependências e ainda escala o Core inteiro."),
                       ("Serviço seletivo de ranking", "Permite deploy/escala independentes; acrescenta rede, sincronização de dados e operação sem demanda medida neste experimento.")],
         decisao="Modularizar incrementalmente curso e ranking dentro do Core. Ranking lê alunos pela API pública do serviço, sem importar seu repositório. Preservar contratos de cursos e alunos.",
         consequencias="Não há escala independente dos módulos. Ranking usa 100 pontos por entrada distinta no histórico e desempate por ID; não foram introduzidas moedas. Consulta atual é didática e não certifica desempenho para 100 mil usuários.",
         evidencia="Snapshot original, árvore reorganizada, imports antes/depois, consulta ao ranking e regressão automatizada.",
         c4="core", prints=["01-camadas-antes","02-modulos-depois","03-ranking-funcionando"]),
    dict(n=2, titulo="Organização interna do Core", rf="RF02 Conquistas e recompensa por conclusão; RF01 Ranking como leitura do resultado.",
         rnfs="Manutenibilidade, testabilidade, modificabilidade e facilidade de evolução.",
         asrs=[("Testabilidade", "A política de bônus deve rodar sem contexto Spring nem acesso ao banco."),
               ("Modificabilidade", "O caso de conclusão depende de uma porta de dados com adapters substituíveis."),
               ("Manutenibilidade", "Uma única política concentra o limite de nota e a quantidade de bônus.")],
         rpc="Core permanece Spring Boot, regras existentes reaproveitadas e refatoração localizada. Básico com nota ≥ 8,5 recebe três cursos; Premium não recebe esse bônus.",
         alternativas=[("Estrutura atual", "Simples e já testada; acesso JPA e orquestração ficam juntos no serviço."),
                       ("Ports & Adapters localizado", "Caso de uso e regra testáveis com memória/JPA; acrescenta uma porta e adapter, sem reescrever todas as entidades.")],
         decisao="Extrair PoliticaBonus em Java puro e ConclusaoDeCurso dependente de ConclusaoPort. Usar JpaConclusaoAdapter no Core e adapter em memória nos testes.",
         consequencias="As entidades legadas ainda possuem anotações JPA; a proteção é aplicada à política e ao caso de uso selecionados. DDD organiza os conceitos; Hexagonal organiza dependências. Clean/Onion podem compartilhar esse princípio, mas não exigem quatro estruturas simultâneas.",
         evidencia="Teste puro da política, contrato de conclusão em memória e integração JPA/H2, limites de nota e relatório de cobertura.",
         c4="component", prints=["01-regra-isolada","02-adapters-testados","03-regressao-cobertura"]),
    dict(n=3, titulo="Serviço Python e IA", rf="RF03 Recomendação inteligente; RF04 Assistente educacional, em microsolução demonstrativa.",
         rnfs="Deploy independente, escalabilidade, tolerância a falhas, interoperabilidade, desempenho e manutenibilidade.",
         asrs=[("Tolerância a falhas", "Timeout e resposta degradada impedem que a IA indisponível bloqueie o Core."),
               ("Deploy independente", "Processo Python próprio permite atualizar a implementação sem reiniciar o Java."),
               ("Interoperabilidade", "Contrato HTTP/JSON mantém a fronteira entre Java e Python explícita.")],
         rpc="Core Java/Spring Boot, IA em Python, fluxo essencial disponível sem IA. Usuário escolheu laboratório local sem provedor pago.",
         alternativas=[("IA embutida no Core", "Menos processos; ciclo de modelos e execução ficam acoplados ao Java."),
                       ("Módulo acoplado", "Localiza a capacidade, mas não oferece isolamento de processo ou deploy."),
                       ("FastAPI independente", "Fronteira e deploy próprios; exige contratos, timeout e tratamento de indisponibilidade.")],
         decisao="Um FastAPI atende recomendação e assistente demonstrativos. O Core chama por HTTP com timeout de dois segundos e sem retentativa na thread do usuário. Falha retorna HTTP 200 com disponivel=false e fallback explícito.",
         consequencias="Python sozinho não prova necessidade de serviço; autonomia de ciclo e isolamento de falha justificam a fronteira aqui testada. ML/RAG compartilham o executável enquanto não há evidência de cargas/ciclos distintos. A recomendação é determinística e o assistente faz busca textual em material local, sem treinamento de ML ou RAG/LLM completo.",
         evidencia="Requisições com IA ativa, IA parada e conclusão de curso mantendo recompensa e histórico.",
         c4="ai", prints=["01-ia-disponivel","02-ia-indisponivel","03-core-sem-ia"]),
    dict(n=4, titulo="Comunicação e eventos", rf="RF02 Conquistas; RF05 Notificações após conclusão.",
         rnfs="Tolerância a falhas, disponibilidade, latência, consistência, desacoplamento e recuperabilidade.",
         asrs=[("Tolerância a falhas", "Falha do receptor não deve impedir confirmar conclusão e bônus."),
               ("Consistência", "Estado essencial e evento pendente são gravados na mesma transação; notificação é eventual."),
               ("Recuperabilidade", "Eventos pendentes e identificadores estáveis permitem retentar após indisponibilidade.")],
         rpc="Core precisa concluir com consumidor externo indisponível; broker dedicado implica custo operacional. Processamento único de outbox no laboratório.",
         alternativas=[("REST síncrono", "Resposta imediata do receptor; falha e latência propagam-se à chamada dependente."),
                       ("Outbox e worker HTTP", "Usa o banco relacional existente e entrega eventual; exige polling, retentativa e deduplicação."),
                       ("RabbitMQ ou Kafka", "RabbitMQ agrega filas/roteamento e acknowledgements; Kafka agrega log/replay e grupos. Ambos exigem operação adicional sem necessidade de throughput ou replay demonstrada neste caso.")],
         decisao="Conclusão e outbox na mesma transação. Worker HTTP a cada cinco segundos, timeout de dois segundos e retentativa com o mesmo eventId. Receptor Python persiste deduplicação em SQLite.",
         consequencias="Entrega pelo menos uma vez, com deduplicação no receptor; não há exatamente uma vez distribuído. Confirmação da notificação é eventual. Polling acrescenta latência e o dispatcher do laboratório é de instância única. Dados relacionais do laboratório ficam em H2 arquivo; configuração PostgreSQL permanece para Compose.",
         evidencia="Falha síncrona provocada, conclusão HTTP 200 com evento pendente, recuperação e entrega do mesmo identificador.",
         c4="sequence", prints=["01-sincrono-falha","02-assincrono-pendente","03-recuperacao"]),
    dict(n=5, titulo="IoT e MQTT", rf="RF06 Receber presença, início e conclusão de atividade por dispositivo simulado.",
         rnfs="Interoperabilidade, eficiência, disponibilidade, tolerância à conexão intermitente, escalabilidade e segurança de integração.",
         asrs=[("Interoperabilidade", "Gateway traduz o evento do dispositivo para contrato HTTP do Core."),
               ("Eficiência de comunicação", "MQTT pub/sub evita acoplamento HTTP de cada dispositivo ao Core."),
               ("Tolerância à conexão intermitente", "Sessão persistente, QoS 1 e inbox idempotente permitem reconexão e retransmissão.")],
         rpc="Dispositivo pode ter poucos recursos e conexão instável; broker e gateway acrescentam operação. Laboratório usa dados sintéticos e conexões restritas ao loopback.",
         alternativas=[("REST direto", "Menos componentes; cada dispositivo precisa conhecer a integração e suas falhas HTTP."),
                       ("MQTT com gateway", "Sessões e pub/sub adequados ao cenário; exige broker, política de entrega e deduplicação."),
                       ("MQTT e broker interno adicional", "Útil para múltiplos consumidores e replay conforme ASRs; neste laboratório duplicaria infraestrutura sem necessidade comprovada.")],
         decisao="Mosquitto com persistência e QoS 1 no tópico b1/atividades. Gateway Python mantém spool SQLite e confirma MQTT depois da aceitação HTTP. Core grava eventId e efeito de negócio atomicamente; retransmissão retorna sucesso sem repetir bônus.",
         consequencias="QoS 1 admite duplicatas e não substitui idempotência. O experimento prova a janela de desconexão/reconexão executada, não ausência absoluta de perdas em qualquer falha de disco. O gateway compartilha executável de integrações para reduzir operação, com responsabilidades separadas no código.",
         evidencia="Publicação/recepção com mesmo ID, publicação com gateway offline, reconexão e retransmissão sem nova recompensa.",
         c4="iot", prints=["01-mqtt-publicacao-recepcao","02-reconexao","03-evento-sem-duplicacao"]),
    dict(n=6, titulo="CI CD e observabilidade", rf="RF01 a RF06: construção, implantação e observação dos componentes executados.",
         rnfs="Observabilidade, deploy independente, confiabilidade, testabilidade, recuperabilidade e desempenho.",
         asrs=[("Testabilidade", "Pipeline executa testes e a política de cobertura antes de disponibilizar artefato."),
               ("Observabilidade", "Métricas e logs mostram efeito da falha e da recuperação sobre os fluxos essenciais."),
               ("Deploy independente", "Jobs por executável atualizam somente Core, IA ou integrações.")],
         rpc="Jenkins é a esteira; Prometheus/Grafana são obrigatórios; configurações e evidências versionadas. Ambiente sem engine Docker disponível.",
         alternativas=[("Pipeline único", "Visão centralizada e configuração inicial menor; mudanças independentes ficam acopladas à mesma execução."),
                       ("Pipeline por executável", "Validação e deploy independentes; duplica parte da configuração e requer contratos entre componentes.")],
         decisao="Três pipelines Jenkins com teste, build e deploy nativo local. Falha em teste impede build/deploy. Prometheus coleta o Core a cada cinco segundos; Grafana exibe falhas da IA, pendências de notificação e métricas HTTP.",
         consequencias="A prova foi desenhada para processos Windows portáveis, com JAR/ZIP e health check. Dockerfiles/Compose são alternativa fornecida, sem alegar execução de containers. O laboratório usa H2 relacional em arquivo; não comprova operação PostgreSQL nem escala. Métrica técnica vira evidência arquitetural quando a parada/recuperação mostra preservação do Core e drenagem da outbox.",
         evidencia="Builds reais de três jobs, teste falho controlado bloqueando deploy, dashboard durante falha/recuperação e consultas Prometheus.",
         c4="deployment", prints=["01-jenkins-sucesso","02-jenkins-bloqueio","03-grafana-falha-recuperacao"]),
]

MERMAID = {
"core": '''flowchart LR
 U[Aluno e equipe] -->|HTTP JSON| C[Core Spring Boot\nCurso Ranking Aluno Gamificação]
 C -->|JPA| DB[(Banco relacional)]
''',
"ai": '''flowchart LR
 U[Aluno] -->|HTTP JSON| C[Core Spring Boot :8080]
 C -->|JPA| DB[(Banco relacional)]
 C -->|HTTP JSON timeout2s| IA[IA FastAPI :8001\nRecomendação e assistente demonstrativos]
 IA -. indisponibilidade .-> F[Core retorna fallback explícito]
''',
"container": '''flowchart LR
 U[Aluno e equipe] -->|HTTP JSON| C[Core Spring Boot :8080]
 C -->|JPA| DB[(Banco relacional\nH2 arquivo no lab\nPostgreSQL no Compose)]
 C -->|HTTP JSON timeout 2s| IA[IA FastAPI :8001]
 C -->|Outbox worker HTTP| IN[Integrações FastAPI :8002]
 IN --> S[(SQLite dedup e spool)]
 D[Dispositivo simulado] -->|MQTT QoS1| M[Mosquitto :1883]
 M -->|MQTT sessão persistente| IN
 IN -->|HTTP evento idempotente| C
''',
"component": '''flowchart LR
 API[AlunoController] --> AS[AlunoService\nfronteira transacional]
 AS --> UC[ConclusaoDeCurso]
 UC --> PORT[ConclusaoPort]
 UC --> AL[Aluno]
 AL --> R[PoliticaBonus\nJava puro]
 JPA[JpaConclusaoAdapter] -. implementa .-> PORT
 MEM[Adapter memória em teste] -. implementa .-> PORT
 JPA --> REP[Repositories JPA]
 AS --> OUT[NotificacaoOutbox]
 OUT --> DB[(Banco relacional)]
 REP --> DB
 RANK[Ranking] -->|API pública| AS
''',
"sequence": '''sequenceDiagram
 participant U as Cliente
 participant C as Core
 participant D as Banco relacional
 participant W as Worker outbox
 participant N as Receptor Python
 U->>C: concluir curso
 C->>D: BEGIN conclusão + bônus + evento
 D-->>C: COMMIT
 C-->>U: HTTP 200
 W->>D: consultar eventos pendentes
 W->>N: POST eventId
 alt indisponível
 N--xW: falha/timeout
 Note over W,D: manter pendente e retentar
 else disponível
 N-->>W: confirmado/deduplicado
 W->>D: marcar entregue
 end
''',
"iot": '''flowchart LR
 DEV[Simulador\neventId tipo aluno curso nota] -->|MQTT QoS1| M[Mosquitto\nsessão persistente]
 M --> G[Gateway Python]
 G --> S[(Spool SQLite)]
 G -->|POST evento| CORE[Core\ninbox e caso de conclusão]
 CORE -->|mesma transação| DB[(Inbox histórico bônus outbox)]
 CORE -->|2xx| G
 G -->|ACK após aceitação| M
''',
"deployment": '''flowchart TB
 subgraph WIN[Máquina Windows local — loopback]
 J[Jenkins :8081\n3 pipelines]
 C[Core JVM :8080]
 IA[Python IA :8001]
 IN[Python integrações :8002]
 M[Mosquitto :1883]
 P[Prometheus :9090]
 G[Grafana :3000]
 J -->|JAR health| C
 J -->|ZIP health| IA
 J -->|ZIP health| IN
 C --> IA
 C --> IN
 M --> IN
 IN --> C
 P -->|scrape 5s| C
 G -->|PromQL| P
 end
'''
}

def generate():
    architecture = ROOT/'docs/arquitetura'
    adrdir = ROOT/'docs/adr'
    diagrams = architecture/'diagramas'
    diagrams.mkdir(parents=True, exist_ok=True)
    adrdir.mkdir(parents=True, exist_ok=True)
    for name, source in MERMAID.items():
        (diagrams/f'{name}.mmd').write_text(source, encoding='utf-8')
    matrix = []
    for d in DESAFIOS:
        adrname = f"ADR-{d['n']:03d}"
        evidence = f"../evidencias/b1/desafio-{d['n']:02d}/README.md"
        body = [f"# {adrname} — {d['titulo']}", "", "Estado: decisão implementada; resultados e limites vinculados nas evidências de execução.",
                "", "## Contexto e requisitos", "",d['rf'],"", d['rnfs'],"", "## ASRs prioritários", ""]
        for i,(name,impact) in enumerate(d['asrs'],1):
            body.append(f"{i}. **{name}:** {impact}")
            matrix.append(f"| D{d['n']}-ASR{i} | {d['n']} | {name} | {impact} | [{adrname}](../adr/{adrname}.md) |")
        body += ["", "## Restrições e premissas", "",d['rpc'],"", "## Alternativas e trade offs", ""]
        for name,tradeoff in d['alternativas']:
            body.append(f"- **{name}:** {tradeoff}")
        body += ["", "## Decisão", "",d['decisao'],"", "## Consequências e limites", "", d['consequencias'],
                 "", "## C4 e evidência", "", f"[Diagrama fonte](../arquitetura/diagramas/{d['c4']}.mmd)","",
                 "```mermaid",MERMAID[d['c4']].rstrip(),"```","",d['evidencia'],"",f"[Resultados de execução]({evidence})",""]
        (adrdir/f'{adrname}.md').write_text('\n'.join(body), encoding='utf-8')
    text = ["# Registro arquitetural do B1", "", "Equipe: Gabriel Baldi e Higor Aranda, conforme identificação existente no README da AC1.", "",
            "Repositório: https://github.com/GabrielBGS04/DevOPs", "", "Base confirmada: bdb6943. Implementação na branch local codex/b1-architecture-lab; resultados sem novo commit são identificados como árvore de trabalho modificada.",
            "", "## Objetivo e execução", "", "Os seis desafios evoluem o mesmo MVP. Cada ADR relaciona RF/RNF, até três ASRs, restrições, alternativas, decisão, C4 e evidência. O laboratório usa dados sintéticos e processos nativos locais; os limites de IA, escala, Docker e PostgreSQL estão explícitos nas decisões.",
            "", "## Requisitos e FURPS", "", "RF01 ranking; RF02 conquistas/recompensa; RF03 recomendação; RF04 assistente; RF05 notificação; RF06 IoT. A regra existente concede três cursos ao plano básico com nota mínima de 8,5.", "",
            "RNFs: confiabilidade/tolerância e recuperabilidade (R); desempenho/latência/throughput (P); suporte, manutenibilidade, testabilidade e observabilidade (S); protocolos e implantação nas restrições adicionais (+). Os ASRs abaixo são um subconjunto dos RNFs analisados em cada desafio.",
            "", "## Matriz cumulativa de ASRs", "", "| Identificador | Desafio | Qualidade | Impacto arquitetural | Decisão |", "| --- | --- | --- | --- | --- |", *matrix,
            "", "## Decisões e evidências", ""]
    for d in DESAFIOS:
        n=d['n']
        text.append(f"- Desafio {n}: [{d['titulo']}](../adr/ADR-{n:03d}.md) — [evidências](../evidencias/b1/desafio-{n:02d}/README.md).")
    text += ["", "## C4 final Container", "", "```mermaid", MERMAID['container'].rstrip(),"```", "", "## C4 final Deployment", "", "```mermaid", MERMAID['deployment'].rstrip(),"```",
             "", "## Síntese para a Avaliação Final", "", "Levar para a PoC: módulos incrementais no Core, política de bônus pura, porta de persistência, isolamento HTTP da IA com fallback, outbox transacional, inbox idempotente e métricas ligadas aos experimentos. Manter um único serviço demonstrativo de IA enquanto não houver evidência para separar ML/RAG.", "",
             "Aprofundar antes de produção: carga real e consulta paginada do ranking; modelo/recuperação RAG reais; autenticação e integração por instituição; operação PostgreSQL e containers; retenção/limpeza da outbox e políticas de retry; múltiplos workers; segurança MQTT fora do loopback; backup e continuidade. O cenário de 100 mil usuários não foi certificado pelos pequenos experimentos.",
             "", "## Reprodução", "", "Consultar [infraestrutura](../../infra/README.md), [roteiro de comprovação](../evidencias/b1/README.md) e os comandos registrados nos resultados dos desafios. O documento Word de entrega será disponibilizado em docs/entrega/.",""]
    (architecture/'README.md').write_text('\n'.join(text), encoding='utf-8')
    (architecture/'desafios.json').write_text(json.dumps(DESAFIOS,ensure_ascii=False,indent=2), encoding='utf-8')

if __name__ == '__main__':
    generate()
