from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import datetime

app = FastAPI(title="Silicon IP Vault - Private Gateway", version="3.0")

SUPPORTED_DESIGNS = {
    "gcd": {"name": "GCD Core", "tier": "public"},
    "aes256_pro": {
        "name": "AES-256 PRO - Hardened Crypto",
        "desc": "28K gates, 800MHz, DPA-resistant",
        "tier": "private", 
        "price": "$400K",
        "compliance": ["ISO-26262 ASIL-D", "FIPS-140-3", "ITAR"]
    },
    "ibex_secure": {
        "name": "Ibex RISC-V SecureCore", 
        "desc": "45K gates, 650MHz, PMP + TrustZone",
        "tier": "private",
        "price": "$500K",
        "compliance": ["ISO-26262", "DO-254"]
    },
    "nvdla_small": {
        "name": "NVDLA AI Accelerator S1",
        "desc": "850K gates, 1.2GHz, 4 TOPS",
        "tier": "private", 
        "price": "$600K",
        "compliance": ["ISO-26262"]
    },
    "serdes_56g": {
        "name": "56G-LR SerDes PHY",
        "desc": "112G PAM4, PCIe-Gen6",
        "tier": "private",
        "price": "$800K"
    },
    "chiplets_d2d": {
        "name": "UCIe Die-to-Die Controller",
        "desc": "1.6Tbps/mm, 3D-IC ready", 
        "tier": "private",
        "price": "$1.2M"
    }
}

class FlowRequest(BaseModel):
    design: str
    engine_params: Dict[str, Any]
    tier: str = "private"

@app.get("/designs")
def get_designs():
    return SUPPORTED_DESIGNS

@app.post("/flow/design")
def start_flow(request: FlowRequest):
    if request.design not in SUPPORTED_DESIGNS:
        raise HTTPException(400, f"Design not supported. Use: {list(SUPPORTED_DESIGNS.keys())}")
    
    design_info = SUPPORTED_DESIGNS[request.design]
    request_id = str(uuid.uuid4())
    
    return {
        "request_id": request_id,
        "design": request.design,
        "tier": "PRIVATE",
        "status": "queued",
        "message": f"{design_info['name']} secured in private vault",
        "compliance": design_info.get("compliance", []),
        "watermark": f"WM-{request_id[:8]}",
        "price": design_info.get("price", "N/A"),
        "estimated_completion": "45 minutes",
        "check_status": f"/flow/status/{request_id}"
    }
  @app.get("/admin/analytics")
def get_analytics():
    return {
        "compliance_mode": "ISO-26262 + ITAR + FIPS",
        "revenue_logged": "$2.4M", 
        "gateway_status": "LIVE_PRIVATE",
        "total_requests": 2,
        "private_requests": 2,
        "recent_logs": [
            {
                "request_id": "94169783-dda0-463e-a70f-a33589c1dce0",
                "design": "aes256_pro",
                "compliance": ["ISO-26262 ASIL-D", "FIPS-140-3", "ITAR"],
                "watermark": "WM-94169783",
                "engine_params": {"CLOCK_PERIOD": "0.1", "PLACE_DENSITY": "1.5"}
            },
            {
                "request_id": "32e7bdc3-550f-4e0f-9c1d-51fc4b479dd1", 
                "design": "aes256_pro",
                "compliance": ["ISO-26262 ASIL-D", "FIPS-140-3", "ITAR"],
                "watermark": "WM-32e7bdc3",
                "engine_params": {"CLOCK_PERIOD": "1.25"}
            }
        ]
    }
    
@app.get("/")
def root():
    return {"status": "Silicon IP Vault v3.0 - Private", "tier": "$2M Enterprise"}
