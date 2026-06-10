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

@app.get("/")
def root():
    return {"status": "Silicon IP Vault v3.0 - Private", "tier": "$2M Enterprise"}
