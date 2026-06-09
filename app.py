from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()

# Ye OpenRoad ka asli API URL hai. Client se confirm kar lena.
OPENROAD_BASE_URL = "https://api.openroad.com" 

@app.get("/")
def root():
    return {"message": "OpenRoad Proxy Live on Render"}

@app.get("/health")
def health():
    return {"status": "OK"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_openroad(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Client ki request ko OpenRoad tak forward karo
        url = f"{OPENROAD_BASE_URL}/{path}"
        
        # Headers copy karo, 'host' hata ke
        headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
        
        # OpenRoad ko request bhejo
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=await request.body()
        )
        
        # OpenRoad ka response client ko wapas bhejo
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )
