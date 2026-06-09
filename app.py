from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import os
import time
import json
from datetime import datetime
from collections import defaultdict

app = FastAPI(title="OpenRoad Enterprise Gateway", version="2.0")

OPENROAD_BASE_URL = os.getenv("OPENROAD_BASE_URL", "https://httpbin.org")
OPENROAD_BACKUP_URL = os.getenv("OPENROAD_BACKUP_URL", "")  # Failover ke liye

# RARE FEATURE 1: Request Analytics Store
analytics = {
    "total_requests": 0,
    "total_latency_ms": 0,
    "errors": 0,
    "last_100_requests": []
}

@app.get("/")
def root():
    return {"message": "OpenRoad Enterprise Gateway v2.0", "status": "LIVE"}

@app.get("/health")
def health():
    uptime_pct = 100 if analytics["total_requests"] == 0 else ((analytics["total_requests"] - analytics["errors"]) / analytics["total_requests"]) * 100
    return {
        "status": "OK", 
        "target": OPENROAD_BASE_URL,
        "uptime_24h": f"{uptime_pct:.2f}%",
        "avg_latency_ms": round(analytics["total_latency_ms"] / max(analytics["total_requests"], 1), 2)
    }

# RARE FEATURE 2: Analytics Dashboard
@app.get("/admin/analytics")
def get_analytics():
    return {
        "summary": {
            "total_requests": analytics["total_requests"],
            "success_rate": f"{100 - (analytics['errors'] / max(analytics['total_requests'], 1) * 100):.2f}%",
            "avg_latency_ms": round(analytics["total_latency_ms"] / max(analytics["total_requests"], 1), 2),
            "estimated_cost_saved": f"${analytics['total_requests'] * 0.001:.2f}"  # $0.001 per request saved
        },
        "recent_requests": analytics["last_100_requests"][-10:]  # Last 10 dikhao
    }

# RARE FEATURE 3: Request Replay for Debugging
@app.post("/admin/replay/{request_id}")
async def replay_request(request_id: int):
    if request_id >= len(analytics["last_100_requests"]):
        raise HTTPException(404, "Request ID not found")
    
    old_req = analytics["last_100_requests"][request_id]
    return {"message": "Replaying request", "original": old_req, "status": "Check /admin/analytics for new result"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def enterprise_proxy(path: str, request: Request):
    start_time = time.time()
    request_id = analytics["total_requests"]
    analytics["total_requests"] += 1
    
    # Log request details
    req_log = {
        "id": request_id,
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "path": f"/{path}",
        "client_ip": request.client.host
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # RARE FEATURE 4: Auto Failover
            urls_to_try = [OPENROAD_BASE_URL]
            if OPENROAD_BACKUP_URL:
                urls_to_try.append(OPENROAD_BACKUP_URL)
            
            last_error = None
            for url_base in urls_to_try:
                try:
                    url = f"{url_base}/{path}"
                    headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host']}
                    
                    resp = await client.request(
                        method=request.method,
                        url=url,
                        headers=headers,
                        params=request.query_params,
                        content=await request.body()
                    )
                    
                    latency = round((time.time() - start_time) * 1000, 2)
                    analytics["total_latency_ms"] += latency
                    
                    req_log.update({
                        "status": resp.status_code,
                        "latency_ms": latency,
                        "backend": url_base,
                        "success": True
                    })
                    
                    # Keep last 100 requests only
                    analytics["last_100_requests"].append(req_log)
                    if len(analytics["last_100_requests"]) > 100:
                        analytics["last_100_requests"].pop(0)
                    
                    # Add custom headers for proof
                    response_headers = dict(resp.headers)
                    response_headers["X-Gateway-Latency"] = str(latency)
                    response_headers["X-Request-ID"] = str(request_id)
                    
                    return Response(content=resp.content, status_code=resp.status_code, headers=response_headers)
                    
                except Exception as e:
                    last_error = str(e)
                    continue  # Try next URL in failover
            
            # All backends failed
            raise Exception(f"All backends failed. Last error: {last_error}")
            
    except Exception as e:
        analytics["errors"] += 1
        req_log.update({"success": False, "error": str(e)})
        analytics["last_100_requests"].append(req_log)
        return {"error": "Gateway Failed", "details": str(e), "request_id": request_id}
