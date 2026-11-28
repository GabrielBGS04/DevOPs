# SkillPath AI — baseline e verificações da fundação

## Base Git

Em 27/11/2026, `git fetch origin` confirmou a mesma SHA em `main` e `origin/main`, `2c9d8563630cd1ee9bdb7e9252a867e096e28801`. A branch `af/foundation` nasceu desse commit. O remoto é [GabrielBGS04/DevOPs](https://github.com/GabrielBGS04/DevOPs). A exclusão local de `docs/entrega/~$_Architecture_Lab_Final.docx` já constava em `git status` e foi preservada.

## Testes automatizados

| Execução | Baseline | Após as alterações |
| --- | --- | --- |
| Maven Wrapper 3.9.16, `clean verify` em modo offline, JDK 25.0.4.1, alvo Java 17 | 80 testes, zero falhas, erros e ignorados. Gate JaCoCo aprovado para 38 classes. | 80 testes, zero falhas, erros e ignorados. Gate JaCoCo aprovado para 38 classes. |
| Python 3.12.14, `pytest` para IA, integrações e runner B1 | 19 testes aprovados. | 19 testes aprovados. `pip check` sem dependências incompatíveis no ambiente usado. |

```powershell
.\mvnw.cmd clean verify
services/ia/.venv/Scripts/python.exe -m pytest services/ia/tests services/integracoes/tests scripts/b1/tests -q
```

O Maven Wrapper inicialmente falhou por falta de escrita no cache. A execução usou o cache Maven existente, com caminho explícito, modo offline e permissão correspondente. As advertências de carregamento dinâmico do agente Mockito em JDK 25 apareceram na execução. No Dockerfile, o Core usa JDK/JRE 17 e Maven 3.9.11. Essa combinação e o download limpo dos pins Python ainda precisam passar pelo build das imagens.

## Gateway, interface e fluxos legados

- O binário Docker Compose 5.6.0 validou a configuração com `config --quiet` e listou `db`, `app`, `gateway`, `ia`, `mqtt` e `integracoes`.
- Nginx 1.28.3 para Windows validou o arquivo versionado com `nginx -t`. Para o ensaio HTTP, uma configuração temporária trocou o DNS Docker por um upstream local e usou portas efêmeras. O gateway encaminhou a página, o Swagger e a API do Core. As rotas reservadas retornaram `503` JSON com identificador de requisição, e `/internal/` retornou `404`.
- Chrome headless verificou a página em 1280 e 390 px. Os três links levaram por teclado às seções esperadas, com foco e sem rolagem horizontal. O envio pela tela criou aluno e curso de teste e concedeu três bônus com nota 8,5. O ensaio serviu localmente a mesma versão do Vue carregada via CDN pela aplicação.
- O Core executou com H2 em memória. Os dois FastAPI e o Mosquitto rodaram em loopback. A recomendação B1 ficou disponível, a outbox entregou a notificação e um evento MQTT QoS 1 foi processado pelo Core. Ao final, os processos temporários foram encerrados e as portas liberadas.
- O diagrama C4 foi renderizado com Mermaid 11.12.2 e inspecionado para conferir limites, componentes e ligações.

## Limites e riscos abertos

- O host está sem Docker Engine disponível. A validação sintática e o ensaio nativo deixam pendentes o build das imagens, injeção DNS do Docker, operação com PostgreSQL e persistência em volumes dos contêineres.
- O frontend depende da CDN Vue. O [plano de integração](ARCHITECTURE.md#execução-com-um-comando-na-entrega-final) prevê servir os assets no build.
- As portas históricas do Core e do banco continuam publicadas no Compose atual, e a API legada usa dados de laboratório. Antes da entrega com identidade real, restringir publicação, provisionar papéis por esquema e validar autenticação e escopos.
- A compatibilidade do BOM Spring AI, o consumo local dos modelos, a extensão pgvector, a recuperação de jobs e o desempenho sob 300 usuários simultâneos serão medidos nas fases seguintes.
