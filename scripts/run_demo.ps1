$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:HF_HOME=Join-Path (Get-Location) 'artifacts\hf-cache'
$env:HF_HUB_DISABLE_XET='1'
$env:HF_HUB_OFFLINE='1'
$env:TRANSFORMERS_OFFLINE='1'
& .venv\Scripts\python.exe -m streamlit run app.py
