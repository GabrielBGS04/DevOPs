# Entrega do Architecture Lab B1

**[Documento final em Word](B1_Architecture_Lab_Final.docx)** — 27 páginas, com os seis desafios, as 12 partes do modelo em cada desafio, seis diagramas e 23 capturas diretas para os 18 itens de evidência. As respostas foram resumidas e os prints aparecem junto do desafio correspondente.

Equipe: Gabriel Baldi e Higor Aranda.

As telas mostram Swagger, JaCoCo, Maven Surefire, arquivos do projeto, Jenkins e Grafana. O print 1.1 exibe um registro histórico da estrutura anterior; o 1.2 mostra a listagem atual dos diretórios. Os três prints do Jenkins/Grafana mantêm as datas originais. O [índice das capturas](../evidencias/b1/telas-reais/README.md) relaciona arquivos, cenários, fontes e hashes.

Nesta rodada, `clean verify` aprovou os 80 testes Java. Os cenários manuais de IA, outbox e MQTT foram executados para as novas capturas. As contagens de 19 testes Python e 36 verificações E2E pertencem à execução automatizada original.

A execução comprovada usa Windows nativo, H2 em arquivo e SQLite. Docker, PostgreSQL e nuvem não foram executados. A IA é uma demonstração determinística com busca textual local. Todos os serviços temporários iniciados para as capturas foram encerrados.

## Materiais de apoio

- [Registro arquitetural](../arquitetura/README.md), [ADRs](../adr/) e [evidências por desafio](../evidencias/b1/README.md).
- [Índice das capturas diretas](../evidencias/b1/telas-reais/README.md), com os arquivos brutos de apoio.

Esta pasta contém apenas a versão final em Word e este índice. O enunciado e o exemplo recebidos em Downloads foram preservados.
