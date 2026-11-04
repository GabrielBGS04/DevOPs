# Capturas diretas das ferramentas — B1

As imagens desta pasta e as três capturas preservadas do desafio 6 compõem **23 capturas para os 18 itens de evidência**. Os sufixos a/b separam etapas ou resultados do mesmo item.

Os prints foram obtidos diretamente no navegador: Swagger, JaCoCo, Maven Surefire e listagens de arquivos. Não foram recriadas interfaces de terminal, editor ou ferramenta. O print 1.1 mostra o registro histórico da estrutura; o 1.2 mostra o diretório atual servido localmente. As legendas identificam essa diferença.

As contagens de 7, 9 e 20 checks E2E pertencem às execuções automatizadas originais. Nesta rodada foram reexecutados os testes Java e os cenários manuais de IA, notificações e MQTT. Os três prints do Jenkins/Grafana conservam suas datas originais.

## Índice

| Item | Tela | Ferramenta | Captura em São Paulo |
| --- | --- | --- | --- |
| 1.1 | [Estrutura anterior](D1-1-registro-estrutura-anterior.jpg) | Navegador — arquivo de texto | 04/11/2026 15:47 |
| 1.2 | [Módulos atuais](D1-2-diretorios-reais.jpg) | Navegador — listagem de diretório | 04/11/2026 15:48 |
| 1.3 | [Ranking em execução](D1-3-ranking-swagger.jpg) | Swagger do Core | 04/11/2026 11:07 |
| 2.1 | [Política de bônus isolada](D2-1-politica-jacoco.jpg) | JaCoCo | 04/11/2026 15:49 |
| 2.2 | [Testes dos adapters](D2-2-testes-adapters-surefire.jpg) | Maven Surefire | 04/11/2026 15:50 |
| 2.3a | [Regressão Java](D2-3a-resumo-surefire.jpg) | Maven Surefire | 04/11/2026 15:50 |
| 2.3b | [Cobertura do Core](D2-3-cobertura-jacoco.jpg) | JaCoCo | 04/11/2026 15:49 |
| 3.1 | [IA disponível](D3-1-ia-disponivel-swagger.jpg) | Swagger do Core | 04/11/2026 11:10 |
| 3.2 | [Fallback da IA](D3-2-ia-indisponivel-swagger.jpg) | Swagger do Core | 04/11/2026 11:11 |
| 3.3 | [Conclusão sem IA](D3-3-conclusao-sem-ia-swagger.jpg) | Swagger do Core | 04/11/2026 11:12 |
| 4.1 | [Falha da chamada síncrona](D4-1-notificacao-sincrona-falha.jpg) | Swagger das integrações | 04/11/2026 15:37 |
| 4.2a | [Conclusão confirmada](D4-2a-conclusao-confirmada.jpg) | Swagger do Core | 04/11/2026 15:37 |
| 4.2b | [Evento pendente](D4-2b-outbox-pendente.jpg) | Swagger do Core | 04/11/2026 15:37 |
| 4.3a | [Outbox após recuperação](D4-3a-outbox-recuperada.jpg) | Swagger do Core | 04/11/2026 15:39 |
| 4.3b | [Notificação recebida](D4-3b-notificacao-recebida.jpg) | Swagger das integrações | 04/11/2026 15:40 |
| 5.1 | [Evento MQTT entregue](D5-1-evento-mqtt-entregue.jpg) | Swagger das integrações | 04/11/2026 15:42 |
| 5.2a | [Gateway desconectado](D5-2a-antes-reconexao.jpg) | Swagger do Core | 04/11/2026 15:42 |
| 5.2b | [Após reconexão](D5-2b-depois-reconexao.jpg) | Swagger do Core | 04/11/2026 15:44 |
| 5.3a | [Mesmo evento aceito](D5-3a-evento-repetido-aceito.jpg) | Swagger do Core | 04/11/2026 15:46 |
| 5.3b | [Sem recompensa duplicada](D5-3b-sem-bonus-duplicado.jpg) | Swagger do Core | 04/11/2026 15:46 |
| 6.1 | [Pipeline aprovado](../desafio-06/01-jenkins-sucesso.jpg) | Jenkins | 03/11/2026 20:12 |
| 6.2 | [Teste falho bloqueia o deploy](../desafio-06/02-jenkins-bloqueio.jpg) | Jenkins | 03/11/2026 20:12 |
| 6.3 | [Falha e recuperação nas métricas](../desafio-06/03-grafana-falha-recuperacao.jpg) | Grafana | 04/11/2026 08:28 |

## Fontes e verificação

- [Manifesto com arquivos, datas, dimensões e SHA-256](capturas.json).
- [Estado final consultado nas APIs](fontes/estado-final.json): alunos 65 a 68 com três cursos de bônus e uma conclusão; outbox zerada.
- [Verificação Maven](fontes/maven-verify.log), [geração do relatório Surefire](fontes/surefire-report.log) e [cobertura XML](fontes/jacoco.xml).
- [Publicação MQTT normal](fontes/mqtt-normal.log), [publicação offline](fontes/mqtt-offline.log), [retransmissão](fontes/mqtt-retransmissao.log), [payload normal](fontes/mqtt-normal.json) e [payload offline](fontes/mqtt-offline.json).
- Os arquivos `TEST-*.xml` da pasta `fontes` registram os resultados individuais dos testes Java.

Datas HTTP aparecem em GMT e timestamps do SQLite em UTC; o manifesto informa o horário de São Paulo. As capturas são momentos dos experimentos, e não indicam que os serviços devam permanecer ligados. Os processos temporários desta rodada foram encerrados e suas portas liberadas.

O documento de entrega está em [B1 Architecture Lab final](../../../entrega/B1_Architecture_Lab_Final.docx).
