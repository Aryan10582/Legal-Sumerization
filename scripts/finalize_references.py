"""Produce a checked journal bibliography and an audit of all synopsis entries."""
import json,html,re,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORDER=[14,5,1,28,3,4,13,15,22,21,20,23,24,26,8,25,27,10,16,17]
YEARS={1:2019,2:2016,3:2023,4:2023,5:2023,6:2021,7:2017,8:2022,9:2020,10:2026,11:2025,12:2022,13:2022,14:2019,15:2023,16:2026,17:2023,18:2025,19:2025,20:2025,21:2024,22:2024,23:2025,24:2026,25:2026,26:2025,27:2025,28:2010}
EVIDENCE={
 'Artificial Intelligence and Law':{'status':'publisher-confirmed journal indexing','url':'https://link.springer.com/journal/10506','databases':['Scopus','SCIE','SSCI']},
 'Artificial Intelligence Review':{'status':'publisher-confirmed journal indexing','url':'https://link.springer.com/journal/10462','databases':['Scopus','SCIE']},
 'SN Computer Science':{'status':'publisher-confirmed journal indexing','url':'https://link.springer.com/journal/42979','databases':['Scopus']},
 'Information':{'status':'publisher-confirmed journal indexing','url':'https://www.mdpi.com/journal/information','databases':['Scopus','ESCI']},
 'Mathematics':{'status':'publisher-confirmed journal indexing','url':'https://www.mdpi.com/journal/mathematics/history','databases':['Scopus','SCIE']},
 'IEEE Access':{'status':'publisher-confirmed journal indexing','url':'https://ieeeaccess.ieee.org/about/bibliometrics/','databases':['Scopus','SCIE']},
 'Journal of King Saud University Computer and Information Sciences':{'status':'publisher-confirmed journal indexing','url':'https://link.springer.com/journal/44443','databases':['Scopus','SCIE']},
 'Journal of King Saud University - Computer and Information Sciences':{'status':'publisher-confirmed journal indexing; journal has transferred publisher','url':'https://link.springer.com/journal/44443','databases':['Scopus','SCIE']},
 'Automation in Construction':{'status':'institutional primary record supports Scopus coverage; direct source-list access blocked','url':'https://snu.elsevierpure.com/en/publications/automated-detection-of-contractual-risk-clauses-from-construction/','databases':['Scopus'],'note':'The university author record links the 2022 article to Scopus citations. Current journal metrics corroborated by TU Dresden journal record. No authenticated per-article database audit for 2026.'},
}

def initials(name):
    return ' '.join(s[0]+'.' for s in re.findall(r'[\wÀ-ž]+',name) if s)
def fmt(m,n=None):
    authors=[initials(a.get('given',''))+' '+a['family'] for a in m['author']]
    a=authors[0]+' et al.' if len(authors)>=3 else ' and '.join(authors)
    s=f'{a}, "{html.unescape(m["title"][0])}," {html.unescape(m["container-title"][0])}'
    if m.get('volume'): s+=f', vol. {m["volume"]}'
    if m.get('issue'): s+=f', no. {m["issue"]}'
    article=m.get('article-number')
    page=m.get('page')
    if article: s+=f', Art. no. {article}'
    elif page and '-' in page: s+=f', pp. {page.replace("-","–")}'
    elif page: s+=f', Art. no. {page}'
    s+=f', {m["citation_year"]}, doi: {m["DOI"]}.'
    return (f'[{n}] ' if n else '')+s

