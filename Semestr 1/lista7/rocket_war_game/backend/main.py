"""
Tutaj uruchamiamy serwer. 
Z konsoli: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from connection_manager import ConnectionManager
from game_state import GameState

# Konfiguracja loopa gry
TICK_RATE = 30
DELTA_TIME = 1.0 / TICK_RATE

app = FastAPI()
manager = ConnectionManager()
game_state = GameState()

@app.websocket("/ws/{player_id}")
async def game_ws(websocket: WebSocket, player_id: str):
    """
    Każdy gracz łączy się np (ws://localhost:8000/ws/player1)
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "fire":
                angle = data.get("angle", 45)
                power = data.get("power", 50)
                game_state.fire_rocket(player_id, angle, power)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

async def game_loop():
    """
    Główna pętla gry: co klatkę aktualizuje stan
    i wysyła go do wszystkich podłączonych klientów.
    """
    while True:
        game_state.update(DELTA_TIME)
        current_state = game_state.get_state()
        await manager.broadcast(current_state)
        await asyncio.sleep(DELTA_TIME)

@app.on_event("startup")
async def on_startup():
    """Uruchamia pętlę gry przy starcie serwera."""
    asyncio.create_task(game_loop())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
