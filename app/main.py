from fastapi import FastAPI

app = FastAPI(title="E-commerce AI Agent")


@app.get("/health")
def health():
    return {"status": "ok"}