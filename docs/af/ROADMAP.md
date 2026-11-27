# SkillPath AI — roteiro da AF

## 01 · Fundação compartilhada

Base Git `main` sincronizada com `origin/main` e branch `af/foundation`. Registrar [baseline](BASELINE.md), escopo acadêmico, contratos, C4 e ADR. Preparar o gateway e a navegação. Os quatro requisitos individuais ficam para a próxima fase.

Após a revisão do usuário, publicar somente `af/foundation`, abrir o PR para `main` e solicitar revisão de Gabriel. A decisão de merge pertence à dupla.

## 02 · Implementações individuais

| Responsável | Requisitos | Fronteira de arquivos |
| --- | --- | --- |
| Higor Aranda | RF03 RAG e RF04 agente | `services/spring-ai/`, `src/main/resources/static/af/ia/` e [docs/af/higor/](higor/README.md) |
| Gabriel Baldi | RF02 classificação e RF05 treinamento | `services/ml/`, `src/main/java/com/example/devops/af/competencia/`, `src/main/java/com/example/devops/af/treinamento/`, pacotes equivalentes de testes, `src/main/resources/static/af/ml/` e [docs/af/gabriel/](gabriel/README.md) |
| Ambos, com integração coordenada | RF01 e infraestrutura comum | README raiz, Compose raiz, gateway, navegação geral, catálogo de contratos e adaptadores compartilhados do Core |

Cada integrante inicia sua branch a partir da fundação revisada. Durante a fase individual, cada um registra as mudanças de ambiente, rotas, migrações, permissões e pontos de navegação exigidos no README da própria área. Arquivos compartilhados têm um único responsável por vez durante a integração. Alterações de contrato passam por revisão da dupla antes de alterar consumidor e produtor.

- **Higor.** Selecionar corpus permitido e modelo local de chat/embeddings. Validar compatibilidade do BOM Spring AI com a versão de Spring Boot do serviço independente. Definir seções de fontes, recuperação e qualidade. Testar ação permitida, aprovação explícita, recusa, expiração e repetição. O adaptador de contexto e efeitos no Core exige coordenação conjunta.
- **Gabriel.** Definir o dataset permitido e versionado, os códigos de competência e o modelo inicial. Validar contrato REST, inferência sob carga e publicação de versão. Testar aceitação de job com o ML indisponível, retomada, duplicata e atualização de estado.
- **Dependência comum.** Definir a emissão de tokens de demonstração, a vinculação `sub` → aluno e a credencial para chamadas internas. Usar dados sintéticos na demonstração e acordar a política de acesso ao catálogo e aos conjuntos de dados.

## 03 · Integração e apresentação

1. Aplicar as mudanças compartilhadas em sequência. Ligar as rotas públicas da AF às implementações, manter as rotas anteriores e verificar isolamento entre dependências.
2. Fechar o Compose sem pré-requisitos de processos auxiliares. Executar o roteiro de [arquitetura](ARCHITECTURE.md#execução-com-um-comando-na-entrega-final) em ambiente com Docker Engine e registrar versões, logs e comandos.
3. Demonstrar os cinco RFs e os cenários previstos para os RNFs. Publicar evidências reais nas pastas dos respectivos responsáveis.
