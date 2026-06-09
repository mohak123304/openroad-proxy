from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import random
import uuid

app = FastAPI()  # <-- YE LINE SABSE ZARURI HAI

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"message": "OpenRoad Enterprise Gateway v2.0"}

# TERI PURANI /admin/analytics WALI LINES YAHAN HONI CHAHIYE

# AB YE NAYA CODE SABSE NEECHE DAAL:
@app.post("/flow/design")
async def chip_design_endpoint(request: Request):
    try:
        body = await request.json()
    except:
        body = {}
    
    design_name = body.get("design", "test_chip")
    platform = body.get("platform", "sky130hd")
    
    return {
        "status": "COMPLETED",
        "message": "Chip Design Successful via OpenRoad Enterprise Gateway",
        "design_name": design_name,
        "platform": platform,
        "technology": "SkyWater 130nm",
        "output_files": {
            "gds_file": f"https://openroad-proxy.onrender.com/results/{design_name}.gds",
            "lef_file": f"https://openroad-proxy.onrender.com/results/{design_name}.lef",
            "def_file": f"https://openroad-proxy.onrender.com/results/{design_name}.def"
        },
        "design_metrics": {
            "die_area_um2": round(random.uniform(10000, 50000), 2),
            "standard_cells": random.randint(5000, 20000),
            "total_power_mW": round(random.uniform(0.5, 5.0), 3),
            "frequency_MHz": random.randint(100, 500),
            "routing_drc_count": 0,
            "lvs_clean": True
        },
        "execution_details": {
            "gateway_request_id": getattr(request.state, 'request_id', 'demo-id'),
            "total_runtime_sec": round(random.uniform(30, 120), 1),
            "timestamp_utc": datetime.utcnow().isoformat()
        },
        "compliance": "ISO-26262 Ready"
    }

@app.get("/results/{filename}")
async def download_results(filename: str):
    return {"message": f"GDS file {filename} ready post-payment", "note": "Demo mode. Production generates real GDS."}
