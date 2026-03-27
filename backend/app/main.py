from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import Base, engine
from app.routes.api import router as api_router
from app.routes.dev2_routes import router as dev2_router

try:
    with engine.connect() as conn:
        pass
except Exception:
    pass

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ET Money Mentor API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(dev2_router)

