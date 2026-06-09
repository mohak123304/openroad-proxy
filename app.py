 from fastapi import FastAPI
import httpx
app = FastAPI()

CODESPACE_URL = "https://solid-space-robot-jjx494q6jggg3557r-8080.app.github.dev"

@app.get("/")
def root(): return {"status": "Railway Proxy OK"}

@app.get("/health")
async def health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{CODESPACE_URL}/health")
        return r.json()

@app.post("/run-openroad")
async def run_openroad(payload: dict):
    async with httpx.AsyncClient(timeout=600.0) as client:
        r = await client.post(f"{CODESPACE_URL}/run-openroad", json=payload)
        return r.json()
