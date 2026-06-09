from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"message": "OpenRoad Proxy Live on Render"}

@app.get("/health")
def health():
    return {"status": "OK"}
