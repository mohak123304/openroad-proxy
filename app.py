from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root(): 
    return {"status": "Railway OK"}

@app.get("/health")
def health():
    return {"status": "Proxy OK"}  # Codespace call hata diya yaha se
