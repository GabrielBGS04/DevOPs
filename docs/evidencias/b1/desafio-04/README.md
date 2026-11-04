# Evidências do Desafio 4 — Comunicação e eventos

**Estado:** IMPLEMENTADO, EXPERIMENTO EXECUTADO E CAPTURAS SALVAS.

## Hipótese arquitetural

Falha síncrona provocada, conclusão HTTP 200 com evento pendente, recuperação e entrega do mesmo identificador.

## Execução observada

Execução `20261104-082328-241e66`: 2026-11-04T08:23:33.360-03:00 a 2026-11-04T08:23:55.582-03:00. [Respostas e comandos integrais](execucao.json).

9 verificações aprovadas. Com receptor parado, tentativa síncrona falhou, mas conclusão/bônus3 foram confirmados e uma pendência permaneceu por10s com retentativas do mesmo eventId. Após restauração, o mesmo identificador foi recebido uma vez, outbox esvaziou e repetição foi deduplicada. Não comprova atomicidade distribuída ou envio real de mensagem.

Base Git: `bdb6943`, branch local `codex/b1-architecture-lab`, com alterações B1 no momento da execução. Os JSONs dos experimentos e os artefatos do Jenkins registram hashes dos fontes para identificar a implementação efetivamente testada.

## Capturas diretas atualizadas

As telas atuais estão reunidas na pasta `telas-reais`. Os logs e JSONs desta pasta preservam a execução original.

| Item | Tela | Ferramenta |
| --- | --- | --- |
| 4.1 | [Falha da chamada síncrona](../telas-reais/D4-1-notificacao-sincrona-falha.jpg) | Swagger das integrações |
| 4.2a | [Conclusão confirmada](../telas-reais/D4-2a-conclusao-confirmada.jpg) | Swagger do Core |
| 4.2b | [Evento pendente](../telas-reais/D4-2b-outbox-pendente.jpg) | Swagger do Core |
| 4.3a | [Outbox após recuperação](../telas-reais/D4-3a-outbox-recuperada.jpg) | Swagger do Core |
| 4.3b | [Notificação recebida](../telas-reais/D4-3b-notificacao-recebida.jpg) | Swagger das integrações |

[Manifesto com datas e hashes](../telas-reais/capturas.json).

## Fontes e reprodução

[Execução estruturada](execucao.json) e logs dos comandos em `comandos/`.

[Guia de captura e reprodução](../README.md)

[ADR-004](../../../adr/ADR-004.md) · [C4 fonte](../../../arquitetura/diagramas/sequence.mmd)

## Limites

Entrega pelo menos uma vez, com deduplicação no receptor; não há exatamente uma vez distribuído. Confirmação da notificação é eventual. Polling acrescenta latência e o dispatcher do laboratório é de instância única. Dados relacionais do laboratório ficam em H2 arquivo; configuração PostgreSQL permanece para Compose.

Os relatórios visuais antigos foram substituídos por capturas diretas das ferramentas. O print 1.1 exibe o registro histórico da estrutura; o 1.2 mostra a listagem atual dos diretórios. Os dados originais de execução permanecem preservados.
