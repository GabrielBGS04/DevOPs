"""Entrega B1: preserva o DOCX recebido e insere respostas e evidências reais."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from lxml import etree
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(r"C:\Users\higor aranda\Downloads\Exercicio_B1_Architecture_Lab_6_Desafios_Reavaliado.docx")
SHA = "cb5b51138ad714b3f86d6bbaf6a47fbdbdf7b41d6ccbf32065714934972b1d7f"
OUTPUT = ROOT / "docs/entrega/B1_Architecture_Lab_Resolvido.docx"
QA = ROOT / "infra/.runtime/word-final"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

CAPTIONS = {
    1: [
        ("Estrutura anterior em camadas", "Snapshot do commit base: controllers, services, repositories e domínio organizados por responsabilidade técnica. O snapshot preserva o antes sem substituir os arquivos atuais."),
        ("Módulos de curso e ranking", "Comparação real de árvore e imports. Ranking usa a API pública de alunos; curso concentra API, aplicação, domínio e persistência."),
        ("Ranking em execução", "Resposta HTTP do ranking e pontuação derivada do histórico. A execução demonstra o contrato funcional; não representa ensaio de carga para 100 mil usuários."),
    ],
    2: [
        ("Regra de bônus isolada", "PoliticaBonus concentra a regra em Java puro. O teste cobre o limiar de nota e a condição do plano, sem inicializar Spring nem banco."),
        ("Adapters substituíveis", "A porta do caso de conclusão é exercitada com memória e com JPA/H2. A mesma política de negócio permanece em ambos os caminhos."),
        ("Regressão e cobertura", "A verificação Maven registrou 80 testes sem falhas. JaCoCo registrou 100% das linhas, instruções e branches nas 38 classes medidas; cobertura não substitui a análise das hipóteses de falha."),
    ],
    3: [
        ("Serviço Python disponível", "Core consulta a recomendação e o assistente pelo contrato HTTP/JSON. A resposta identifica o conteúdo local usado na demonstração."),
        ("Falha da IA tratada", "A indisponibilidade foi confirmada no health do processo Python. O Core responde HTTP 200 com disponivel=false e fallback explícito."),
        ("Conclusão preservada sem IA", "Com IA parada, a conclusão foi confirmada com histórico e três cursos de bônus. O experimento verifica isolamento de falha do fluxo essencial."),
    ],
    4: [
        ("Propagação da falha síncrona", "O receptor foi interrompido e a chamada síncrona registrou falha. A interação dependente mostra o custo do acoplamento temporal."),
        ("Conclusão e outbox pendente", "A conclusão HTTP 200 registra bônus e evento pendente enquanto o consumidor está indisponível. O compromisso essencial é local e transacional."),
        ("Recuperação e entrega eventual", "Após retorno do receptor, o evento identificado é entregue. A entrega admite repetição e o receptor deduplica por eventId."),
    ],
    5: [
        ("Publicação e recepção MQTT", "Publicação QoS 1 no tópico b1/atividades, recepção no gateway e efeito confirmado no Core. PUBACK do broker é distinguido da aceitação de negócio."),
        ("Reconexão e recuperação", "Publicação durante interrupção do gateway e posterior recuperação. O laboratório também verificou spool pendente com Core offline e recuperação após reiniciar o gateway."),
        ("Retransmissão idempotente", "O mesmo eventId é retransmitido por MQTT e diretamente por HTTP. O estado final mantém uma conclusão e três cursos de bônus."),
    ],
    6: [
        ("Pipelines Jenkins concluídos", "Os jobs independentes executam teste, build e deploy. Core nº 3, IA nº 8 e integrações nº 4 tiveram resultado SUCCESS; o deploy local usa JAR/ZIP e health check."),
        ("Teste falho bloqueia implantação", "O build controlado nº 9 da IA falhou na etapa de teste. Build e deploy foram bloqueados e o último artefato aprovado permaneceu disponível."),
        ("Observabilidade de falha e recuperação", "Grafana mostra séries reais: falhas da IA de 0 a 2, outbox de 0 a 1 e de volta a 0. O contador da IA retorna a zero porque o Core reiniciou no ensaio de spool do desafio 5; essa queda não significa recuperação da IA. A drenagem da outbox e os registros HTTP sustentam a recuperação observada."),
    ],
}

FLOW = {
    1: "O C4 mantém um único processo Java e banco relacional. A modularização altera a organização interna; os consumidores seguem usando HTTP/JSON. Separar ranking em processo próprio fica condicionado a medição que justifique escala ou ciclo de deploy independente.",
    2: "O controlador delega ao caso ConclusaoDeCurso; o caso usa ConclusaoPort e PoliticaBonus. JpaConclusaoAdapter implementa a porta para persistência, enquanto os testes substituem esse adapter por memória. A dependência relevante passa a apontar para o contrato da aplicação.",
    3: "O Core chama um processo FastAPI independente por HTTP/JSON. Timeout limita a espera; a indisponibilidade produz resposta degradada. Conclusão e recompensa permanecem no Java e não dependem de resposta da IA.",
    4: "O estado da conclusão e o registro da outbox são confirmados juntos. Um dispatcher consulta pendências e faz HTTP fora do caminho essencial; o consumidor deduplica o eventId. O diagrama de sequência detalha a comunicação entre esses containers do laboratório.",
    5: "O simulador publica no Mosquitto; o gateway consome MQTT, persiste spool SQLite e envia HTTP ao Core. O Core combina inbox e efeito de negócio em transação. Broker, gateway e Core têm responsabilidades distintas; não foi acrescentado outro broker interno.",
    6: "Jenkins implanta Core, IA e integrações separadamente na máquina Windows. Mosquitto recebe eventos; Prometheus coleta o Core e Grafana consulta o Prometheus. Cada processo tem porta explícita e acesso local. O deployment corresponde aos processos efetivamente executados.",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(node) -> bytes:
    return etree.tostring(node, method="c14n")


def reference_contract() -> None:
    assert digest(SOURCE.read_bytes()) == SHA, "A fonte mudou; redestilar antes de editar."
    QA.mkdir(parents=True, exist_ok=True)
    with ZipFile(SOURCE) as z:
        parts = [(n, len(z.read(n)), digest(z.read(n))) for n in z.namelist()]
    text = f"""# Contrato de fidelidade B1

