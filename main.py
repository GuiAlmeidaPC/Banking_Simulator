from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Banking Simulator API")

app.include_router(router)

# Run the app with: uvicorn main:app --reload