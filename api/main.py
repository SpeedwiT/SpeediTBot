"""ماژول اصلی API - FastAPI"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api.routers import (
    users_router, products_router, orders_router,
    panels_router, transactions_router, cards_router, vps_router,
)

app = FastAPI(
    title="ProxiMan API",
    description="API for ProxiMan Telegram Bot & Mini App",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(users_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(panels_router)
app.include_router(transactions_router)
app.include_router(cards_router)
app.include_router(vps_router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "ProxiMan API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Serve Mini App
WEBAPP_DIR = Path(__file__).parent.parent / "webapp"


@app.get("/miniapp")
async def serve_miniapp():
    return FileResponse(str(WEBAPP_DIR / "index.html"))


@app.get("/miniapp/{path:path}")
async def serve_static(path: str):
    file_path = WEBAPP_DIR / path
    if file_path.exists():
        return FileResponse(str(file_path))
    return FileResponse(str(WEBAPP_DIR / "index.html"))


# Mount static files for Mini App
try:
    app.mount("/static", StaticFiles(directory=str(WEBAPP_DIR)), name="static")
except Exception:
    pass
