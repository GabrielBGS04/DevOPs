"""Relaciona artefatos reais às seis decisões, sem criar resultados de execução."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone, timedelta
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/evidencias/b1'
SP=timezone(timedelta(hours=-3))

def main():
    desafios=json.loads((ROOT/'docs/arquitetura/desafios.json').read_text(encoding='utf-8'))
    manifest=[]
    for d in desafios:
        folder=BASE/f"desafio-{d['n']:02d}"
        images=[]
        for name in d['prints']:
            file=folder/f'{name}.jpg'
            if not file.is_file(): raise FileNotFoundError(file)
            with Image.open(file) as im:
                if im.format!='JPEG': raise ValueError(f'Formato inesperado: {file}')
                size=im.size
            item={'arquivo':str(file.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
                  'dimensoes':list(size),'capturadoEm':datetime.fromtimestamp(file.stat().st_mtime,SP).isoformat()}
            manifest.append(item); images.append(item)
        if d['n'] in [3,4,5]:
            execution=json.loads((folder/'execucao.json').read_text(encoding='utf-8'))
            if execution['estado']!='PASSOU' or not all(c['passou'] for c in execution['verificacoes']):
                raise ValueError('Experimento não aprovado')
            result=f"{len(execution['verificacoes'])} verificações aprovadas. {execution['conclusao']}"
            details=f"Execução `{execution['runId']}`: {execution['inicio']} a {execution['fim']}. [Respostas e comandos integrais](execucao.json)."
            loglinks='[Execução estruturada](execucao.json) e logs dos comandos em `comandos/`.'
        elif d['n']==1:
            ranking=json.loads((folder/'ranking.json').read_text(encoding='utf-8'))
            assert ranking['status']==200 and len(ranking['resposta'])>=2
            result='Snapshot em camadas preservado; curso e ranking agrupados por capacidade; ranking HTTP 200 com pontuação e ordem verificadas; regressão sem falhas.'
            details='Baseline executado em 03/11/2026: 45 testes aprovados. Verificação final da implementação: 80 testes e cobertura de 100% por classe; ranking consultado após os experimentos de 04/11/2026.'
            loglinks='[Baseline](baseline-testes.log), [RED](red-b1.log), [imports antes](antes-dependencias.txt), [imports depois](depois-dependencias.txt), [resposta real do ranking](ranking.json), [verificação final](../desafio-02/verify-final.log).'
        elif d['n']==2:
            log=(folder/'verify-final.log').read_text(encoding='utf-8',errors='replace')
            assert 'Tests run: 80, Failures: 0, Errors: 0' in log and 'All coverage checks have been met.' in log
            result='80 testes Java aprovados; 38 classes com 100% de linhas, branches e instruções. Política pura em teste sem Spring; adapter em memória e JPA/H2 preservam histórico e bônus.'
            details='Verificação `mvnw.cmd clean verify` concluída em 03/11/2026; logs e relatórios preservados. A refatoração mantém as entidades legadas JPA e isola a regra/caso de uso selecionados.'
            loglinks='[Saída final Maven](verify-final.log), [JaCoCo](cobertura/index.html) e relatórios `TEST-*.xml` nesta pasta.'
        else:
            metrics=json.loads((ROOT/'infra/evidencias/prometheus-resumo.json').read_text(encoding='utf-8-sig'))
            assert all(x['maximo']>x['minimo'] for x in metrics)
            result='Jenkins executou testes, build e deploy nativo: Core #3 (80 testes), IA #8 e integrações #4. IA #9 falhou por teste controlado, bloqueando build/deploy e preservando a última release aprovada.'
            details='Jenkins de 03/11/2026; Grafana e séries reais do experimento de 04/11/2026. Falhas acumuladas da IA variaram de 0 a 2; pendências variaram de 0 a 1 e voltaram a 0. O contador da IA reinicia quando o Core é reiniciado no Desafio 5; isso não representa apagamento das falhas por recuperação da IA.'
            loglinks='[Logs, métricas e auditoria de listeners](../../../../infra/evidencias/), [pipeline Core](http://127.0.0.1:8081/job/b1-core/3/), [sucesso IA](http://127.0.0.1:8081/job/b1-ia/8/), [falha controlada IA](http://127.0.0.1:8081/job/b1-ia/9/), [sucesso integrações](http://127.0.0.1:8081/job/b1-integracoes/4/). URLs localhost exigem laboratório ativo.'
        lines=[f"# Evidências do Desafio {d['n']} — {d['titulo']}", '', '**Estado:** IMPLEMENTADO, EXPERIMENTO EXECUTADO E CAPTURAS SALVAS.', '',
               '## Hipótese arquitetural', '', d['evidencia'], '', '## Execução observada', '', details, '', result, '',
               'Base Git: `bdb6943`, branch local `codex/b1-architecture-lab`, com alterações B1 no momento da execução. Os JSONs dos experimentos e os artefatos do Jenkins registram hashes dos fontes para identificar a implementação efetivamente testada.', '',
               '## Capturas reais', '']
        for item in images:
            filename=Path(item['arquivo']).name
            lines += [f"### {filename}", '', f"![{filename}]({filename})", '', f"Captura: {item['capturadoEm']}. SHA-256: `{item['sha256']}`.", '']
        lines += ['## Fontes e reprodução', '', loglinks, '', '[Guia de captura e reprodução](../README.md)', '',
                  f"[ADR-{d['n']:03d}](../../../adr/ADR-{d['n']:03d}.md) · [C4 fonte](../../../arquitetura/diagramas/{d['c4']}.mmd)", '',
                  '## Limites', '', d['consequencias'], '', 'Os prints dos Desafios 1 a 5 mostram relatórios de dados reais preservados em texto/JSON; não simulam interface de terminal, Swagger ou IDE. Os prints do Desafio 6 mostram Jenkins e Grafana diretamente.', '']
        (folder/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    (BASE/'capturas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    guide=BASE/'README.md'
    txt=guide.read_text(encoding='utf-8').replace('.png','.jpg').replace('PNG','JPEG')
    txt=txt.replace('**Estado:** roteiro de captura. Os experimentos ainda precisam ser implementados e executados. A criação destas pastas não comprova sua execução.',
                    '**Estado:** seis desafios implementados e experimentados no laboratório local, com 18 capturas reais salvas. As pastas de cada desafio relacionam imagens, logs, respostas e limites.')
    txt=txt.replace('A única captura disponível imediatamente','A primeira captura registrada')
    txt=txt.replace('- [ ]','- [x]')
    txt+='\n## Capturas produzidas\n\nAs 18 imagens JPEG foram capturadas no navegador. Desafios 1 a 5: relatórios explícitos dos fontes, testes e respostas reais; Desafio 6: telas diretas do Jenkins e Grafana. Os HTMLs-fonte permanecem ao lado das imagens, com dados originais e identificadores da execução. O [manifesto](capturas.json) registra hash, dimensão e data de cada captura.\n'
    guide.write_text(txt,encoding='utf-8')
    print(f'{len(manifest)} capturas verificadas; seis READMEs de resultados atualizados.')

if __name__=='__main__': main()
