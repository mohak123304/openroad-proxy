from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import subprocess, uuid, os, shutil
from collections import deque

app = FastAPI()
request_logs = deque(maxlen=500)

# SAB DESIGN KA CONFIG YAHAN
SUPPORTED_DESIGNS = {
    "gcd": {
        "config": "designs/sky130hd/gcd/config.mk",
        "name": "GCD Core",
        "desc": "13K gates, 481MHz - Hello World",
        "gds_path": "results/sky130hd/gcd/6_final.gds"
    },
    "aes": {
        "config": "designs/sky130hd/aes/config.mk", 
        "name": "AES-256 Crypto",
        "desc": "50K gates, 250MHz - Crypto Core",
        "gds_path": "results/sky130hd/aes/6_final.gds"
    },
    "ibex": {
        "config": "designs/sky130hd/ibex/config.mk",
        "name": "Ibex RISC-V CPU", 
        "desc": "25K gates, 300MHz - Real CPU",
        "gds_path": "results/sky130hd/ibex/6_final.gds"
    },
    "tinyrocket": {
        "config": "designs/sky130hd/tinyRocket/config.mk",
        "name": "TinyRocket SOC",
        "desc": "100K gates, 200MHz - Full SOC", 
        "gds_path": "results/sky130hd/tinyRocket/6_final.gds"
    },
    "jpeg": {
        "config": "designs/sky130hd/jpeg/config.mk",
        "name": "JPEG Encoder",
        "desc": "80K gates - Image Processing",
        "gds_path": "results/sky130hd/jpeg/6_final.gds"
    }
}

class DesignRequest(BaseModel):
    design: str  # "gcd", "aes", "ibex", "tinyrocket", "jpeg"
    engine_params: dict = {}  # Engine me change ke liye

@app.post("/flow/design")
async def run_design_flow(req: DesignRequest, background_tasks: BackgroundTasks):
    req_id = str(uuid.uuid4())
    
    if req.design not in SUPPORTED_DESIGNS:
        raise HTTPException(400, f"Design not supported. Use: {list(SUPPORTED_DESIGNS.keys())}")
    
    design_info = SUPPORTED_DESIGNS[req.design]
    
    # ENGINE ME CHANGE: Agar user params bheje
    env_vars = os.environ.copy()
    if req.engine_params:
        # Example: {"PLACE_DENSITY": "0.7", "CORE_UTILIZATION": "50"}
        for key, val in req.engine_params.items():
            env_vars[f"FLOW_{key}"] = str(val)
    
    # LOG KAR
    request_logs.append({
        "request_id": req_id,
        "design": req.design,
        "design_name": design_info["name"],
        "status": "queued",
        "engine_params": req.engine_params,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # BACKGROUND ME CHALA
    background_tasks.add_task(execute_openroad, req_id, design_info, env_vars)
    
    return {
        "request_id": req_id,
        "design": req.design,
        "status": "queued", 
        "message": f"{design_info['name']} flow started",
        "engine_params": req.engine_params,
        "check_status": f"/flow/status/{req_id}",
        "download_gds": f"/flow/gds/{req_id}"
    }

def execute_openroad(req_id, design_info, env_vars):
    try:
        # OpenROAD chalao
        cmd = f"cd /OpenROAD-flow-scripts/flow && make DESIGN_CONFIG={design_info['config']}"
        subprocess.run(cmd, shell=True, env=env_vars, check=True)
        
        # Update log
        for log in request_logs:
            if log["request_id"] == req_id:
                log["status"] = "completed"
                log["gds_ready"] = True
    except Exception as e:
        for log in request_logs:
            if log["request_id"] == req_id:
                log["status"] = "failed"
                log["error"] = str(e)

@app.get("/flow/status/{req_id}")
async def get_status(req_id: str):
    for log in request_logs:
        if log["request_id"] == req_id:
            return log
    raise HTTPException(404, "Request ID not found")

@app.get("/flow/gds/{req_id}")
async def download_gds(req_id: str):
    # Yahan se GDS download hoga jab ready ho
    return {"msg": "GDS download endpoint. Use real storage path"}

@app.get("/admin/analytics")
async def analytics():
    return {
        "gateway_status": "LIVE",
        "total_requests": len(request_logs),
        "supported_designs": list(SUPPORTED_DESIGNS.keys()),
        "recent_logs": list(request_logs)[-10:]
    }

@app.get("/designs")
async def list_designs():
    return SUPPORTED_DESIGNS
    return {"message": f"GDS file {filename} ready post-payment", "note": "Demo mode. Production generates real GDS."}
