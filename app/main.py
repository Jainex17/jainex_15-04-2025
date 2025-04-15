from fastapi import FastAPI
from app.api.routes import router
from app.api.tasks import calculate_report

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is running"}

app.include_router(router, prefix="/api")
