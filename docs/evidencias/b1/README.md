# Guia de prints e evidências do B1

**Estado:** seis desafios implementados e experimentados no laboratório local, com 18 capturas reais salvas. As pastas de cada desafio relacionam imagens, logs, respostas e limites.

## Pasta correta

Usar a raiz confirmada com o GitHub:

```text
C:\Users\higor aranda\Documents\importante\ENGENHARIA DE SOFTWARE\aaaaaaa\DEVOPS
```

Ela está na branch `main`, commit `bdb6943` (`jacoco 100%`), que correspondia ao GitHub na conferência de 03/11/2026. A pasta interna `DEVOPS\DevOPs` é outra cópia, no commit anterior `f37ac3a`; não salvar as evidências do B1 nela.

Repositório conferido: https://github.com/GabrielBGS04/DevOPs

O [plano de implementação](../../superpowers/plans/2026-11-03-b1-architecture-lab.md) define os experimentos. A [especificação](../../superpowers/specs/2026-11-03-b1-design.md) fixa os comportamentos esperados.

## Quantos prints e onde salvar

Sugestão: **18 prints, três por desafio**. A quantidade é uma organização proposta para a entrega; o enunciado fornecido não fixa um total de imagens. Se a professora tiver uma orientação adicional sobre quantidade ou formato, ela deve ser aplicada.

Salvar cada imagem na pasta correspondente abaixo, dentro desta raiz. Usar os nomes da tabela para facilitar os links no registro arquitetural.

| Desafio | Pasta dentro do projeto | O que os prints precisam demonstrar |
| --- | --- | --- |
| 1 | `docs/evidencias/b1/desafio-01/` | Organização em camadas, organização modular e ranking funcionando |
| 2 | `docs/evidencias/b1/desafio-02/` | Regra isolada, adapters substituíveis e regressão preservada |
| 3 | `docs/evidencias/b1/desafio-03/` | IA funcionando, degradação durante falha e Core funcionando sem IA |
| 4 | `docs/evidencias/b1/desafio-04/` | Falha síncrona, conclusão com notificação pendente e recuperação |
| 5 | `docs/evidencias/b1/desafio-05/` | Publicação/recepção MQTT, reconexão e ausência de bônus duplicado |
| 6 | `docs/evidencias/b1/desafio-06/` | Jenkins com sucesso, deploy bloqueado por falha e métricas de recuperação |

## Como fazer uma captura útil

1. Executar o cenário antes de capturar. Confirmar o resultado e manter o comando, endpoint ou teste legível na tela.
2. Usar `Win + Shift + S` para capturar a janela ou região relevante. Salvar em JPEG com o nome indicado.
3. Mostrar o resultado completo: status HTTP e corpo, resumo dos testes ou estágios do pipeline. Para comparar sistemas, organizar as janelas lado a lado.
4. Mostrar o mesmo identificador de aluno/curso/evento nos pontos correlacionados. Isso conecta publicação, recebimento e efeito no negócio.
5. Preencher o README da pasta com data, commit, comando, resultado observado e conclusão. Resultados esperados neste guia não são resultados já obtidos.
6. Guardar também logs em texto e relatórios necessários. Um terminal com `BUILD SUCCESS` comprova o build executado; a evidência arquitetural precisa mostrar a hipótese testada.

As imagens devem ser legíveis no GitHub sem ampliar excessivamente. Pode recortar áreas sem informação, mas preservar o contexto do resultado. Evitar capturar tokens, senhas pessoais ou dados reais de alunos.

## Desafio 1 — camadas e módulos

**Momento:** o primeiro print deve ser tirado agora, antes da modularização. Os outros dois, depois da implementação do Desafio 1.

| Arquivo | Tela a capturar | Conteúdo que precisa aparecer |
| --- | --- | --- |
| `01-camadas-antes.jpg` | Explorador da IDE com a estrutura original expandida | Caminho da raiz e `src/main/java/com/example/devops` com `controller`, `service`, `repository`, `domain` e `dto` |
| `02-modulos-depois.jpg` | A mesma árvore após a refatoração | Módulo `curso` com API/aplicação/domínio/persistência e módulo `ranking`; comparar com o print anterior |
| `03-ranking-funcionando.jpg` | Swagger, Postman ou terminal chamando `GET /api/ranking` | URL, HTTP 200 e pelo menos dois alunos com quantidade de conclusões e pontuação ordenada |

