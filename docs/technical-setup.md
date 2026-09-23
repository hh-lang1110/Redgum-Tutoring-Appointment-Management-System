# Technical setup

## Requirements
- Python 3.10 or newer
- No third-party packages

## Run locally in PowerShell
From the project root:

```powershell
$env:HOST = "127.0.0.1"
$env:PORT = "8000"
$env:DB_PATH = "data/redgum.sqlite3"
python app.py
