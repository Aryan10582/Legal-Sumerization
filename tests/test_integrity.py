import re
import numpy as np
import pytest
from legal_nlp.text import clean,segments,extract
from legal_nlp.splitting import partition,assert_integrity
from legal_nlp.data import read_cuad,clause_rows
from legal_nlp.common import select_threshold,LABELS
from legal_nlp.evaluation import rouge_metrics,classification_metrics
from legal_nlp.summarization import select_text

def test_clean_preserves_legal_content():
    text='Section 7: shall NOT assign.\r\nRs. 1,50,000 on 12-10-2026.\x00'
    assert clean(text)=='Section 7: shall NOT assign.\nRs. 1,50,000 on 12-10-2026.'

def test_segments_cover_all_words_with_offsets():
    text='1. Governing Law. This contract is subject to Indian law.\n'+('Obligation ' * 240)
    pieces=segments(text)
    assert all(text[r['start']:r['end']]==r['text'] for r in pieces)
    assert re.findall(r'\S+',text)==[w for r in pieces for w in r['text'].split()]

def test_duplicate_train_test_quarantine():
    docs=[{'id':'a','text':'The appeal was dismissed by the court.','official_split':'train'},
          {'id':'b','text':'THE APPEAL was dismissed by the court.','official_split':'test'},
          {'id':'c','text':'The tenant sought repayment of the deposit.','official_split':'train'},
          {'id':'d','text':'The supplier failed to deliver goods in time.','official_split':'train'}]
    split,audit=partition(docs); assert_integrity(split)
    assert audit['quarantined_train_ids']==['a']
    assert split['test'][0]['id']=='b'

def test_leakage_check_fails():
    same={'id':'a','group_id':'1','text':'same document'}
    with pytest.raises(ValueError): assert_integrity({'train':[same],'test':[same]})

def test_multilabel_metrics_not_single_label_confusion():
    y=np.array([[1,0],[1,1],[0,0]]); p=np.array([[.9,.1],[.8,.8],[.1,.2]])
    # Metrics function expects the explicit eight-label schema.
    y=np.pad(y,((0,0),(0,6))); p=np.pad(p,((0,0),(0,6)))
    m=classification_metrics(y,p,.5)
    assert m['subset_accuracy']==1
    assert m['per_class'][LABELS[0]]['confusion_matrix_tn_fp_fn_tp']==[1,0,0,2]

def test_rouge_identity():
    m,_=rouge_metrics(['The appeal was dismissed.'],['The appeal was dismissed.'])
    assert all(m[k]==1 for k in ['rouge1','rouge2','rougeL'])

def test_selector_can_use_late_content_and_obeys_budget():
    text='Background procedural matter. '+('The liability clause limits liability for damages. ' * 8)+'The court dismissed the appeal with costs.'
    result,trace=select_text(text,None,25)
    assert len(result.split())<=25
    assert trace['source_units']>trace['selected_units']
    assert all(0<=s['start']<s['end']<=len(text) for s in trace['spans'])

def test_bad_upload():
    with pytest.raises(ValueError,match='Supported'): extract('data.exe',b'hello world this is unsupported')
    with pytest.raises(ValueError,match='UTF-8'): extract('data.txt',b'\xff\xfe\xff')

def test_threshold_uses_given_validation_only():
    y=np.array([[1,0],[0,1]]); p=np.array([[.4,.1],[.1,.4]])
    threshold,grid=select_threshold(y,p)
    assert threshold<=.4
    assert len(grid)==17