Referência preservada: `{SOURCE}`
SHA-256: `{SHA}`. Oito páginas, uma seção; inspeção visual das oito PNGs em `infra/.runtime/word-reference`, PDF `original.pdf`.

## Sistema da página e tipografia

Letter retrato 21,59 × 27,94 cm; margens superior 1,45 cm, inferior 1,35 cm, laterais 1,65 cm; header/footer a 1,27 cm. Uma coluna, uma seção. Não alterar sectPr ou referências de header/footer. Títulos de página centralizados em Aptos 18, negrito azul 17365D, borda/régua original preservada. Normal Aptos 9, espaço posterior 3 pt. Heading 1 Aptos 13, azul 365F91, antes 5 pt/depois 3 pt. Heading 2 Aptos 10,5, azul 4F81BD, antes 4 pt/depois 2 pt. Listas e tabelas do enunciado são preservadas; nenhuma reconstrução. Header com nome da disciplina alinhado à direita; footer centralizado com exercício e valor. Ambos são preserve-only.

## Padrões e cobertura

Página 1: contexto, regras e case com tabela horizontal RF a evidência. Página 2: entrega e avaliação com duas tabelas. Páginas 3 a 8: título de desafio, cenário, oito itens e entrega. Existem parágrafos explícitos de quebra de página entre padrões. Inventário do package confirma três tabelas, sem imagens no corpo, sem comentários ou controles. Body, células, header/footer e XML foram inspecionados; customXml e demais partes opacas preservadas.

## Mapa de slots e capacidade

