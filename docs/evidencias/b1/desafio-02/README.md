# Evidências do Desafio 2 — Organização interna do Core

**Estado:** IMPLEMENTADO, EXPERIMENTO EXECUTADO E CAPTURAS SALVAS.

## Hipótese arquitetural

Teste puro da política, contrato de conclusão em memória e integração JPA/H2, limites de nota e relatório de cobertura.

## Execução observada

Verificação `mvnw.cmd clean verify` concluída em 03/11/2026; logs e relatórios preservados. A refatoração mantém as entidades legadas JPA e isola a regra/caso de uso selecionados.

80 testes Java aprovados; 38 classes com 100% de linhas, branches e instruções. Política pura em teste sem Spring; adapter em memória e JPA/H2 preservam histórico e bônus.

Base Git: `bdb6943`, branch local `codex/b1-architecture-lab`, com alterações B1 no momento da execução. Os JSONs dos experimentos e os artefatos do Jenkins registram hashes dos fontes para identificar a implementação efetivamente testada.

## Capturas diretas atualizadas

As telas atuais estão reunidas na pasta `telas-reais`. Os logs e JSONs desta pasta preservam a execução original.

| Item | Tela | Ferramenta |
| --- | --- | --- |
| 2.1 | [Política de bônus isolada](../telas-reais/D2-1-politica-jacoco.jpg) | JaCoCo |
| 2.2 | [Testes dos adapters](../telas-reais/D2-2-testes-adapters-surefire.jpg) | Maven Surefire |
| 2.3a | [Regressão Java](../telas-reais/D2-3a-resumo-surefire.jpg) | Maven Surefire |
| 2.3b | [Cobertura do Core](../telas-reais/D2-3-cobertura-jacoco.jpg) | JaCoCo |

[Manifesto com datas e hashes](../telas-reais/capturas.json).

## Fontes e reprodução

[Saída final Maven](verify-final.log), [JaCoCo](cobertura/index.html) e relatórios `TEST-*.xml` nesta pasta.

[Guia de captura e reprodução](../README.md)

[ADR-002](../../../adr/ADR-002.md) · [C4 fonte](../../../arquitetura/diagramas/component.mmd)

## Limites

As entidades legadas ainda possuem anotações JPA; a proteção é aplicada à política e ao caso de uso selecionados. DDD organiza os conceitos; Hexagonal organiza dependências. Clean/Onion podem compartilhar esse princípio, mas não exigem quatro estruturas simultâneas.

Os relatórios visuais antigos foram substituídos por capturas diretas das ferramentas. O print 1.1 exibe o registro histórico da estrutura; o 1.2 mostra a listagem atual dos diretórios. Os dados originais de execução permanecem preservados.
