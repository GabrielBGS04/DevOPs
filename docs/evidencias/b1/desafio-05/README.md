# Evidências do Desafio 5 — IoT e MQTT

**Estado:** IMPLEMENTADO, EXPERIMENTO EXECUTADO E CAPTURAS SALVAS.

## Hipótese arquitetural

Publicação/recepção com mesmo ID, publicação com gateway offline, reconexão e retransmissão sem nova recompensa.

## Execução observada

Execução `20261104-082328-241e66`: 2026-11-04T08:23:55.622-03:00 a 2026-11-04T08:24:32.660-03:00. [Respostas e comandos integrais](execucao.json).

20 verificações aprovadas. QoS1 e gateway ativo entregaram evento normal. Publicação com gateway parado não alterou o Core; após reconexão da sessão persistente, o evento foi entregue e concedeu bônus3. Retransmissão MQTT e repetição direta no Core preservaram uma conclusão e bônus3. Com Core parado, outro evento ficou PENDENTE após tentativa HTTP; gateway também foi parado e reiniciado, recuperou o spool e entregou uma vez após retorno do Core. Demonstra cenário local; não injeta queda na janela exata após commit do Core e antes do PUBACK.

Base Git: `bdb6943`, branch local `codex/b1-architecture-lab`, com alterações B1 no momento da execução. Os JSONs dos experimentos e os artefatos do Jenkins registram hashes dos fontes para identificar a implementação efetivamente testada.

## Capturas diretas atualizadas

As telas atuais estão reunidas na pasta `telas-reais`. Os logs e JSONs desta pasta preservam a execução original.

| Item | Tela | Ferramenta |
| --- | --- | --- |
| 5.1 | [Evento MQTT entregue](../telas-reais/D5-1-evento-mqtt-entregue.jpg) | Swagger das integrações |
| 5.2a | [Gateway desconectado](../telas-reais/D5-2a-antes-reconexao.jpg) | Swagger do Core |
| 5.2b | [Após reconexão](../telas-reais/D5-2b-depois-reconexao.jpg) | Swagger do Core |
| 5.3a | [Mesmo evento aceito](../telas-reais/D5-3a-evento-repetido-aceito.jpg) | Swagger do Core |
| 5.3b | [Sem recompensa duplicada](../telas-reais/D5-3b-sem-bonus-duplicado.jpg) | Swagger do Core |

[Manifesto com datas e hashes](../telas-reais/capturas.json).

## Fontes e reprodução

[Execução estruturada](execucao.json) e logs dos comandos em `comandos/`.

[Guia de captura e reprodução](../README.md)

[ADR-005](../../../adr/ADR-005.md) · [C4 fonte](../../../arquitetura/diagramas/iot.mmd)

## Limites

QoS 1 admite duplicatas e não substitui idempotência. O experimento prova a janela de desconexão/reconexão executada, não ausência absoluta de perdas em qualquer falha de disco. O gateway compartilha executável de integrações para reduzir operação, com responsabilidades separadas no código.

Os relatórios visuais antigos foram substituídos por capturas diretas das ferramentas. O print 1.1 exibe o registro histórico da estrutura; o 1.2 mostra a listagem atual dos diretórios. Os dados originais de execução permanecem preservados.
