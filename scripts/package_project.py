from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
root=Path.cwd();dest=root/'deliverables'/'Legal_NLP_Mini_Project.zip';dest.parent.mkdir(exist_ok=True)
files=[]
for name in ['README.md','PACKAGE_NOTE.md','pyproject.toml','requirements-lock.txt','config.yaml','config.full.yaml','app.py','.gitignore']:
    files.append(root/name)
for folder in ['.streamlit','src','tests','docs','examples','templates']:
    files.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc'])
files.extend(p for p in (root/'scripts').glob('*') if p.is_file())
for name in ['Final_Report.docx','Final_Report.pdf','Initial_Problem_Statement.docx','Initial_Problem_Statement.pdf','QA.md','artifact.md','final_QA.json','structural_QA.json']:
    files.append(root/'reports'/name)
files.extend((root/'reports'/'figures').glob('*.png'))
for p in (root/'research').rglob('*'):
    if p.is_file() and p.name!='inabs-tree.json':files.append(p)
for name in ['validation.json','demo_inference.json','qualitative_examples.json']:
    files.append(root/'artifacts'/name)
files.append(root/'data'/'raw'/'downloads.json')
files.append(root/'data'/'processed'/'pilot'/'preparation.json')
for task in ['classification','summarization']:
    files.append(root/'data'/'processed'/'pilot'/task/'split_manifest.json')
manifest={}
with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=8) as z:
    for p in sorted(set(files)):
        if not p.is_file():raise FileNotFoundError(p)
        rel=p.relative_to(root).as_posix()
        # Put completed-run records away from live checkpoint paths, so an extracted
        # package correctly asks users to train rather than finding an incomplete run.
        z.write(p,rel)
        manifest[rel]={'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    for model in ['tfidf','legalbert','extractive','t5']:
        base=root/'artifacts'/'pilot'/model
        for rel in ['run.json','training_log.json','test/metrics.json','test/predictions.jsonl']:
            p=base/rel
            if p.is_file():
                arc=f'records/pilot/{model}/{rel}'
                z.write(p,arc)
                manifest[arc]={'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest,indent=2))
with ZipFile(dest) as z:
    assert z.testzip() is None
    names=z.namelist()
    assert all(not n.startswith(('data/raw/cuad','data/raw/inabs','data/processed/pilot/classification/train','data/processed/pilot/summarization/train')) for n in names)
    assert all(not n.endswith(('.safetensors','.joblib')) for n in names)
    assert 'reports/Final_Report.pdf' in names and 'src/legal_nlp/training.py' in names
print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'files':len(names),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2))