Para exibir a árvore original no terminal, a partir da raiz correta:

```powershell
Get-Location
tree /F src\main\java\com\example\devops
```

**Acompanhar com:** log dos testes, relatório de dependências/imports antes/depois e ADR-001. A mudança de pastas demonstra organização; o relatório deve explicar também as fronteiras e dependências. Não usar esse experimento para afirmar que o sistema já suporta 100 mil usuários.

## Desafio 2 — domínio e adapters

**Momento:** após extrair a política de bônus e implementar as duas formas de persistência do caso de uso.

| Arquivo | Tela a capturar | Conteúdo que precisa aparecer |
| --- | --- | --- |
| `01-regra-isolada.jpg` | Editor e execução do teste unitário da política | Regra Java sem imports Spring/JPA e testes para básico 8,49 → 0, básico 8,5 → 3 e Premium → 0 |
| `02-adapters-testados.jpg` | Terminal ou painel de testes | Contrato executado com adapter em memória e adapter JPA/H2, ambos verificando a mesma recompensa e o histórico |
| `03-regressao-cobertura.jpg` | Terminal e resumo JaCoCo | Suíte final sem falhas, `BUILD SUCCESS` do `verify` e cobertura conforme a política configurada |

**Acompanhar com:** relatórios dos testes e ADR-002 com C4 Component. A captura precisa identificar quais adapters foram testados; somente mostrar o nome de uma interface não demonstra que a troca funciona.

## Desafio 3 — IA e indisponibilidade

**Momento:** executar o experimento planejado em `scripts/b1/desafio-03.ps1`, quando o script e os serviços existirem. O script deverá imprimir os dados criados e as respostas para facilitar a captura.

| Arquivo | Tela a capturar | Conteúdo que precisa aparecer |
| --- | --- | --- |
| `01-ia-disponivel.jpg` | Requisições ao Core e resposta do serviço Python | Recomendações e assistente via Core, HTTP 200, `disponivel=true` e resultado demonstrativo identificado |
| `02-ia-indisponivel.jpg` | Estado do serviço `ia` e nova resposta do Core | Python parado, mesma consulta com `disponivel=false`, fallback e tempo observado |
| `03-core-sem-ia.jpg` | Conclusão de curso com Python ainda parado | Requisição ao endpoint existente, HTTP 200, nota 8,5 registrada e aumento de três cursos para aluno básico |

**Acompanhar com:** log das chamadas e testes de timeout/resposta inválida. Registrar a nota e os cursos disponíveis antes/depois. O teste é de integração e isolamento de falha; identificar a IA como microsolução demonstrativa, sem afirmar treinamento de ML ou RAG/LLM completo.

## Desafio 4 — entrega assíncrona

**Momento:** executar `scripts/b1/desafio-04.ps1` quando o receptor, outbox e worker estiverem implementados.

| Arquivo | Tela a capturar | Conteúdo que precisa aparecer |
| --- | --- | --- |
| `01-sincrono-falha.jpg` | Chamada de notificação síncrona do laboratório com receptor parado | Endpoint/comando, erro de conexão/timeout e identificação de falha provocada |
| `02-assincrono-pendente.jpg` | Conclusão bem-sucedida com receptor ainda parado e consulta da outbox | HTTP 200, bônus aplicado e identificador de evento persistido como pendente |
| `03-recuperacao.jpg` | Receptor restaurado, logs e nova consulta da outbox | O mesmo identificador recebido/processado e evento marcado como entregue |

**Acompanhar com:** log das tentativas e timestamps, teste de rollback e teste de deduplicação. A falha do primeiro print é um resultado esperado da comparação; ela não deve permanecer como defeito no fluxo essencial.

## Desafio 5 — MQTT, reconexão e duplicidade

**Momento:** executar `scripts/b1/desafio-05.ps1` com broker, gateway e Core implementados.

| Arquivo | Tela a capturar | Conteúdo que precisa aparecer |
| --- | --- | --- |
| `01-mqtt-publicacao-recepcao.jpg` | Publicador e gateway lado a lado | Tópico `b1/atividades`, JSON publicado, mesmo `eventId` recebido e aceitação pelo Core |
| `02-reconexao.jpg` | Linha do tempo do experimento e logs após reconexão | Gateway desconectado, publicação durante a ausência, reconexão e recebimento do evento pendente |
| `03-evento-sem-duplicacao.jpg` | Retransmissão e consulta do aluno/registro | Mesmo `eventId` enviado novamente, resposta de sucesso idempotente e bônus total de três cursos, sem segundo acréscimo |

