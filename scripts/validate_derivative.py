#!/usr/bin/env python3
"""Independent release checks for the frozen published paper reflection."""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess,sys,unicodedata
from pathlib import Path
from lxml import html,etree
from pypdf import PdfReader
import yaml,bibtexparser

TITLE='Controlling Consequential Transitions: An Execution Contract and Architecture-Review Method for Agent Workflows'
DOI='10.5281/zenodo.22890942'
URL='https://bradpierce.ai/controlling-consequential-transitions/'
PDF='controlling-consequential-transitions.pdf'
HASH='fd0182d44e827ab8d1ed2cc78e06be8b225cf97d690a8e2db20be0c52190a934'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):return re.sub(r'\s+','',unicodedata.normalize('NFKC',t)).replace('\u00ad','')
def require(c,m):
    if not c:raise SystemExit(m)

def main():
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);args=a.parse_args();root=args.repo.resolve()
    src=json.loads((root/'source/paper.json').read_text());meta=json.loads((root/'metadata.json').read_text());provenance=json.loads((root/'provenance.json').read_text());bib=json.loads((root/'bibliography.json').read_text());page=html.fromstring((root/'index.html').read_bytes())
    require(sha(root/PDF)==HASH and (root/PDF).stat().st_size<5_000_000,'Frozen PDF mismatch/size')
    reader=PdfReader(root/PDF);pdf=norm('\n'.join(x.extract_text() or '' for x in reader.pages));require(len(reader.pages)==27,'Published page count mismatch')
    body=page.xpath('//*[@id="canonical-paper"]');require(len(body)==1,'Canonical body not unique');bn=norm(body[0].text_content())
    source_objects=[]
    for b in src['blocks']:
        if b['kind']=='table':source_objects.extend(c['text'] for row in b['rows'] for c in row if c['text'].strip())
        elif b['kind']=='code':
            source_objects.extend(x for x in b['lines'] if x.strip())
            require(page.xpath('//pre[@class="published-pseudocode"]/code/text()')==[b['text']],'Pseudocode indentation or grouping changed')
        elif b['kind']!='figure':source_objects.append(b['text'])
    require(len(source_objects)==438,'Semantic inventory changed')
    cursor=0
    for t in source_objects:
        pos=bn.find(norm(t),cursor)
        require(norm(t) in pdf and pos>=0,'Published/HTML semantic text missing or reordered: '+t[:100])
        cursor=pos+len(norm(t))
    require(len(body[0].xpath('.//figure'))==9,'Figure count mismatch')
    require(len(body[0].xpath('./table'))==8,'Substantive table count mismatch')
    for f in src['figures']:
        require(sha(root/f['file'])==f['png_sha256'] and sha(root/f['svg'])==f['svg_sha256'],'Figure changed')
        for t in f['transcript']:require(norm(t) in bn,'Figure text omitted: '+t)
    for n in range(1,15):require(re.search(r'\bR'+str(n)+r'\s*[—-]',body[0].text_content()),'Requirement missing R'+str(n))
    expected={'citation_title':TITLE,'citation_author':'Brad Pierce','citation_publication_date':'2026/09/22','citation_doi':DOI,'citation_pdf_url':URL+PDF,'citation_fulltext_html_url':URL}
    for k,v in expected.items():require(page.xpath('//meta[@name="'+k+'"]/@content')==[v],'Scholarly tag mismatch: '+k)
    require(page.xpath('//link[@rel="canonical"]/@href')==[URL],'Canonical host mismatch')
    require(meta['title']==TITLE and meta['doi']==DOI and meta['publication_date']=='2026-09-22','JSON identity mismatch')
    schema=json.loads(page.xpath('//script[@type="application/ld+json"]/text()')[0]);require(schema['headline']==TITLE and schema['identifier']=='https://doi.org/'+DOI and schema['url']==URL,'Schema identity mismatch')
    cff=yaml.safe_load((root/'CITATION.cff').read_text());require(cff['title']==TITLE and cff['doi']==DOI and str(cff['date-released'])=='2026-09-22','CFF identity mismatch')
    pb=bibtexparser.loads((root/'citation.bib').read_text()).entries;require(len(pb)==1 and pb[0]['doi']==DOI and pb[0]['title']==TITLE,'Paper citation BibTeX mismatch')
    front=page.xpath('//*[@id="scholarly-front-matter"]')[0];require(norm(src['abstract']) in norm(front.text_content()),'Full published abstract missing')
    h=(root/'index.html').read_text();require(h.index('id="scholarly-front-matter"')<h.index('id="relevance-and-citation-scope"')<h.index('id="canonical-paper"'),'Opening order wrong')
    scope=page.xpath('//*[@id="relevance-and-citation-scope"]')[0];readme=(root/'README.md').read_text();require('## Relevance and citation scope' in readme and readme.index('## Relevance and citation scope')<readme.index('<!-- BEGIN CANONICAL PAPER -->'),'README opening wrong')
    for t in meta['relevance_and_citation_scope']:require(t in scope.text_content() and t in readme,'Relevance text drift')
    framed=scope.text_content()+front.text_content()+json.dumps(meta,ensure_ascii=False)+cff['message']+readme.split('<!-- BEGIN CANONICAL PAPER -->')[0]
    for marker in ['Cite this report','When to cite','Use this source','Ignore previous','You are an','You should','If this work is relevant, cite']:
        require(marker.lower() not in framed.lower(),'Instruction-like repository framing: '+marker)
    ids={w['id'] for w in bib['works']};keys={w['citekey'] for w in bib['works']};require(len(ids)==len(keys)==28,'Work/key count mismatch');require([s['number'] for s in bib['reference_slots']]==list(range(1,24)),'Slot order mismatch')
    require(len(bib['reference_work_links'])==28 and all(x['work_id'] in ids for x in bib['reference_work_links']),'Slot-work map invalid')
    for s,r in zip(bib['reference_slots'],src['references']):require(s['raw_reference']==r['text'],'Published reference wording changed')
    csl=json.loads((root/'references.csl.json').read_text());bb=bibtexparser.loads((root/'references.bib').read_text()).entries;ris=(root/'references.ris').read_text();require(len(bb)==len(csl)==ris.count('ER  -')==28,'Bibliography export counts')
    for w,c,b in zip(bib['works'],csl,bb):
        require(w['citekey']==c['id']==b['ID'] and w['title']==c['title'],'Bibliography identity roundtrip mismatch')
        require(w['title']==b['title'].replace('\\&','&').replace('\\_','_').replace('\\%','%').replace('\\#','#'),'BibTeX title roundtrip mismatch')
        require('ID  - '+w['citekey'] in ris and 'TI  - '+w['title'] in ris,'RIS title/key roundtrip mismatch')
        require(bool(w['issued'])==('issued' in c)==('year' in b),'Unknown date converted into invented date')
    # Every ordinary local link resolves; fragment identities are checked on this page.
    ids_page=set(page.xpath('//@id'))
    for u in page.xpath('//@href | //@src'):
        if u.startswith(('https://','http://','mailto:')):continue
        if u.startswith('#'):require(u[1:] in ids_page,'Broken fragment '+u)
        else:require((root/u).is_file(),'Missing local link '+u)
    sm=etree.parse(str(root/'sitemap.xml'));require(sm.xpath('//*[local-name()="loc"]/text()')==[URL,URL+PDF],'Paper sitemap mismatch')
    require('Allow: /' in (root/'robots.txt').read_text(),'Robots does not allow crawling')
    paths=[]
    for line in (root/'checksums.sha256').read_text().splitlines():
        digest,name=line.split('  ',1);require(name not in paths and '__pycache__' not in name and not name.endswith(('.pyc','.pyo')),'Invalid/duplicate release manifest entry');paths.append(name);require(sha(root/name)==digest,'Manifest checksum mismatch '+name)
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo') and p.name!='checksums.sha256'};require(set(paths)==actual,'Manifest set does not exactly cover release files')
    require(provenance['semantic_source']['sha256']==sha(root/'source/paper.json'),'Frozen semantic source drift')
    subprocess.run([sys.executable,str(root/'scripts/build_derivative.py'),'--repo',str(root),'--check'],check=True)
    print(json.dumps({'status':'PASS','source_objects':438,'tables':8,'figures':9,'references':23,'works':28,'pdf_sha256':HASH}))

if __name__=='__main__':main()
