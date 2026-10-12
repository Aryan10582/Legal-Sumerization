"""Conservative cleaning, extraction, and offset-preserving segmentation."""
from io import BytesIO
from pathlib import Path
import re, unicodedata

def clean(text):
    text=unicodedata.normalize("NFC",text).replace("\x00","").replace("\r\n","\n").replace("\r","\n")
    text=re.sub(r"[\t \u00a0]+"," ",text)
    return re.sub(r"\n{3,}","\n\n",text).strip()

def canonical(text):
    return re.sub(r"\s+"," ",unicodedata.normalize("NFC",text)).strip().lower()

def extract(name, data):
    ext=Path(name).suffix.lower()
    if len(data)>20*1024*1024: raise ValueError("File exceeds the 20 MB demonstration limit")
    messages=[]
    if ext==".txt":
        try: text=data.decode("utf-8-sig")
        except UnicodeDecodeError as exc: raise ValueError("Save text as UTF-8 before uploading") from exc
    elif ext==".docx":
        from docx import Document
        from docx.oxml.ns import qn
        d=Document(BytesIO(data))
        # Traverse XML in document order, including table cells (not only paragraphs).
        lines=[]
        for p in d.element.body.iter(qn("w:p")):
            lines.append("".join(t.text or "" for t in p.iter(qn("w:t"))))
        text="\n".join(lines)
    elif ext==".pdf":
        from pypdf import PdfReader
        r=PdfReader(BytesIO(data))
        if r.is_encrypted and not r.decrypt(""): raise ValueError("Password-protected PDF: upload an unlocked copy")
        texts=[]; blank=[]
        for i,page in enumerate(r.pages):
            s=page.extract_text() or ""
            if len(re.sub(r"\s","",s))<20: blank.append(i+1)
            texts.append(s)
        if blank: messages.append(f"Pages with little or no extractable text: {blank}. OCR is not installed; those pages may be scanned and are omitted from usable text.")
        if len(blank)==len(r.pages): raise ValueError("Scanned or empty PDF. Run OCR to produce a searchable PDF, then upload it again.")
        text="\n\n".join(texts)
    else: raise ValueError("Supported types: UTF-8 TXT, DOCX, searchable PDF")
    text=clean(text)
    if len(text)<20: raise ValueError("Too little text to process")
    return text,messages

def segments(text, max_words=100):
    """Every non-whitespace token is retained; offsets address the original context.

    Prefer paragraph/sentence boundaries. Split very long sentences into word spans.
    Numbered headings, names, dates, negations, and citations are never removed.
    """
    chunks=[]
    for match in re.finditer(r"[^\n]+",text):
        line=match.group()
        cursor=0
        for part in re.split(r"(?<=[.!?;])\s+(?=[A-Z0-9(])",line):
            rel=line.find(part,cursor); cursor=rel+len(part)
            words=list(re.finditer(r"\S+",part))
            for i in range(0,len(words),max_words):
                batch=words[i:i+max_words]
                start=match.start()+rel+batch[0].start(); end=match.start()+rel+batch[-1].end()
                chunks.append({"start":start,"end":end,"text":text[start:end]})
    return chunks

def bounded_segments(text, tokenizer, limit=256):
    """Token budget enforcement shared by train, evaluation, and app inference."""
    out=[]
    def add(s):
        ids=tokenizer(s['text'],add_special_tokens=True,truncation=False)['input_ids']
        if len(ids)<=limit: out.append(s); return
        words=list(re.finditer(r"\S+",s['text']))
        if len(words)<2:
            # Rare oversized single token: split by characters, preserving coverage.
            half=max(1,len(s['text'])//2)
        else: half=words[len(words)//2].start()
        for a,b in [(0,half),(half,len(s['text']))]:
            t=s['text'][a:b]
            if t.strip(): add({"start":s['start']+a,"end":s['start']+b,"text":t})
    for s in segments(text): add(s)
    return out
