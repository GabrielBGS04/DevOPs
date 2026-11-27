# SkillPath AI — requisitos da AF

A referência acadêmica é o Estudo de Caso 1 do `AF_Facens_v3.pdf`, páginas 1 a 3. O termo **colaborador** do enunciado corresponde ao **aluno** cadastrado no Core. Os identificadores abaixo pertencem à AF. Os ADRs históricos usam uma numeração própria do B1.

| ID | Requisito | Responsável | Situação nesta fase e aceite futuro |
| --- | --- | --- | --- |
| RF01 | Cadastrar e consultar colaboradores e cursos | Base compartilhada | Reaproveitar o cadastro e as consultas de alunos e cursos. Revalidar pelo gateway. |
| RF02 | Classificar o nível de competência com ML | Gabriel Baldi | Planejado. Inferir com um modelo treinado e identificado por versão. Exibir nível e confiança por competência. |
| RF03 | Recomendar cursos com RAG sobre documentos institucionais | Higor Aranda | Planejado. Recuperar trechos de um corpus permitido, gerar recomendações fundamentadas e citar os trechos associados a cursos válidos. |
| RF04 | Coordenar orientação e acompanhamento com autorização do usuário | Higor Aranda | Planejado. Exibir a ação e seus efeitos antes da decisão do titular. Demonstrar recusa, expiração e repetição da aprovação sem efeitos duplicados. |
| RF05 | Acompanhar solicitações de treinamento de modelos | Gabriel Baldi | Planejado. Solicitar treinamento assíncrono e consultar lista e detalhe, incluindo sucesso ou falha com motivo seguro para exibição. |

| ID | Requisito não funcional | Verificação prevista para a entrega |
| --- | --- | --- |
| RNF01 | 95% das consultas de classificação em até 2 s com 300 usuários simultâneos | Ensaio pelo gateway com modelo carregado, duração e carga registradas, p95 e taxa de erros reportados. |
| RNF02 | Aceitar solicitações de treinamento com o serviço de ML temporariamente indisponível | Parar o worker, receber `202`, consultar `QUEUED`, recuperar o worker e verificar o estado terminal sem efeitos duplicados. Repetir com o broker indisponível para validar recuperação pela outbox. |
| RNF03 | Proteger dados pessoais e controlar acesso de agentes a informação e ferramentas | Testar acesso entre titulares, escopos, rejeição de ação alterada, expiração e ausência de dados pessoais nos eventos. |
| RNF04 | Evoluir os componentes de IA de forma independente do cadastro e da consulta | Reiniciar ML e Spring AI separadamente e validar alunos, cursos e conclusão em paralelo. |
| RNF05 | Manter custos e esforço operacional adequados à equipe reduzida | Subir a entrega com Compose e medir tempo de inicialização, RAM, armazenamento e tamanho dos modelos locais. |

## Funcionalidades existentes

- Cadastro e consulta de alunos e cursos, conclusão, histórico, bônus e ranking no Core.
- Tela Vue para cadastro e cálculo de nota, com chamadas HTTP na mesma origem.
- Recomendações determinísticas e assistente de busca textual no FastAPI legado, com fallback no Core.
- Outbox de notificações via HTTP, IoT via Mosquitto/MQTT com spool SQLite e inbox idempotente, pipelines Jenkins e observabilidade Prometheus/Grafana no laboratório.

Os serviços legados continuam sustentando os fluxos das ACs. As rotas da AF, treinamento, RAG e autorização passam pelos [contratos propostos](CONTRACTS.md). A [baseline](BASELINE.md) registra o que foi efetivamente executado.
