from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, engine
from .routers import admin, events


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="CardRadar Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(events.router, prefix=settings.api_prefix)
    app.include_router(admin.router, prefix=settings.api_prefix)

    return app


Base.metadata.create_all(bind=engine)
app = create_app()