**Acompanhar com:** configuração de persistência/sessão/QoS do broker e testes de idempotência. Usar aluno novo e registrar saldo inicial para tornar a ausência de duplicação verificável. Não usar evento com outro ID para esse teste, pois seria uma nova operação.

## Desafio 6 — Jenkins e observabilidade

**Momento:** após configurar o agente, pipelines, exportação de métricas e dashboard. Executar `scripts/b1/desafio-06.ps1` e aguardar coleta do Prometheus.

| Arquivo | Tela a capturar | Conteúdo que precisa aparecer |
| --- | --- | --- |
| `01-jenkins-sucesso.jpg` | Página do build do Core no Jenkins | Nome do job, número do build, commit e estágios de teste/build/deploy concluídos com sucesso |
| `02-jenkins-bloqueio.jpg` | Build controlado com teste falhando no Jenkins | Estágio de teste falho e deploy não executado; identificar que é um experimento controlado |
| `03-grafana-falha-recuperacao.jpg` | Dashboard Grafana no intervalo do experimento | Datas/horários, falhas da IA e notificações pendentes variando durante parada e recuperação dos serviços |

**Acompanhar com:** logs e relatórios dos pipelines de `core`, `ia` e `integracoes`, consultas do Prometheus e dashboard versionado. A imagem de sucesso do Core não substitui os resultados dos outros dois pipelines. Se não couberem na evidência textual, acrescentar prints `04-jenkins-ia.jpg` e `05-jenkins-integracoes.jpg`.

No Grafana, o contador acumulado de falhas da IA não volta a zero após recuperar o serviço: sua taxa de crescimento deve cessar. A quantidade de notificações pendentes deve diminuir quando a entrega voltar. Escolher o intervalo de tempo que inclua funcionamento, falha e recuperação; uma tela vazia ou apenas `up=1` não demonstra esses efeitos.

## Como relacionar o print à decisão

No README de cada desafio, preencher uma tabela como esta somente após executar:

| Campo | Informação a registrar |
| --- | --- |
| Data e horário | Momento da captura e fuso usado |
| Commit | Saída de `git rev-parse --short HEAD`; se houver código sem commit, informar e preservar o diff da execução |
| Cenário | Hipótese arquitetural e condições iniciais |
| Comando/requisição | Ação exata, incluindo IDs/dados de teste necessários |
| Resultado observado | Saída real, status, contagens ou métrica |
| Conclusão e limite | O que o resultado sustenta e o que não foi medido |
| Arquivos | Print, log e relatório relacionados |

Depois de salvar uma imagem real, incluir no README do desafio usando o nome relativo. Exemplo de sintaxe para o primeiro print: `![Organização em camadas antes da refatoração](01-camadas-antes.jpg)`.

O registro final `docs/arquitetura/README.md` deve apontar para os READMEs destas seis pastas e para os ADRs correspondentes. Os diagramas C4 devem ser versionados como fonte e exibidos de forma legível; eles complementam os prints de execução.

## Conferência antes de entregar

- [x] Existem as 18 capturas previstas ou uma justificativa explícita para alteração do roteiro.
- [x] Imagens legíveis, nomes consistentes e links funcionando no GitHub.
- [x] Cada desafio identifica hipótese, ASRs/RPCs, alternativas, ADR, C4 e evidência.
- [x] Cada print está associado a resultado observado e comando reproduzível.
- [x] Falhas provocadas e degradação estão explicadas.
- [x] Testes e experimentos ainda não executados continuam marcados como pendentes.
- [ ] Publicação no GitHub conferida no link que será entregue à professora (concluir após o versionamento local).

## Capturas produzidas

As 18 imagens JPEG foram capturadas no navegador. Desafios 1 a 5: relatórios explícitos dos fontes, testes e respostas reais; Desafio 6: telas diretas do Jenkins e Grafana. Os HTMLs-fonte permanecem ao lado das imagens, com dados originais e identificadores da execução. O [manifesto](capturas.json) registra hash, dimensão e data de cada captura.
