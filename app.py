"""Run with: python -m streamlit run app.py"""
from pathlib import Path
import json,io,csv
import streamlit as st
from legal_nlp.common import config,LABELS
from legal_nlp.text import extract,clean
from legal_nlp.inference import Engine

st.set_page_config(page_title='Legal document lab',page_icon=':material/gavel:',layout='wide')
st.title('Legal document lab')
st.caption('Indian judgment summarization and contract clause classification | Machine Learning mini-project')
st.markdown('Review a judgment summary or locate eight types of contract clauses. Compare every output with its source text.')

@st.cache_resource(max_entries=4)
def load_engine(config_path,task,method,checkpoint_stamp):
    return Engine(config(config_path),task,method)

task_label=st.segmented_control('Task',['Judgment summarization','Clause classification'],default='Judgment summarization')
task='summarization' if task_label=='Judgment summarization' else 'classification'
methods={'Extractive baseline':'extractive','Fine-tuned T5':'t5'} if task=='summarization' else {'TF-IDF baseline':'tfidf','Fine-tuned LEGAL-BERT':'legalbert'}
with st.form('document_input'):
    chosen=st.selectbox('Method',list(methods))
    source=st.selectbox('Input',['Paste text','Upload document'])
    pasted=st.text_area('Document text',height=180,placeholder='Paste an English judgment or contract...')
    upload=st.file_uploader('Upload TXT, DOCX or searchable PDF',type=['txt','docx','pdf'],max_upload_size=20)
    submitted=st.form_submit_button('Process document',type='primary',icon=':material/play_arrow:')
st.caption('English text only. Scanned pages require OCR before upload. Uploaded text is processed locally and is not saved by this app.')
if task=='classification':
    st.info('The classifiers were trained on CUAD commercial contracts, not an Indian contract benchmark. Labels may overlap; displayed scores are not calibrated legal confidence.')
    with st.expander('Clause categories'):
        st.markdown(', '.join(LABELS))

if submitted:
    try:
        if source=='Upload document':
            if upload is None: raise ValueError('Select a file before processing')
            text,warnings=extract(upload.name,upload.getvalue())
        else: text=clean(pasted); warnings=[]
        for warning in warnings: st.warning(warning)
        method=methods[chosen]; cfg=config(); run=Path(cfg['output_dir'])/method/'run.json'
        stamp=run.stat().st_mtime if run.exists() else 0
        with st.spinner('Processing the document...'):
            engine=load_engine('config.yaml',task,method,stamp)
            result=engine.run(text)
        st.session_state['result']=(text,result,warnings)
    except Exception as exc:
        st.error(f'Could not process the document: {exc}')
        st.session_state.pop('result',None)

if 'result' in st.session_state:
    text,result,warnings=st.session_state['result']
    if result['task']==task:
        original,output=st.columns([1,1])
        with original:
            st.subheader('Original text')
            with st.container(height=520): st.text(text)
        with output:
            st.subheader('Output')
            st.caption(f"Method: {result['method']} · elapsed {result['seconds']:.2f} s")
            if task=='summarization':
                st.text(result['summary'])
                trace=result['trace']
                st.caption(f"Selected {trace['selected_units']} of {trace['source_units']} source units; retained {trace['coverage_fraction']:.1%} of source characters. Budget: {trace['budget_unit']}.")
                st.download_button('Download summary',result['summary'],file_name='judgment_summary.txt',mime='text/plain')
            else:
                rows=[{'Start':r['start'],'End':r['end'],'Clause':r['text'],'Labels':', '.join(r['labels']) or 'No selected label detected'} for r in result['segments']]
                st.dataframe(rows,hide_index=True,height=480,alt='Contract passages and predicted clause labels with source offsets')
                stream=io.StringIO(); writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
                st.download_button('Download clauses as CSV',stream.getvalue(),file_name='clause_predictions.csv',mime='text/csv')
            st.caption(result['scope'])
            st.download_button('Download full result as JSON',json.dumps(result,indent=2,ensure_ascii=False),file_name='legal_nlp_result.json',mime='application/json')
