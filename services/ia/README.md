# IA local demonstrativa B1

Um executável FastAPI oferece recomendação determinística e busca textual em conteúdo local. Não acessa o banco do Core, não treina modelo, não usa API paga e não implementa RAG/LLM completo.

Na raiz do repositório, usando Python 3.12:

```powershell
python -m venv services/ia/.venv
services/ia/.venv/Scripts/python.exe -m pip install -r services/ia/requirements-dev.txt
services/ia/.venv/Scripts/python.exe -m pytest services/ia/tests -v
services/ia/.venv/Scripts/python.exe -m uvicorn services.ia.app.main:app --host 127.0.0.1 --port 8001
```

Também é possível entrar em `services/ia` e executar `python -m uvicorn app.main:app --port 8001`, usando o ambiente virtual ativado.

| Rota | Contrato |
| --- | --- |
| `GET /health` | `{"status":"ok","servico":"ia"}` |
| `POST /recomendacoes` | Entrada: `{"alunoId":1,"historico":["Java"],"cursos":[{"id":2,"nome":"Python"}]}`. Saída: `{"disponivel":true,"recomendacoes":[{"id":2,"nome":"Python"}]}` |
| `POST /assistente` | Entrada: `{"pergunta":"Como funciona o bônus?"}`. Saída: `disponivel`, `resposta` e `fonte` |

A recomendação exclui os nomes presentes no histórico, ordena por ID crescente e limita a três itens. O assistente normaliza acentos e procura palavras dos assuntos no arquivo `app/conteudo.json`. Sem correspondência, declara que o conteúdo local não respondeu à pergunta. Perguntas vazias são rejeitadas com HTTP 422.

O Core é responsável pelo timeout de dois segundos e pela resposta degradada quando este serviço estiver indisponível. Esses mecanismos não são simulados dentro da IA.

`tests/evidence/01-red-missing-service.log` registra a ausência inicial do pacote; `02-red-contracts.log` registra seis testes falhando nos contratos ainda ausentes. `04-green-python-suite.log` registra os 12 testes Python dos dois serviços passando sem avisos. Os logs iniciais preservam avisos das versões exploradas antes de fixar as dependências compatíveis.

`Dockerfile` possui alvos `test` e `runtime`. O `Jenkinsfile` espera agente com label `docker`, checkout do repositório e acesso ao engine/Compose local; executa testes antes do build e atualiza somente `ia`, com imagem `b1-ia:${B1_IMAGE_TAG}`. O caminho nativo do laboratório é documentado na infraestrutura. A existência desses arquivos não comprova execução de Docker/Jenkins.
