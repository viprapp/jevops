import os

from fastapi import FastAPI

app = FastAPI()

REDIS_URL = os.getenv("REDIS_URL", "")


@app.get("/")
def root():
    return {"ok": True, "redis_url_set": bool(REDIS_URL)}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
