from fastapi import FastAPI, Request, Response
import httpx
import os

app = FastAPI()

# Environment variables se URL aur Key lenge
OPENROAD_BASE_URL = os.getenv("OPENROAD_BASE_URL", "https://httpbin.org")  # Test ke liye httpbin daala hai
OPENROAD_API_KEY = os.getenv("OPENROAD_API_KEY", "")

@app.get("/")
def root():
    return {"message": "OpenRoad Proxy Live on Render"}

@app.get("/health")
def health():
    return {"status": "OK", "target": OPENROAD_BASE_URL}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_openroad(path: str, request: Request):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{OPENROAD_BASE_URL}/{path}"
            headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}
            
            if OPENROAD_API_KEY:
                headers['Authorization'] = f"Bearer {OPENROAD_API_KEY}"

            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                params=request.query_params,
                content=await request.body()
            )
            
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers)
            )
    except Exception as e:
        return {"error": "Proxy Failed", "details": str(e), "target_url": f"{OPENROAD_BASE_URL}/{path}"}