Fonte `word/document.xml`, body/p de índices Python 33, 56, 79, 102, 125, 148 são os títulos dos seis desafios. Após cada respectivo último parágrafo de entrega (54, 77, 100, 123, 146, 169), inserir resolução, C4 e três screenshots. Nos desafios 1 a 5 inserir antes do parágrafo original de quebra (55, 78, 101, 124, 147). No 6 inserir antes de body/sectPr. Todos os filhos originais do body são preserve-only, mantidos em ordem, sem alteração de texto ou formatação. Não preencher campos do enunciado nem remover perguntas. O slot novo pode ocupar várias páginas; um print por página para legibilidade.

Estilos novos B1 Body, B1 Heading, B1 Subheading, B1 Caption e B1 Figure herdam Aptos/ritmo da fonte e são pretos. Uso de estilos novos evita alterar a aparência dos oito padrões originais. Nenhum header, footer ou título original será editado. Diagramas e prints inseridos inline com proporções preservadas, largura máxima 18,29 cm e altura máxima 20,6 cm. Legendas com fonte, data de captura e leitura do resultado. Adicionar síntese final AF após as evidências do sexto desafio.

## Partes editáveis e gates

Editar apenas document.xml, adicionar estilos B1 ao styles.xml, ampliar relacionamentos de imagens e content types. Todos os outros package parts devem permanecer byte a byte iguais. Os estilos e relacionamentos originais devem permanecer semanticamente iguais e na mesma ordem. Cada filho original do body deve existir como subsequência canônica intacta. Diagramas e 18 screenshots reais devem ser incorporados, sem depender de links externos. Fonte Downloads deve manter seu SHA original após execução.

Renderizador empacotado render_docx.py foi tentado e diagnosticado em `infra/.runtime/word-render-diagnostico.log`: LibreOffice não existe no bundle Windows. Fallback acordado: Word nativo COM read-only exporta PDF via scripts/b1/render-word.ps1; Poppler empacotado gera PNGs. Inspecionar TODAS as páginas finais e comparar visualmente as oito páginas de enunciado com o padrão fonte. Registar contagem final, imagens, preservação de partes, referências e resultados em QA. Não entregar PDF/PNGs internos.

## Inventário baseline de package parts

