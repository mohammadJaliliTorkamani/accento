from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import detection, health
from app.core.database import create_indexes

app = FastAPI(title="Accento")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detection.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup():

    await create_indexes()