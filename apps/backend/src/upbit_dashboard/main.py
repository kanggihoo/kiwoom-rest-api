from fastapi import FastAPI

app = FastAPI(title="Upbit Dashboard API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "upbit-dashboard-backend"}
