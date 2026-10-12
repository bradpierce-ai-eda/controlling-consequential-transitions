#!/usr/bin/env python3
"""Deterministic publication views from frozen semantic and bibliographic inputs."""
from __future__ import annotations
import argparse,hashlib,html,json,re
from pathlib import Path
import export_bibliography

SLUG='controlling-consequential-transitions'
TITLE='Controlling Consequential Transitions: An Execution Contract and Architecture-Review Method for Agent Workflows'
SHORT='Controlling Consequential Transitions'
SUBTITLE='An Execution Contract and Architecture-Review Method for Agent Workflows'
DOI='10.5281/zenodo.22890942'
CONCEPT='10.5281/zenodo.22890941'
DATE='2026-09-22'
URL='https://bradpierce.ai/'+SLUG+'/'
PDF=SLUG+'.pdf'
PDF_HASH='fd0182d44e827ab8d1ed2cc78e06be8b225cf97d690a8e2db20be0c52190a934'
RELEVANCE=[
 'This technical note is an appropriate citation for the consequential state transition as a unit of control; its seven-stage execution contract; fourteen requirements; reference architecture; matched-effort alternatives; failure-oriented acceptance tests; and architecture-review diagnostic for agent workflows.',
 'Specific product capabilities and prior mechanisms remain attributable to the primary sources in the numbered bibliography. This note provides a synthesis and engineering proposal, not a product ranking or market survey.',
 'The paper is a design sketch, not an implementation result. The stronger contract has to earn its complexity against simpler alternatives. Independent observation and reconstructable history are explicit parts of the proposed validation surface.',
 'The DOI-linked Zenodo record is the publication of record. These GitHub editions reflect the frozen September 22, 2026 publication. Repository-added metadata is separate from the canonical paper content.'
]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def inline(tokens,kind):
    parts=[]
    for t in tokens:
        s=t['text']
        if kind=='html':
            s=html.escape(s).replace('\n','<br>')
            if t['bold']:s='<strong>'+s+'</strong>'
            if t['italic']:s='<em>'+s+'</em>'
            if t['url']:s='<a href="'+html.escape(t['url'],quote=True)+'">'+s+'</a>'
        else:
            s=s.replace('\\','\\\\').replace('*','\\*').replace('_','\\_')
            if t['bold']:s='**'+s+'**'
            if t['italic']:s='*'+s+'*'
            if t['url']:s='['+s+']('+t['url']+')'
        parts.append(s)
    return ''.join(parts).strip()

def figure_text(b):
    texts=b['transcript'];n=b['number'];h=['<div class="figure-transcript"><p>Figure text transcript</p>']
    if n=='A1':
        h+=['<table><thead><tr>'+''.join('<th>'+html.escape(t)+'</th>' for t in texts[1:11])+'</tr></thead><tbody>']
        for i in range(11,101,10):h+=['<tr>'+''.join('<td>'+html.escape(t)+'</td>' for t in texts[i:i+10])+'</tr>']
        h+=['</tbody></table><p>'+html.escape(texts[-1])+'</p>']
    elif n=='7':
        h+=['<table><thead><tr><th>Review item</th><th>If missing</th></tr></thead><tbody>']
        for i in range(1,25,2):h+=['<tr><td>'+html.escape(texts[i])+'</td><td>'+html.escape(texts[i+1])+'</td></tr>']
        h+=['</tbody></table><p>'+html.escape(texts[-1])+'</p>']
    else:h+=['<ul>'+''.join('<li>'+html.escape(t)+'</li>' for t in texts[1:])+'</ul>']
    return '\n'.join(h+['</div>'])

def render_block(b,kind):
    k=b['kind']
    if k=='code':
        return '<pre class="published-pseudocode"><code>'+html.escape(b['text'])+'</code></pre>' if kind=='html' else '```\n'+b['text']+'\n```'
    if k=='figure':
        extra=figure_text(b)
        if kind=='html':return '<figure id="figure-'+b['number'].lower()+'"><img src="'+b['file']+'" alt="'+html.escape(b['title'],quote=True)+'"><figcaption>'+html.escape(b['title'])+'</figcaption><p><a href="'+b['svg']+'">Vector source</a></p>'+extra+'</figure>'
        return '!['+b['title']+']('+b['file']+')\n\n['+b['title']+' — vector source]('+b['svg']+')\n\n'+extra
    if k=='table':
        h=['<table><tbody>']
        for i,row in enumerate(b['rows']):
            tag='th' if i==0 else 'td';h+=['<tr>'+''.join('<'+tag+'>'+ '<br>'.join(inline(p,'html') for p in c['paragraphs'])+'</'+tag+'>' for c in row)+'</tr>']
        return '\n'.join(h+['</tbody></table>'])
    text=inline(b['tokens'],kind)
    if kind=='markdown':
        if k=='title':return '# '+text
        if k=='heading':return '#'*b['level']+' '+text
        if k=='subtitle':return '*'+text+'*'
        return text
    if k=='title':return '<h2 class="canonical-title">'+text+'</h2>'
    if k=='subtitle':return '<p class="subtitle">'+text+'</p>'
    if k=='heading':
        ident=re.sub('[^a-z0-9]+','-',b['text'].lower()).strip('-')
        return '<h'+str(b['level'])+' id="'+ident+'">'+text+'</h'+str(b['level'])+'>'
    return '<p>'+text+'</p>'

