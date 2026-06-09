from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Railway is running"}

@app.get("/health")
def health_check():
    return {"status": "OK"}  # Codespace ko call mat kar yaha
