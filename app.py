import os
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
import yaml

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}

def coerce(key, value):
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return as_bool(value)
    return str(value)

def normalized_layer(layer):
    result = {}
    for key, value in layer.items():
        if value is None:
            continue
        normalized_key = str(key).strip().lower()
        if normalized_key == "num_workers":
            normalized_key = "workers"
        elif normalized_key.startswith("app_"):
            normalized_key = normalized_key[4:]
        result[normalized_key] = value
    return result

@app.get("/effective-config")
def effective_config(set: Optional[list[str]] = Query(default=None)):
    config = dict(DEFAULTS)

    env_name = os.environ.get("APP_ENV", "development")
    yaml_path = f"config.{env_name}.yaml"
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as file:
            yaml_layer = yaml.safe_load(file) or {}
        config.update(normalized_layer(yaml_layer))

    dotenv_layer = dotenv_values(".env")
    config.update(normalized_layer(dotenv_layer))

    os_layer = {
        key: value
        for key, value in os.environ.items()
        if key.startswith("APP_")
    }
    config.update(normalized_layer(os_layer))

    for item in set or []:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip().lower()
        if key in DEFAULTS:
            config[key] = value

    output = {}
    for key in DEFAULTS:
        value = config.get(key, DEFAULTS[key])
        try:
            output[key] = coerce(key, value)
        except (ValueError, TypeError):
            output[key] = coerce(key, DEFAULTS[key])

    output["api_key"] = "****"
    return output

@app.get("/")
def root():
    return {"status": "ok", "endpoint": "/effective-config"}
