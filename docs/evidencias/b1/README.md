# Evidências do Architecture Lab B1

A entrega reúne seis desafios, com decisões, diagramas, testes e experimentos locais. O [Word final](../../entrega/B1_Architecture_Lab_Final.docx) contém as respostas e 23 capturas diretas para os 18 itens de evidência.

## Capturas da entrega

O [índice das telas reais](telas-reais/README.md) relaciona as imagens, as ferramentas e os horários. Seu [manifesto](telas-reais/capturas.json) registra caminhos, dimensões e SHA-256.

| Desafio | Evidência | Registros de apoio |
| --- | --- | --- |
| 1 | Estrutura histórica, módulos atuais e ranking | [Resultados e dependências](desafio-01/README.md) |
| 2 | Política isolada, adapters, testes e cobertura | [Resultados Java e JaCoCo](desafio-02/README.md) |
| 3 | IA disponível, fallback e conclusão sem IA | [Execução estruturada](desafio-03/README.md) |
| 4 | Falha síncrona, outbox pendente e recuperação | [Execução estruturada](desafio-04/README.md) |
| 5 | MQTT, reconexão e retransmissão idempotente | [Execução estruturada](desafio-05/README.md) |
| 6 | Jenkins aprovado, bloqueio de deploy e métricas | [Pipelines e observabilidade](desafio-06/README.md) |

O print 1.1 mostra um arquivo de texto com o registro histórico da estrutura anterior. O 1.2 mostra a listagem atual dos diretórios. As demais capturas mostram Swagger, JaCoCo, Maven Surefire, Jenkins ou Grafana. Os sufixos a/b separam etapas do mesmo item.

## Fontes e datas

Os testes Java foram reexecutados em 04/11/2026: 80 aprovados e 100% de linhas, instruções e branches nas 38 classes medidas. A [pasta de fontes das capturas](telas-reais/fontes/) preserva logs, XMLs, payloads MQTT e o estado final consultado nas APIs.

Os logs e JSONs das pastas `desafio-01` a `desafio-06` registram as execuções originais. As contagens de 19 testes Python e de 7, 9 e 20 verificações E2E pertencem a essas execuções. Os três prints de Jenkins/Grafana mantêm suas datas originais.

Os 15 relatórios montados em imagem dos desafios 1 a 5 e seus HTMLs foram substituídos pelas capturas diretas. O arquivo `capturas.json` desta pasta conserva os hashes históricos e identifica as substituições; o manifesto da entrega atual é `telas-reais/capturas.json`.

Datas HTTP aparecem em GMT e timestamps do SQLite em UTC. As legendas das capturas usam o horário de São Paulo.

## Reprodução e interpretação

Consultar o [guia da infraestrutura](../../../infra/README.md) para preparar e iniciar os componentes. O Swagger do Core está em `http://127.0.0.1:8080/swagger-ui/index.html`; as integrações usam `http://127.0.0.1:8002/docs`.

Para repetir os ensaios, usar novos alunos, cursos e identificadores de evento. Comparar os mesmos IDs nas requisições e nos estados resultantes:

1. Consultar a IA ativa, interrompê-la e observar o fallback; concluir um curso enquanto ela está indisponível.
2. Interromper o receptor, verificar a falha síncrona e concluir um curso pelo Core. Observar a pendência e restaurar o receptor para conferir a entrega.
3. Publicar MQTT com o gateway indisponível, restaurá-lo e consultar o aluno. Reenviar o mesmo evento e verificar que bônus e histórico não duplicam.
4. Nos pipelines, comparar sucesso e falha controlada. Nas métricas, observar o intervalo completo de falha e recuperação.

Encerrar os componentes conforme as instruções da infraestrutura ao terminar. Os serviços iniciados para as capturas da entrega foram encerrados.

## Rastreabilidade e limites

O [registro arquitetural](../../arquitetura/README.md) liga requisitos, ASRs, restrições, alternativas, ADRs, C4 e evidências. A demonstração usa Windows nativo, H2 em arquivo, SQLite e dados sintéticos. Docker, PostgreSQL, nuvem, carga de 100 mil usuários e ML/RAG completo não foram comprovados.