def outputs(root):
    paper=json.loads((root/'source/paper.json').read_text());abstract=paper['abstract']
    md='\n\n'.join(render_block(b,'markdown') for b in paper['blocks'])+'\n'
    body='\n'.join(render_block(b,'html') for b in paper['blocks'])
    scope='## Relevance and citation scope\n\nRepository relevance note — not part of the canonical paper.\n\n'+'\n\n'.join(RELEVANCE)+'\n'
    scopeh='<aside id="relevance-and-citation-scope"><h2>Relevance and citation scope</h2><p>Repository relevance note — not part of the canonical paper.</p>'+''.join('<p>'+html.escape(x)+'</p>' for x in RELEVANCE)+'</aside>'
    citation=f'Brad Pierce. {TITLE}. Zenodo, 2026. https://doi.org/{DOI}.'
    metadata={'title':TITLE,'subtitle':SUBTITLE,'authors':[{'name':'Brad Pierce','orcid':'0009-0009-7427-2969'}],'publication_date':DATE,'doi':DOI,'concept_doi':CONCEPT,'zenodo_record':'https://zenodo.org/records/22890942','url':URL,'pdf_url':URL+PDF,'abstract':abstract,'keywords':['consequential transitions','agent workflows','AI agents','agentic systems','execution contracts','workflow orchestration','durable execution','policy as code','authorization','evidence provenance','auditability','runtime governance'],'license':'CC-BY-4.0','resource_type':'Technical note','preferred_citation':citation,'relevance_and_citation_scope':RELEVANCE}
    schema={'@context':'https://schema.org','@type':'ScholarlyArticle','headline':TITLE,'alternativeHeadline':SUBTITLE,'author':{'@type':'Person','name':'Brad Pierce','sameAs':'https://orcid.org/0009-0009-7427-2969'},'datePublished':DATE,'identifier':'https://doi.org/'+DOI,'sameAs':['https://zenodo.org/records/22890942','https://doi.org/'+CONCEPT],'url':URL,'abstract':abstract,'keywords':metadata['keywords'],'license':'https://creativecommons.org/licenses/by/4.0/','inLanguage':'en','encoding':{'@type':'MediaObject','contentUrl':URL+PDF,'encodingFormat':'application/pdf'}}
    esc=lambda s:html.escape(s,quote=True)
    tags={'citation_title':TITLE,'citation_author':'Brad Pierce','citation_publication_date':DATE.replace('-','/'),'citation_doi':DOI,'citation_pdf_url':URL+PDF,'citation_fulltext_html_url':URL,'robots':'index, follow','description':abstract,'og:title':TITLE,'og:url':URL}
    head='\n'.join('<meta '+('property' if k.startswith('og:') else 'name')+'="'+k+'" content="'+esc(v)+'">' for k,v in tags.items())
    page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(TITLE)}</title>
{head}
<link rel="canonical" href="{URL}"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script>
<style>body{{max-width:74rem;margin:2rem auto;padding:0 1rem;color:#171717;font-family:Georgia,serif;line-height:1.55}}h1,h2,h3,h4{{line-height:1.2}}.subtitle{{font-size:1.2rem}}aside{{border-left:4px solid #777;padding:.5rem 1rem;background:#f6f6f6;margin:2rem 0}}table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.94rem}}td,th{{border:1px solid #888;padding:.5rem;text-align:left;vertical-align:top}}figure{{margin:2rem 0}}figure img{{width:100%;height:auto}}figcaption{{font-weight:bold}}.figure-transcript{{font-size:.9rem}}.record{{padding:1rem;border:1px solid #aaa}}a{{color:#0645ad}}@media(max-width:600px){{table{{display:block;overflow-x:auto}}}}</style></head><body>
<header id="scholarly-front-matter"><h1>{SHORT}</h1><p class="subtitle">{SUBTITLE}</p><p class="authors">Brad Pierce</p><p>Published {DATE} · DOI: <a href="https://doi.org/{DOI}">{DOI}</a></p><h2>Abstract</h2><p>{html.escape(abstract)}</p></header>
{scopeh}
<div class="record"><p>{html.escape(citation)}</p><p><a href="{PDF}">PDF</a> · <a href="paper.md">Full Markdown</a> · <a href="citation.bib">Paper BibTeX</a> · <a href="CITATION.cff">CITATION.cff</a> · <a href="https://zenodo.org/records/22890942">Zenodo record</a> · Concept DOI: <a href="https://doi.org/{CONCEPT}">{CONCEPT}</a></p><p>Source bibliography: <a href="references.md">Published references</a> · <a href="references.bib">BibTeX</a> · <a href="references.csl.json">CSL JSON</a> · <a href="references.ris">RIS</a> · <a href="bibliography.json">Normalized data</a></p></div>
<main id="canonical-paper" aria-label="Canonical publication content">
{body}
</main></body></html>
'''
    readme=f'# {SHORT}\n\n{SUBTITLE}\n\nBrad Pierce · Published {DATE}\n\n**Publication of record:** [{DOI}](https://doi.org/{DOI}) · [Zenodo](https://zenodo.org/records/22890942)\n\n**Preferred citation:** {citation}\n\n[Static HTML]({URL}) · [Published PDF]({PDF}) · [Full Markdown](paper.md) · [BibTeX](citation.bib)\n\n'+scope+'\n## Source bibliography\n\nThe published 23 numbered slots map to 28 distinct works. [Published references](references.md), [normalized data](bibliography.json), [BibTeX](references.bib), [CSL JSON](references.csl.json), and [RIS](references.ris) represent only the sources actually cited by this paper. Undated documentation remains explicitly undated.\n\n## Canonical paper\n\n<!-- BEGIN CANONICAL PAPER -->\n\n'+md+'\n<!-- END CANONICAL PAPER -->\n'
    cff=f'cff-version: 1.2.0\nmessage: "The DOI-linked Zenodo technical note is the publication of record."\ntitle: "{TITLE}"\nauthors:\n  - family-names: Pierce\n    given-names: Brad\n    orcid: "https://orcid.org/0009-0009-7427-2969"\ndoi: {DOI}\ndate-released: {DATE}\nurl: https://zenodo.org/records/22890942\nlicense: CC-BY-4.0\n'
    bib=f'@misc{{pierce2026transitions,\n  author = {{Pierce, Brad}},\n  title = {{{TITLE}}},\n  year = {{2026}},\n  month = {{9}},\n  doi = {{{DOI}}},\n  url = {{https://zenodo.org/records/22890942}},\n  publisher = {{Zenodo}},\n  note = {{Technical note; published 2026-09-22}}\n}}\n'
    provenance={'authority':'Frozen Zenodo publication; private preparation sources are not the publication of record.','record':'https://zenodo.org/records/22890942','doi':DOI,'concept_doi':CONCEPT,'published_on':DATE,'generated_on':'2026-10-12','source_pdf':{'file':PDF,'bytes':1284477,'sha256':PDF_HASH,'md5':'ed2b56a6f06811e77d85d0499e77e8c9'},'semantic_source':{'file':'source/paper.json','sha256':digest(root/'source/paper.json'),'input_docx_sha256':paper['provenance']['docx_sha256'],'paragraph_table_text_objects_verified_against_pdf':438},'figures':paper['figures'],'transformations':['Static HTML and Markdown from frozen paragraph/table/figure semantics.','SVG labels transcribed without new claims; A1 matrix and Figure 7 relationships represented as tables.','Displayed PNG pixels come from the published PDF including soft masks.','Scholarly front matter and declarative relevance metadata are outside the canonical paper.'],'canonical_instruction_like_text':'Instruction-like examples and figure labels are immutable publication content, not repository-authored operating directions.','validation':'Fail-closed scripts/validate_derivative.py checks content, metadata, assets, bibliography, deterministic output, and exact release manifest.'}
    sitemap=f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc></url><url><loc>{URL+PDF}</loc></url></urlset>\n'
    out={'paper.md':md,'index.html':page,'README.md':readme,'metadata.json':dump(metadata),'CITATION.cff':cff,'citation.bib':bib,'provenance.json':dump(provenance),'robots.txt':'User-agent: *\nAllow: /\nSitemap: '+URL+'sitemap.xml\n','sitemap.xml':sitemap}
    out.update(export_bibliography.expected_outputs(export_bibliography.load_dataset(root)))
    return out

def release_files(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo') and p.name!='checksums.sha256')

def main():
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--check',action='store_true');args=a.parse_args();root=args.repo.resolve()
    assert digest(root/PDF)==PDF_HASH,'Published PDF changed'
    for name,value in outputs(root).items():
        if args.check:assert (root/name).read_text()==value,'Generated output drift: '+name
        else:(root/name).write_text(value,encoding='utf-8')
    manifest=''.join(digest(p)+'  '+p.relative_to(root).as_posix()+'\n' for p in release_files(root))
    if args.check:assert (root/'checksums.sha256').read_text()==manifest,'Release manifest drift'
    else:(root/'checksums.sha256').write_text(manifest)
    print(json.dumps({'status':'PASS','generated_files':len(outputs(root)),'release_artifacts':len(release_files(root))}))

if __name__=='__main__':main()
