# Config Precedence API

## Run locally
```bash
python -m pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Endpoint: `/effective-config`

Example:
`http://127.0.0.1:8000/effective-config?set=port=9000&set=debug=true`

The app merges defaults, `config.development.yaml`, `.env`, OS `APP_*` variables, and query `set` overrides in that order. API keys are always masked.
