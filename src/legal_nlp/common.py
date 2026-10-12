from pathlib import Path
import json, hashlib, random, platform, time, sys
import numpy as np
import yaml

LABELS = ["Governing Law", "Non-Compete", "Exclusivity", "Anti-Assignment",
          "Termination For Convenience", "Cap On Liability", "Audit Rights", "Post-Termination Services"]

def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def write_jsonl(path, rows):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w",encoding="utf-8") as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_json(path, obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def config(path="config.yaml"):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def seed_all(seed):
    random.seed(seed); np.random.seed(seed)
    import torch
    torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)

def runtime(cfg):
    import torch, psutil
    torch.set_num_threads(cfg["runtime"]["cpu_threads"])
    request=cfg["runtime"]["device"]
    device = "cuda" if request == "auto" and torch.cuda.is_available() else ("cpu" if request == "auto" else request)
    if device=="cuda" and not torch.cuda.is_available(): raise ValueError("CUDA requested but unavailable")
    return device, {"python":sys.version,"platform":platform.platform(),"processor":platform.processor(),
                    "ram_bytes":psutil.virtual_memory().total,"torch":torch.__version__,"device":device,
                    "gpu":torch.cuda.get_device_name(0) if device=="cuda" else None,
                    "cpu_threads":torch.get_num_threads()}

def select_threshold(y, probabilities):
    """One global threshold, selected ONLY on validation macro F1."""
    from sklearn.metrics import f1_score
    grid=np.arange(.1,.91,.05)
    scored=[(f1_score(y,probabilities>=t,average="macro",zero_division=0),float(t)) for t in grid]
    best=max(scored,key=lambda x:(x[0],-abs(x[1]-.5)))
    return best[1], [{"threshold":t,"macro_f1":s} for s,t in scored]