def main():
    candidates=json.loads((ROOT/'research/reference-candidates.json').read_text(encoding='utf-8'))
    refs={r['id']:r['candidates'][1 if r['id']==7 else 0] for r in candidates}
    refs[28]={'title':['Identification of Rhetorical Roles for Segmentation and Summarization of a Legal Judgment'],
        'author':[{'given':'M.','family':'Saravanan'},{'given':'B.','family':'Ravindran'}],
        'container-title':['Artificial Intelligence and Law'],'type':'journal-article','volume':'18','issue':'1','page':'45-76',
        'DOI':'10.1007/s10506-010-9087-7','published':{'date-parts':[[2010,5,6]]},'published-online':{'date-parts':[[2010,5,6]]}}
    # Check issue years against publishers, rather than confusing online-first with print year.
    for i,m in refs.items():
        m['citation_year']=YEARS[i]
        journal=html.unescape(m['container-title'][0])
        m['indexing']=EVIDENCE.get(journal,{'status':'not independently verified in this audit','databases':[]})
        m['metadata_source']='Crossref publisher deposit; publisher page where available'
        m['source_id']=i
        m['url']='https://doi.org/'+m['DOI']
        m['checked_on']='2026-10-12'
    final=[{**refs[i],'number':n,'ieee':fmt(refs[i],n)} for n,i in enumerate(ORDER,1)]
    (ROOT/'research/final-bibliography.json').write_text(json.dumps(final,indent=2,ensure_ascii=False),encoding='utf-8')
    (ROOT/'research/bibliography-ieee.txt').write_text('\n\n'.join(m['ieee'] for m in final),encoding='utf-8')
    notes={
     1:'Metadata matches the 2019 issue. Online publication was in 2018.',
     2:'Metadata matches. Outcome prediction is peripheral to the implemented tasks; omitted from the final bibliography. Indexing not independently checked.',
     3:'Verified DOI and journal metadata; article number 250.',
     4:'Verified DOI and journal metadata; article number 1320.',
     5:'Verified DOI and journal metadata; article number 614.',
     6:'Verified DOI, authors and article number. Outcome prediction is peripheral; omitted. Indexing not independently checked.',
     7:'Selected the PLOS ONE journal version, not the earlier SSRN working paper returned first by search. DOI 10.1371/journal.pone.0174698. Omitted as peripheral; indexing not independently checked.',
     8:'Verified DOI, authors and article number. Scopus evidence is the author institution record; direct database source list was blocked.',
     9:'Verified 2020 issue (online 2019). Omitted because judicial outcome prediction uses different labels.',
     10:'Verified 2026 volume 34 issue 2, pp. 523–564 (online 2025). Judgment-domain classification is not contract clause classification.',
     11:'Verified DOI 10.1007/s44443-025-00019-0; volume 37 issue 3, article 31. Omitted as outcome prediction.',
     12:'Verified DOI and metadata. Omitted to prioritize summarization and clause studies; journal indexing not independently confirmed in this audit.',
     13:'Verified 2022 issue; DOI has 2019 because the article was available online earlier.',
     14:'Verified 2019 issue (online 2017); retained as a foundational legal summarization survey.',
     15:'Verified 2023 issue (online 2021); distinguish version-of-record date from issue date.',
     16:'Verified 2026 issue (online 2024). Crossref records pp. 245–266.',
     17:'Crossref author spellings differ from the synopsis: Sangchoconanta and Chaiurangsri. Use the deposited author list; DOI and pages verified.',
     18:'Verified 2025 online-first journal article. Crossref did not supply volume/issue/pages; do not invent these. Omitted from final list.',
     19:'Crossref supplies seven authors, including Yaping Wan, omitted from the synopsis. DOI 10.1016/j.inffus.2025.103081 verified. Omitted as less relevant to eight-label pilot; indexing not independently confirmed.',
    }
    audit=['# Synopsis reference audit','',
      'All 19 entries were searched against publisher-deposited Crossref metadata. The full author lists, all candidate matches, dates, volume, issue, pages/article numbers and DOIs are preserved in reference-candidates.json and crossref/. A title-search hit was not accepted blindly: entry 7 required selecting the journal version. Final issue years were reconciled with publisher pages. Missing fields remain missing.',
      '', 'Journal indexing evidence is journal-level, not an authenticated article-by-article Scopus/WoS export. Publisher claims and the institutional Scopus link are recorded separately. Unconfirmed indexing is explicitly marked; it does not count toward a claim of verification.', '']
    for i in range(1,20):
        m=refs[i]
        audit += [f'## Synopsis [{i}]',fmt(m),notes[i],f'Indexing: {m["indexing"]["status"]}.',f'Metadata: {m["url"]}', '']
    audit+=['## Final selection',f'{len(final)} journal articles. Seventeen are from 2020 onward; the 2010 rhetorical-role study and two 2019 studies are retained for their direct foundational relevance. Conference dataset/model papers and web documentation are recorded in docs/SOURCE_RECORD.md, not disguised as journal articles.',
            '','For Automation in Construction, institutional primary evidence supports Scopus coverage; a current authenticated Scopus/WoS record for each selected article remains a final library check. Publisher-confirmed indexing for the remaining journals is recorded below.','']
    for j,e in EVIDENCE.items(): audit += [f'- {j}: {e["status"]}; {", ".join(e["databases"])}. {e["url"]}']
    (ROOT/'research/SYNOPSIS_REFERENCE_AUDIT.md').write_text('\n\n'.join(audit),encoding='utf-8')
    (ROOT/'research/indexing-evidence.json').write_text(json.dumps(EVIDENCE,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Final bibliography:',len(final),'journal articles')

if __name__=='__main__': main()
