from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Railway is running"}

@app.get("/health")
def health():
    return {"status": "OK"}
