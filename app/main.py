from fastapi import FastAPI

from api.routes.health import router as health_router

app = FastAPI(title="RAG Agent")
app.include_router(health_router)
