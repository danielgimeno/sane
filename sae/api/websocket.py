import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from sae.models.canvas import Canvas
from sae.simulation.engine import SimulationEngine

ws_router = APIRouter()


class SimulationSession:
    def __init__(self) -> None:
        self.engine: SimulationEngine | None = None
        self.task: asyncio.Task | None = None


sessions: dict[str, SimulationSession] = {}


@ws_router.websocket("/ws/simulation")
async def simulation_ws(websocket: WebSocket):
    await websocket.accept()
    session_id = id(websocket)
    session = SimulationSession()
    sessions[session_id] = session

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            action = msg.get("action")

            if action == "start":
                canvas = Canvas(**msg["canvas"])
                duration = msg.get("duration", 30.0)
                speed = msg.get("speed", 1.0)

                if session.task and not session.task.done():
                    session.task.cancel()

                session.engine = SimulationEngine(canvas)
                session.engine.start(duration=duration, speed=speed)

                async def run_sim():
                    while session.engine and session.engine.is_running:
                        metrics = session.engine.step(dt=0.1)
                        await websocket.send_json({
                            "type": "metrics",
                            "data": metrics.model_dump(),
                        })
                        await asyncio.sleep(0.1)

                    if session.engine:
                        await websocket.send_json({
                            "type": "finished",
                            "data": session.engine.metrics.model_dump(),
                        })

                session.task = asyncio.create_task(run_sim())

            elif action == "stop":
                if session.engine:
                    session.engine.stop()
                if session.task and not session.task.done():
                    session.task.cancel()
                await websocket.send_json({"type": "stopped"})

            elif action == "step":
                if session.engine:
                    metrics = session.engine.step(dt=msg.get("dt", 0.5))
                    await websocket.send_json({
                        "type": "metrics",
                        "data": metrics.model_dump(),
                    })

    except WebSocketDisconnect:
        pass
    finally:
        if session.task and not session.task.done():
            session.task.cancel()
        sessions.pop(session_id, None)