| Parte | Bytes | SHA-256 | Regra |
|---|---:|---|---|
"""
    editable = {"word/document.xml", "word/styles.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}
    for name, size, h in parts:
        text += f"| {name} | {size} | {h} | {'acréscimos controlados' if name in editable else 'preserve-only'} |\n"
    (QA / "artifact.md").write_text(text, encoding="utf-8")


def set_styles(doc):
    for name, size, before, after, bold in [
        ("B1 Body", 9, 0, 4, False),
        ("B1 Heading", 13, 0, 8, True),
        ("B1 Subheading", 10.5, 7, 3, True),
        ("B1 Caption", 8, 3, 5, False),
        ("B1 Figure", 9, 4, 5, False),
    ]:
        s = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = doc.styles["Normal"]
        s.font.name, s.font.size, s.font.bold = "Aptos", Pt(size), bold
        s.font.color.rgb = RGBColor(0, 0, 0)
        pf = s.paragraph_format
        pf.space_before, pf.space_after = Pt(before), Pt(after)
        pf.line_spacing = 1.04
        pf.widow_control = True
        if name in ("B1 Heading", "B1 Subheading"):
            pf.keep_with_next = True


class Block:
    def __init__(self, doc, before):
        self.doc, self.before = doc, before

    def p(self, text="", style="B1 Body", page=False):
        p = self.doc.add_paragraph(text, style)
        self.before.addprevious(p._p)
        if page:
            p.paragraph_format.page_break_before = True
        return p

    def label(self, label, text):
        p = self.p()
        p.add_run(label + " ").bold = True
        p.add_run(text)
        return p

    def image(self, path: Path, description: str, max_height=20.6):
        p = self.p(style="B1 Figure")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        with Image.open(path) as im:
            w, h = im.size
        width_cm = min(18.29, max_height * w / h)
        shape = p.add_run().add_picture(str(path), width=Cm(width_cm))
        prop = shape._inline.docPr
        prop.set("descr", description)
        prop.set("title", path.stem)
        return p


def execution_text(n):
    folder = ROOT / f"docs/evidencias/b1/desafio-{n:02d}"
    p = folder / "execucao.json"
    if p.exists():
        result = json.loads(p.read_text(encoding="utf-8-sig"))
        checks = result.get("verificacoes", [])
        passed = sum(c.get("passou") is True for c in checks)
        return f"Execução {result['inicio']} a {result.get('fim', 'fim registrado no JSON')}; resultado {result['estado']}, {passed}/{len(checks)} verificações. {result.get('conclusao', '')}"
    return {
        1: "A árvore anterior foi preservada a partir do commit bdb6943. A árvore atual e os imports mostram o recorte por capacidade. A consulta HTTP ao ranking demonstra o resultado após reorganização; a regressão automatizada verifica os contratos preservados.",
        2: "Maven verify confirmou 80 testes, sem falhas ou erros, e a política JaCoCo passou. A cobertura registrada alcançou 100% nas 38 classes medidas. Os adapters em memória e JPA/H2 exercitam a mesma conclusão; a política pura cobre básico 8,5, básico 7,0 e Premium.",
        6: "Jenkins registrou Core nº 3 SUCCESS com 80 testes, IA nº 8 SUCCESS e integrações nº 4 SUCCESS. O build nº 9 da IA falhou de modo controlado no teste e bloqueou as etapas seguintes. Os 19 testes Python passaram na verificação final. Grafana e Prometheus registram o ciclo observado de falha e recuperação.",
    }[n]


def challenge(block, item):
    n = item["n"]
    block.p(f"Resolução do desafio {n}", "B1 Heading", page=True)
    block.p(item["titulo"], "B1 Subheading")
    block.label("RF", item["rf"])
    block.label("RNF", item["rnfs"])
    block.p("ASRs prioritários e impacto arquitetural", "B1 Subheading")
    for i, (name, why) in enumerate(item["asrs"], 1):
        block.label(f"{i}  {name}.", why)
    block.label("RPC", item["rpc"])
    block.p("Alternativas comparadas", "B1 Subheading")
    for name, tradeoff in item["alternativas"]:
        block.label(name + ".", tradeoff)
    block.p(f"Decisão registrada no ADR {n:03d}", "B1 Subheading")
    block.p(item["decisao"])
    block.label("Consequências e limites.", item["consequencias"])
    block.p(f"Rastreabilidade: docs/adr/ADR-{n:03d}.md; docs/arquitetura/README.md; docs/evidencias/b1/desafio-{n:02d}/.", "B1 Caption")

    block.p(f"Arquitetura e verificação do desafio {n}", "B1 Heading", page=True)
    block.p(FLOW[n])
    diagram = ROOT / f"docs/arquitetura/diagramas/{item['c4']}.png"
    block.image(diagram, f"Diagrama arquitetural do desafio {n}: {item['titulo']}", max_height=12)
    kind = {1: "C4 Container", 2: "C4 Component", 3: "C4 Container", 4: "Sequência dos containers", 5: "C4 Container", 6: "C4 Deployment"}[n]
    block.p(f"Figura D{n}. {kind}. Fonte: docs/arquitetura/diagramas/{item['c4']}.mmd e .png; arquitetura do laboratório em 04/11/2026.", "B1 Caption")
    block.p("Hipótese e resultado observado", "B1 Subheading")
    block.p(execution_text(n))
    block.label("Evidência vinculada.", item["evidencia"])
    block.p("Os três prints seguintes pertencem a este desafio e acompanham os arquivos brutos da pasta de evidências. A captura documenta a tela real; o texto desta página explicita a hipótese arquitetural e os limites do resultado.")

    for i, stem in enumerate(item["prints"], 1):
        title, observation = CAPTIONS[n][i - 1]
        image_path = ROOT / f"docs/evidencias/b1/desafio-{n:02d}/{stem}.jpg"
        stamp = datetime.fromtimestamp(image_path.stat().st_mtime).strftime("%d/%m/%Y %H:%M")
        block.p(f"Evidência {n}.{i} {title}", "B1 Heading", page=True)
        block.image(image_path, f"Print real do desafio {n}, evidência {i}: {title}", max_height=20.0)
        block.p(f"Print {n}.{i}. Fonte: docs/evidencias/b1/desafio-{n:02d}/{stem}.jpg. Captura em {stamp}, horário local de São Paulo.", "B1 Caption")
        block.p(observation)


def summary(block):
    block.p("Síntese final para a Avaliação Final", "B1 Heading", page=True)
    block.p("A PoC da AF deve manter o Core modular, a regra de bônus isolada, a fronteira HTTP da IA com fallback, a outbox transacional e a integração MQTT idempotente. Essas decisões preservam a conclusão do curso diante das falhas exercitadas e oferecem evolução incremental com o legado da AC1.")
    block.p("Decisões que seguem para a PoC", "B1 Subheading")
    for label, text in [
        ("Core", "Manter módulos de curso, ranking e gamificação em um único processo. Medir tempo e custo da consulta de ranking antes de propor processo ou banco independente."),
        ("Domínio", "Manter PoliticaBonus e ConclusaoDeCurso testáveis sem infraestrutura e substituir persistência pela porta já exercitada. Preservar a regra do básico com nota mínima 8,5 e três cursos de bônus."),
        ("IA", "Manter contrato HTTP, timeout e indisponibilidade explícita. Substituir a demonstração determinística por recomendação e RAG/LLM reais somente com corpus, critérios de qualidade, privacidade e avaliação definidos."),
        ("Eventos", "Manter conclusão e outbox atômicas, entrega eventual e deduplicação. Evoluir concorrência do dispatcher antes de múltiplas instâncias; adotar broker adicional apenas com necessidade medida."),
        ("IoT", "Manter Mosquitto, sessão persistente, QoS 1, spool SQLite e inbox no Core. Ampliar injeção de falhas na janela entre commit do Core e confirmação MQTT; definir autenticação e TLS antes de expor fora do loopback."),
        ("Operação", "Manter três pipelines com teste antes de deploy e health check, Prometheus e Grafana. Registrar objetivos de latência, disponibilidade e recuperação para transformar métricas em critérios de aceitação."),
    ]:
        block.label(label + ".", text)
    block.p("Limites comprovados e próximos ensaios", "B1 Subheading")
    block.p("O laboratório foi executado em Windows nativo com Core Java, FastAPI, integrações Python, Mosquitto, Jenkins, Prometheus e Grafana. O banco relacional executado foi H2 em arquivo; SQLite sustenta dados do gateway e deduplicação do receptor. Dockerfiles e Compose estão fornecidos como alternativa e não foram executados. Não houve prova de operação PostgreSQL, 100 mil usuários, implantação em nuvem ou ML/RAG completo.")
    block.p("Os resultados abrangem regressão Java, testes Python e falhas locais reproduzidas nos desafios. Eles sustentam a plausibilidade das decisões no recorte testado. A AF deve acrescentar carga, concorrência, recuperação de dados e testes de contrato entre versões antes de afirmar capacidade de produção.")
    block.p("Equipe e repositório", "B1 Subheading")
    block.p("Gabriel Baldi e Higor Aranda. A premissa de seis desenvolvedores pertence ao cenário do enunciado. Repositório: https://github.com/GabrielBGS04/DevOPs. Base bdb6943aab3baa52994f2f0096c8e4fcef6ccfd6; branch de trabalho codex/b1-architecture-lab, com alterações locais. Esta entrega não declara publicação remota das alterações.")
    block.p("O registro cumulativo e a matriz dos 18 ASRs selecionados estão em docs/arquitetura/README.md; as seis decisões detalhadas em docs/adr; scripts, logs, JSONs, relatórios e capturas em docs/evidencias/b1. O arquivo original recebido em Downloads foi preservado.")


def verify_package(before: bytes, after: bytes):
    editable = {"word/document.xml", "word/styles.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}
    with ZipFile(io.BytesIO(before)) as orig, ZipFile(io.BytesIO(after)) as final:
        for name in orig.namelist():
            if name not in editable:
                assert orig.read(name) == final.read(name), f"Parte preserve-only mudou: {name}"
        for name in ("word/styles.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"):
            a, b = etree.fromstring(orig.read(name)), etree.fromstring(final.read(name))
            final_ids = {(c.get("Id") or c.get(qn("w:styleId")) or c.get("PartName") or c.get("Extension")): c for c in b}
            for c in a:
                ident = c.get("Id") or c.get(qn("w:styleId")) or c.get("PartName") or c.get("Extension")
                if ident:
                    assert canonical(c) == canonical(final_ids[ident]), f"Elemento original mudou em {name}: {ident}"
        a = etree.fromstring(orig.read("word/document.xml")).find("w:body", NS)
        b = etree.fromstring(final.read("word/document.xml")).find("w:body", NS)
        it = iter(b)
        for c in a:
            expected = canonical(c)
            assert any(canonical(x) == expected for x in it), "Elemento original do body alterado/removido"
        assert len(b.findall(".//w:drawing", NS)) == 24, "Esperados seis diagramas e 18 prints"
        return {"partesOriginaisPreservadas": len(orig.namelist()) - len(editable), "filhosOriginaisBodyPreservados": len(a), "figuras": 24, "printsReais": 18, "diagramas": 6}


def build():
    reference_contract()
    items = json.loads((ROOT / "docs/arquitetura/desafios.json").read_text(encoding="utf-8-sig"))
    for item in items:
        for stem in item["prints"]:
            path = ROOT / f"docs/evidencias/b1/desafio-{item['n']:02d}/{stem}.jpg"
            assert path.is_file(), f"Print real ausente: {path}"
    before = SOURCE.read_bytes()
    doc = Document(io.BytesIO(before))
    original_paragraphs = list(doc.paragraphs)
    set_styles(doc)
    break_indices = {1: 55, 2: 78, 3: 101, 4: 124, 5: 147}
    for item in items:
        n = item["n"]
        anchor = original_paragraphs[break_indices[n]]._p if n < 6 else doc._element.body.sectPr
        challenge(Block(doc, anchor), item)
    summary(Block(doc, doc._element.body.sectPr))
    buffer = io.BytesIO()
    doc.save(buffer)
    # python-docx authoring is needed for pictures and in-place insertion. Restore
    # every opaque and preserve-only package part byte-for-byte from the source.
    edit = {"word/document.xml", "word/styles.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}
    rebuilt = io.BytesIO()
    with ZipFile(io.BytesIO(before)) as z0, ZipFile(io.BytesIO(buffer.getvalue())) as z1, ZipFile(rebuilt, "w", ZIP_DEFLATED) as out:
        for part in z1.namelist():
            out.writestr(part, z0.read(part) if part in z0.namelist() and part not in edit else z1.read(part))
    data = rebuilt.getvalue()
    report = verify_package(before, data)
    assert digest(SOURCE.read_bytes()) == SHA
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(data)
    report.update({"output": str(OUTPUT), "sha256Original": SHA, "sha256Final": digest(data), "bytes": len(data)})
    (QA / "verificacao-estrutural.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT.parent / "README.md").write_text("# Entrega B1 resolvida\n\n[B1 Architecture Lab resolvido](B1_Architecture_Lab_Resolvido.docx) contém o enunciado integral, as seis resoluções, seis diagramas e 18 prints reais inseridos após o desafio correspondente.\n\nEquipe: Gabriel Baldi e Higor Aranda. O arquivo fonte `Exercicio_B1_Architecture_Lab_6_Desafios_Reavaliado.docx`, em Downloads, foi preservado. SHA-256: `" + SHA + "`.\n\nO documento acompanha o registro cumulativo em `../arquitetura/README.md`, os ADRs em `../adr/` e os registros de execução em `../evidencias/b1/`. Ambiente executado: Windows nativo, H2 arquivo e JAR/ZIP; Docker e PostgreSQL não executados. IA é demonstração determinística com busca textual local. As alterações são locais e esta entrega não declara publicação remota.\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-reference", action="store_true")
    args = parser.parse_args()
    reference_contract() if args.audit_reference else build()
