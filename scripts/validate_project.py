"""Execute prepared-data, reload, document extraction and Streamlit checks."""
from pathlib import Path
import os,io,json
os.environ['HF_HOME']=str(Path('artifacts/hf-cache').resolve())
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
from legal_nlp.common import config,read_jsonl,write_json,LABELS
from legal_nlp.inference import Engine
from legal_nlp.text import extract,canonical
from legal_nlp.training import data_fingerprint
from docx import Document
from pypdf import PdfWriter

checks={}
cfg=config()
for task in ['classification','summarization']:
    splits={s:read_jsonl(Path(cfg['data_dir'])/task/(s+'.jsonl')) for s in ['train','validation','test']}
    key='document_id' if task=='classification' else 'id'
    ids={s:{r[key] for r in rows} for s,rows in splits.items()}
    for a,b in [('train','validation'),('train','test'),('validation','test')]:
        assert not ids[a]&ids[b],(task,a,b)
        assert not {canonical(r['text']) for r in splits[a]}&{canonical(r['text']) for r in splits[b]}
    checks[task+'_prepared_split_integrity']='passed'
    for method in (['tfidf','legalbert'] if task=='classification' else ['t5']):
        meta=json.loads((Path(cfg['output_dir'])/method/'run.json').read_text())
        assert meta['data_fingerprint']==data_fingerprint(cfg['data_dir'],task)
        if task=='classification':
            from transformers import AutoTokenizer
            # Package the baseline's exact segmentation tokenizer for offline inference.
            tok=AutoTokenizer.from_pretrained(Path(cfg['output_dir'])/'legalbert')
            if method=='tfidf': tok.save_pretrained(Path(cfg['output_dir'])/'tfidf')
            assert all(len(tok.encode(r['text']))<=cfg['classification']['max_tokens'] for s in splits.values() for r in s)
        checks[method+'_fingerprint_and_token_limits']='passed'

buf=io.BytesIO(); doc=Document(); doc.add_paragraph('The appeal was NOT dismissed on 12 October 2026.'); doc.add_table(rows=1,cols=1).cell(0,0).text='Rs. 1,50,000'; doc.save(buf)
text,_=extract('example.docx',buf.getvalue()); assert 'NOT dismissed' in text and '1,50,000' in text
checks['docx_table_and_paragraph_extraction']='passed'
blank=io.BytesIO(); writer=PdfWriter(); writer.add_blank_page(width=612,height=792); writer.write(blank)
try: extract('scan.pdf',blank.getvalue()); raise AssertionError('Scanned PDF was not rejected')
except ValueError as e: assert 'OCR' in str(e)
checks['scanned_pdf_clear_error']='passed'
examples={}
for task,methods,name in [('classification',['tfidf','legalbert'],'demo_contract.txt'),('summarization',['extractive','t5'],'demo_judgment.txt')]:
    for method in methods:
        result=Engine(cfg,task,method).run(Path('examples',name).read_text(encoding='utf-8'))
        assert result['segments'] if task=='classification' else result['summary']
        examples[method]=result; checks[method+'_checkpoint_reload_and_inference']='passed'
write_json('artifacts/demo_inference.json',examples)

from streamlit.testing.v1 import AppTest
at=AppTest.from_file(str(Path('app.py').resolve()),default_timeout=90).run()
assert not at.exception,list(at.exception)
at.text_area[0].set_value(Path('examples/demo_judgment.txt').read_text(encoding='utf-8'))
at.button[0].click().run()
assert not at.exception and not at.error,(list(at.exception),list(at.error))
assert at.session_state['result'][1]['summary']
checks['streamlit_form_extract_summary_and_exports']='passed'
at.segmented_control[0].set_value('Clause classification').run()
at.text_area[0].set_value(Path('examples/demo_contract.txt').read_text(encoding='utf-8'))
at.button[0].click().run()
assert not at.exception and not at.error,(list(at.exception),list(at.error))
assert at.session_state['result'][1]['segments'] and len(at.dataframe)==1
checks['streamlit_classification_table_and_exports']='passed'
write_json('artifacts/validation.json',{'checks':checks,'scope':'Executed local pilot. UI downloads constructed; browser click/save not automated. No OCR, GPU, full-corpus or external Indian contract evaluation.'})
print(json.dumps(checks,indent=2))
