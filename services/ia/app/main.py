from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .assistant import answer
from .recommendations import recommend


class Course(BaseModel):
    id: int = Field(gt=0)
    nome: str = Field(min_length=1)


class RecommendationRequest(BaseModel):
    alunoId: int = Field(gt=0)
    historico: list[str]
    cursos: list[Course]


class Question(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    pergunta: str = Field(min_length=1, max_length=2000)

app = FastAPI(title='B1 IA local demonstrativa')


@app.get('/health')
def health():
    return {'status': 'ok', 'servico': 'ia'}


@app.post('/recomendacoes')
def recommendations(request: RecommendationRequest):
    courses = [course.model_dump() for course in request.cursos]
    return {'disponivel': True, 'recomendacoes': recommend(request.historico, courses)}


@app.post('/assistente')
def assistant(request: Question):
    return {'disponivel': True, **answer(request.pergunta)}
