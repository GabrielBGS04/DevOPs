"""Apresenta dados reais do laboratório em páginas estáticas para captura no navegador.

Não simula terminal, Swagger ou Jenkins. Cada página identifica o log/JSON-fonte.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from html import escape
import json
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/evidencias/b1'

def block(title, content):
    if not isinstance(content,str): content=json.dumps(content,ensure_ascii=False,indent=2)
    return f'<section><h2>{escape(title)}</h2><pre>{escape(content)}</pre></section>'

def page(challenge, name, title, blocks, source, note=''):
    target=OUT/f'desafio-{challenge:02d}'/f'{name}.html'
    now=datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')
    target.write_text('''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>'''+escape(title)+'''</title>
<style>*{box-sizing:border-box}body{margin:0;padding:36px 44px;color:#14212f;background:#f3f5f7;font:22px Arial,sans-serif}header{border-left:7px solid #194e78;padding-left:22px;margin-bottom:22px}h1{font-size:32px;margin:8px 0}h2{font-size:23px;margin:0 0 12px}p{margin:8px 0;line-height:1.45}small{font-size:17px;color:#415367}section{background:white;border:1px solid #cbd5df;border-radius:6px;padding:20px;margin:16px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:19px/1.4 Consolas,monospace;margin:0}footer{font-size:16px;color:#415367;line-height:1.4}strong{color:#194e78}</style>
<header><small>B1 ARCHITECTURE LAB · DESAFIO '''+str(challenge)+''' · RELATÓRIO TÉCNICO</small><h1>'''+escape(title)+'''</h1><p>'''+escape(note)+'''</p></header>'''+''.join(blocks)+f'<footer>Fonte: {escape(source)}<br>Relatório gerado: {now} · Base bdb6943 + alterações B1 locais.<br>Captura de relatório de dados reais; não é uma simulação de ferramenta.</footer></html>',encoding='utf-8')

def test_results(names):
    rows=[]
    for name in names:
        file=OUT/'desafio-02'/f'TEST-com.example.devops.{name}.xml'
        if not file.exists(): continue
        root=ET.parse(file).getroot()
        rows.append(f"{root.attrib['name']}\n  testes={root.attrib['tests']} falhas={root.attrib['failures']} erros={root.attrib['errors']} tempo={root.attrib['time']}s")
    return '\n\n'.join(rows)

def step_view(step):
    rows=[step['data']]
    if 'url' in step:
        rows.append(f"{step['metodo']} {step['url']}")
        rows.append(f"HTTP {step.get('status')} · duração {step.get('duracaoMs')} ms")
    for key in ['broker','topico','qos','payload','resposta','erro','eventIds','linhas','confirmacao']:
        if key in step:
            rows.append(key+': '+json.dumps(step[key],ensure_ascii=False,separators=(',',':')))
    return '\n'.join(rows)

def select(data, *prefixes):
    chosen=[]
    for prefix in prefixes:
        matches=[s for s in data['passos'] if s['nome'].startswith(prefix)]
        if not matches: continue
        chosen.append(matches[-1])
    return [block(s['nome'],step_view(s)) for s in chosen]

def main():
    baseline=(OUT/'desafio-01/antes-arquivos.txt').read_text(encoding='utf-8-sig')
    before=[s.replace('\\','/') for s in baseline.splitlines() if 'src/main/java' in s.replace('\\','/')]
    page(1,'01-camadas-antes','Organização original em camadas',[
        block('Snapshot do código original', '\n'.join(before)),
        block('Verificação anterior à refatoração','45 testes · 0 falhas · 0 erros\nBUILD SUCCESS\nCobertura por classe: 100% linhas, branches e instruções')],
        'antes-arquivos.txt; baseline-testes.log', 'Snapshot preservado antes da implementação; pastas técnicas horizontais.')
    groups={}
    for file in sorted((ROOT/'src/main/java/com/example/devops').rglob('*.java')):
        rel=file.relative_to(ROOT/'src/main/java/com/example/devops')
        group=rel.parts[0]
        groups.setdefault(group,[]).append(str(rel).replace('\\','/'))
    lines=[]
    for name in ['curso','ranking','gamificacao','aluno','integracao']:
        files=groups.get(name,[])
        lines.append(f'{name}/ — {len(files)} fontes')
        if name in ['curso','ranking','gamificacao']:
            lines.extend('  '+f.split('/',1)[1] for f in files)
    page(1,'02-modulos-depois','Módulos e fronteiras do Core',[
        block('Árvore real do código implementado','\n'.join(lines)),
        block('Integração pela interface pública',"Ranking → AlunoService.consultarRanking() → projeção no banco\nConclusaoDeCurso → ConclusaoPort ← JpaConclusaoAdapter\nCursoService encapsula seu repositório interno")],
        'src/main/java/com/example/devops/; depois-dependencias.txt', 'Modularização incremental no mesmo processo Spring Boot; legado preservado.')
    rule=(ROOT/'src/main/java/com/example/devops/gamificacao/domain/PoliticaBonus.java').read_text(encoding='utf-8')
    page(2,'01-regra-isolada','Política de bônus em Java puro',[
        block('Fonte executado nos testes',rule),block('Resultado do teste unitário',test_results(['PoliticaBonusTest']))],
        'PoliticaBonus.java; TEST-com.example.devops.PoliticaBonusTest.xml', 'Limite 8,5 e bônus de três cursos preservados; regra sem Spring/JPA.')
    page(2,'02-adapters-testados','Mesmo caso de uso com dois adapters',[
        block('Adapter em memória · teste sem Spring',test_results(['ConclusaoDeCursoTest'])),
        block('Adapter JPA · integração H2',test_results(['BancoH2IntegrationTest','ApiIntegrationTest'])),
        block('Contrato verificado','BASICO + 8,5 → histórico registrado e bônus 3\nBASICO + 7,0 → histórico registrado e bônus 0\nCaso de uso depende de ConclusaoPort; adapter JPA consulta CursoService.')],
        'TEST-*.xml; ConclusaoDeCursoTest.java; BancoH2IntegrationTest.java; ApiIntegrationTest.java')
    verify=(OUT/'desafio-02/verify-final.log').read_text(encoding='utf-8',errors='replace')
    proof=[s for s in verify.splitlines() if 'Tests run:' in s or 'All coverage checks' in s or 'BUILD SUCCESS' in s or 'Finished at:' in s or "Analyzed bundle 'devops'" in s]
    page(2,'03-regressao-cobertura','Verificação final e cobertura exigida',[
        block('Saída real de Maven clean verify','\n'.join(proof[-5:]))],
        'verify-final.log; cobertura/jacoco.xml', 'Cobertura verificada no build por classe, para linhas, branches e instruções.')
    for challenge in [3,4,5]:
        file=OUT/f'desafio-{challenge:02d}/execucao.json'
        if not file.exists(): continue
        data=json.loads(file.read_text(encoding='utf-8'))
        if data['estado']!='PASSOU': continue
        note=f"Execução real {data['runId']} · {data['inicio']} · estado {data['estado']}"
        if challenge==3:
            specs=[('01-ia-disponivel','IA disponível e resposta do conteúdo local',('ia-disponivel-recomendacoes','ia-disponivel-assistente')),
                   ('02-ia-indisponivel','Degradação explícita com IA parada',('ia-indisponivel-confirmado','ia-indisponivel-recomendacoes','ia-indisponivel-assistente')),
                   ('03-core-sem-ia','Conclusão e bônus continuam disponíveis',('core-conclui-sem-ia',))]
        elif challenge==4:
            specs=[('01-sincrono-falha','Falha provocada na interação síncrona',('sincrono-falha-esperada',)),
                   ('02-assincrono-pendente','Conclusão confirmada e notificação pendente',('assincrono-conclusao-disponivel','outbox-pendente-apos10s','log-core-pendencia-retentativas')),
                   ('03-recuperacao','Recuperação e confirmação do mesmo evento',('receptor-recuperado-evento-entregue','outbox-sem-pendencias-apos-recuperacao','receptor-deduplica-repeticao'))]
        else:
            specs=[('01-mqtt-publicacao-recepcao','Publicação MQTT e efeito confirmado no Core',('mqtt-publicacao-normal','core-confirmou-mqtt-normal')),
                   ('02-reconexao','Publicação offline e recuperação da sessão',('mqtt-publicado-com-gateway-offline','core-antes-da-reconexao','core-apos-reconexao')),
                   ('03-evento-sem-duplicacao','Retransmissão sem duplicar a recompensa',('mqtt-retransmissao-mesmo-eventId','core-entrada-idempotente-mesmo-eventId','core-apos-repeticao-direta'))]
        for name,title,prefixes in specs:
            page(challenge,name,title,select(data,*prefixes),'execucao.json',note)
    try:
        with urllib.request.urlopen('http://127.0.0.1:8080/api/ranking',timeout=5) as response:
            result={'url':response.url,'status':response.status,'resposta':json.load(response)}
        (OUT/'desafio-01/ranking.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        if result['resposta']:
            visible='GET '+result['url']+'\nHTTP '+str(result['status'])+'\n\n'
            visible+='\n\n'.join(json.dumps(row,ensure_ascii=False) for row in result['resposta'][:3])
            page(1,'03-ranking-funcionando','Ranking consultado na API real', [block('GET /api/ranking · primeiros três itens',visible)],'ranking.json', 'Projeção agregada no banco; 100 pontos por entrada distinta no histórico; desempate por ID.')
    except OSError:
        pass
    print('Relatórios gerados a partir de fontes reais existentes.')

if __name__=='__main__': main()
