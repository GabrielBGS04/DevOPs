from fastapi.testclient import TestClient

from services.ia.app.main import app


client = TestClient(app)


def test_recommendations_exclude_history_order_and_limit():
    response = client.post('/recomendacoes', json={
        'alunoId': 7, 'historico': ['Java'],
        'cursos': [{'id': 9, 'nome': 'Docker'}, {'id': 1, 'nome': 'Java'},
                   {'id': 5, 'nome': 'SQL'}, {'id': 3, 'nome': 'Python'},
                   {'id': 8, 'nome': 'Redes'}],
    })
    assert response.status_code == 200
    assert response.json() == {'disponivel': True, 'recomendacoes': [
        {'id': 3, 'nome': 'Python'}, {'id': 5, 'nome': 'SQL'},
        {'id': 8, 'nome': 'Redes'},
    ]}


def test_recommendations_exhausted_catalog_is_available_and_empty():
    response = client.post('/recomendacoes', json={
        'alunoId': 1, 'historico': ['Java'], 'cursos': [{'id': 1, 'nome': 'Java'}],
    })
    assert response.json() == {'disponivel': True, 'recomendacoes': []}


def test_assistant_looks_up_local_bonus_content_and_source():
    response = client.post('/assistente', json={'pergunta': 'Como funciona o bônus?'})
    assert response.status_code == 200
    body = response.json()
    assert body['disponivel'] is True
    assert '8,5' in body['resposta']
    assert 'três' in body['resposta']
    assert body['fonte'] == 'conteudo-local/bonus'


def test_assistant_unknown_question_does_not_invent_answer():
    body = client.post('/assistente', json={'pergunta': 'Qual é a capital de Marte?'}).json()
    assert body['disponivel'] is True
    assert 'não respondeu' in body['resposta']
    assert body['fonte'] == 'conteudo-local/sem-correspondencia'


def test_blank_question_is_rejected():
    assert client.post('/assistente', json={'pergunta': '  '}).status_code == 422


def test_health_identifies_service():
    assert client.get('/health').json() == {'status': 'ok', 'servico': 'ia'}
