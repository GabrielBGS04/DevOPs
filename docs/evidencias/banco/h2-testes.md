# Evidência H2

O teste de integração `BancoH2IntegrationTest` executa com o perfil `test` e H2 em memória. Ele cria o esquema, persiste um aluno e um curso, registra a conclusão com nota 8,5 e confirma o bônus de três cursos.

Resultado da execução validada em 15/09/2026:

```text
BancoH2IntegrationTest: 1 teste, 0 falhas, 0 erros
AlunoTest: 3 testes, 0 falhas, 0 erros
Total: 4 testes, 0 falhas, 0 erros
BUILD SUCCESS
```

O SpringDoc é habilitado pela dependência `springdoc-openapi-starter-webmvc-ui`; com a aplicação em execução, o Swagger fica disponível em `/swagger-ui.html` e a especificação em `/v3/api-docs`.
