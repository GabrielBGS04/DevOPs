# Evidências do Desafio 1 — Drivers e evolução do Core

**Estado:** IMPLEMENTADO, EXPERIMENTO EXECUTADO E CAPTURAS SALVAS.

## Hipótese arquitetural

Snapshot original, árvore reorganizada, imports antes/depois, consulta ao ranking e regressão automatizada.

## Execução observada

Baseline executado em 03/11/2026: 45 testes aprovados. Verificação final da implementação: 80 testes e cobertura de 100% por classe; ranking consultado após os experimentos de 04/11/2026.

Snapshot em camadas preservado; curso e ranking agrupados por capacidade; ranking HTTP 200 com pontuação e ordem verificadas; regressão sem falhas.

Base Git: `bdb6943`, branch local `codex/b1-architecture-lab`, com alterações B1 no momento da execução. Os JSONs dos experimentos e os artefatos do Jenkins registram hashes dos fontes para identificar a implementação efetivamente testada.

## Capturas diretas atualizadas

As telas atuais estão reunidas na pasta `telas-reais`. Os logs e JSONs desta pasta preservam a execução original.

| Item | Tela | Ferramenta |
| --- | --- | --- |
| 1.1 | [Registro histórico da estrutura anterior](../telas-reais/D1-1-registro-estrutura-anterior.jpg) | Navegador — arquivo de texto |
| 1.2 | [Módulos atuais](../telas-reais/D1-2-diretorios-reais.jpg) | Navegador — listagem de diretório |
| 1.3 | [Ranking em execução](../telas-reais/D1-3-ranking-swagger.jpg) | Swagger do Core |

[Manifesto com datas e hashes](../telas-reais/capturas.json).

## Fontes e reprodução

[Baseline](baseline-testes.log), [RED](red-b1.log), [imports antes](antes-dependencias.txt), [imports depois](depois-dependencias.txt), [resposta real do ranking](ranking.json), [verificação final](../desafio-02/verify-final.log).

[Guia de captura e reprodução](../README.md)

[ADR-001](../../../adr/ADR-001.md) · [C4 fonte](../../../arquitetura/diagramas/core.mmd)

## Limites

Não há escala independente dos módulos. Ranking usa 100 pontos por entrada distinta no histórico e desempate por ID; não foram introduzidas moedas. Consulta atual é didática e não certifica desempenho para 100 mil usuários.

Os relatórios visuais antigos foram substituídos por capturas diretas das ferramentas. O print 1.1 exibe o registro histórico da estrutura; o 1.2 mostra a listagem atual dos diretórios. Os dados originais de execução permanecem preservados.
