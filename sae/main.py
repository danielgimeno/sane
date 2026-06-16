from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from sae.api.routes import router
from sae.api.websocket import ws_router

app = FastAPI(
    title="SAE — Software Architecture Emulator",
    description="Emulador visual de arquitecturas de software con simulación de tráfico",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(ws_router)

frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


def run() -> None:
    uvicorn.run("sae.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
