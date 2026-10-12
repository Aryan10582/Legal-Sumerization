import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .text import segments, clean

def select_text(text, tokenizer=None, token_budget=128):
    """TF-IDF centroid/MMR selection over the FULL document, source-order output.

    Token budget counts tokenizer pieces when supplied; otherwise whitespace words.
    No prefix-only truncation. Trace identifies retained and excluded source spans.
    """
    pieces=segments(clean(text),max_words=80)
    if not pieces: return '',{'source_units':0,'selected_units':0,'coverage_fraction':0,'spans':[]}
    texts=[s['text'] for s in pieces]
    def size(s): return len(tokenizer.encode(s,add_special_tokens=False)) if tokenizer else len(s.split())
    try:
        x=TfidfVectorizer(lowercase=True,ngram_range=(1,1),sublinear_tf=True).fit_transform(texts)
        centroid=np.asarray(x.mean(axis=0)).ravel()
        scores=np.asarray(x@centroid).ravel()
        scores=scores/(scores.max() or 1)
    except ValueError:
        x=None; scores=np.ones(len(pieces))
    selected=[]; remaining=set(range(len(pieces))); used=0
    costs=[size(s) for s in texts]; redundancy=np.zeros(len(pieces))
    while remaining:
        eligible={i for i in remaining if costs[i]<=token_budget-used}
        if not eligible: break
        i=max(eligible,key=lambda j:(.7*scores[j]-.3*redundancy[j],-j)); remaining.remove(i)
        candidate=' '.join(pieces[j]['text'] for j in sorted(selected+[i]))
        n=size(candidate)
        if n<=token_budget:
            selected.append(i); used=n
            if x is not None: redundancy=np.maximum(redundancy,(x@x[i].T).toarray().ravel())
    if not selected:
        # An oversized sentence is shortened explicitly, with trace information.
        words=texts[0].split(); chosen=[]
        for word in words:
            if size(' '.join(chosen+[word]))>token_budget: break
            chosen.append(word)
        result=' '.join(chosen)
        return result,{'source_units':len(pieces),'selected_units':1,'selected_tokens':size(result),'source_tokens':size(clean(text)),
                       'coverage_fraction':len(result)/max(1,len(clean(text))),'spans':[],'partial_unit':True}
    selected.sort(); result=' '.join(pieces[i]['text'] for i in selected)
    return result,{'source_units':len(pieces),'selected_units':len(selected),'selected_tokens':used,'source_tokens':size(clean(text)),
                   'coverage_fraction':sum(len(pieces[i]['text']) for i in selected)/max(1,len(clean(text))),
                   'spans':[{'start':pieces[i]['start'],'end':pieces[i]['end']} for i in selected],'partial_unit':False}

def transformer_summary(text, tokenizer, model, device, max_source_tokens=512,max_target_tokens=128,num_beams=2):
    import torch
    prefix='summarize: '
    budget=max_source_tokens-len(tokenizer.encode(prefix,add_special_tokens=True))-1
    source,trace=select_text(text,tokenizer,budget)
    inputs=tokenizer(prefix+source,return_tensors='pt',truncation=False).to(device)
    if inputs.input_ids.shape[-1]>max_source_tokens: raise ValueError('Summary selector exceeded token budget')
    with torch.inference_mode():
        output=model.generate(**inputs,max_new_tokens=max_target_tokens,num_beams=num_beams,
                              do_sample=False,no_repeat_ngram_size=3,early_stopping=num_beams>1)
    return tokenizer.decode(output[0],skip_special_tokens=True),trace
