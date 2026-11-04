# Evidências do Desafio 3 — Serviço Python e IA

**Estado:** IMPLEMENTADO, EXPERIMENTO EXECUTADO E CAPTURAS SALVAS.

## Hipótese arquitetural

Requisições com IA ativa, IA parada e conclusão de curso mantendo recompensa e histórico.

## Execução observada

Execução `20261104-082328-241e66`: 2026-11-04T08:23:28.221-03:00 a 2026-11-04T08:23:33.316-03:00. [Respostas e comandos integrais](execucao.json).

7 verificações aprovadas. IA ativa respondeu recomendação e conteúdo local; IA parada produziu HTTP200 degradado e o Core confirmou conclusão com bônus3. Tempos medidos constam nos passos; não se trata de modelo ML ou teste de timeout lento.

Base Git: `bdb6943`, branch local `codex/b1-architecture-lab`, com alterações B1 no momento da execução. Os JSONs dos experimentos e os artefatos do Jenkins registram hashes dos fontes para identificar a implementação efetivamente testada.

## Capturas diretas atualizadas

As telas atuais estão reunidas na pasta `telas-reais`. Os logs e JSONs desta pasta preservam a execução original.

| Item | Tela | Ferramenta |
| --- | --- | --- |
| 3.1 | [IA disponível](../telas-reais/D3-1-ia-disponivel-swagger.jpg) | Swagger do Core |
| 3.2 | [Fallback da IA](../telas-reais/D3-2-ia-indisponivel-swagger.jpg) | Swagger do Core |
| 3.3 | [Conclusão sem IA](../telas-reais/D3-3-conclusao-sem-ia-swagger.jpg) | Swagger do Core |

[Manifesto com datas e hashes](../telas-reais/capturas.json).

## Fontes e reprodução

[Execução estruturada](execucao.json) e logs dos comandos em `comandos/`.

[Guia de captura e reprodução](../README.md)

[ADR-003](../../../adr/ADR-003.md) · [C4 fonte](../../../arquitetura/diagramas/ai.mmd)

## Limites

Python sozinho não prova necessidade de serviço; autonomia de ciclo e isolamento de falha justificam a fronteira aqui testada. ML/RAG compartilham o executável enquanto não há evidência de cargas/ciclos distintos. A recomendação é determinística e o assistente faz busca textual em material local, sem treinamento de ML ou RAG/LLM completo.

Os relatórios visuais antigos foram substituídos por capturas diretas das ferramentas. O print 1.1 exibe o registro histórico da estrutura; o 1.2 mostra a listagem atual dos diretórios. Os dados originais de execução permanecem preservados.
