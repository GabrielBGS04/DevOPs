"""Busca textual local demonstrativa; não executa ML, RAG ou LLM."""

import json
import re
import unicodedata
from pathlib import Path


CONTENT = json.loads(Path(__file__).with_name('conteudo.json').read_text(encoding='utf-8'))


def normalize(text: str) -> set[str]:
    decomposed = unicodedata.normalize('NFD', text.casefold())
    plain = ''.join(character for character in decomposed if not unicodedata.combining(character))
    return set(re.findall(r'\w+', plain))


def answer(question: str) -> dict:
    words = normalize(question)
    scored = [(len(words.intersection(item['palavras'])), item) for item in CONTENT]
    score, item = max(scored, key=lambda result: result[0])
    if score:
        return {'resposta': item['resposta'], 'fonte': item['fonte']}
    return {
        'resposta': 'O conteúdo local não respondeu à pergunta. Consulte o material do curso.',
        'fonte': 'conteudo-local/sem-correspondencia',
    }
