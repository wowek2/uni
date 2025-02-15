import uvicorn
import asyncio
import math
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# -------------------------
# KONFIGURACJA
# -------------------------
TICK_RATE = 30
DELTA_TIME = 1.0 / TICK_RATE

PLANET_RADIUS = 290          # Promień planety
BASE_OFFSET = 300            # Pozycja baz 
BASE_COLLISION_RADIUS = 10
ROCKET_COLLISION_RADIUS = 8
GRAVITY = 40                 # Przyspieszenie grawitacyjne (ku środkowi)

# -------------------------
# KLASY POMOCNICZE
# -------------------------
class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        l = self.length()
        if l > 0:
            return Vector2(self.x / l, self.y / l)
        return Vector2()

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float):
        return Vector2(self.x * scalar, self.y * scalar)

    def copy(self):
        return Vector2(self.x, self.y)


class Rocket:
    def __init__(self, rocket_id, position: Vector2, velocity: Vector2, owner_id: str):
        self.id = rocket_id
        self.pos = position     # Vector2
        self.vel = velocity     # Vector2
        self.owner_id = owner_id  # "player1" / "player2"

    def get_position(self):
        """Zwraca pozycję rakiety w postaci krotki (x, y)."""
        return (self.pos.x, self.pos.y)

    def get_distance_to_point(self, point: Vector2) -> float:
        """Zwraca dystans rakiety do innego punktu (Vector2)."""
        return (self.pos - point).length()

    def move(self, dt: float, gravity: float):
        """
        Aktualizuje prędkość i pozycję rakiety w oparciu o grawitację
        skierowaną do środka układu współrzędnych (0,0).
        """
        center_vec = Vector2(0, 0) - self.pos
        dist = center_vec.length()
        accel_dir = center_vec.normalize() if dist > 0 else Vector2()
        accel = accel_dir * gravity

        # Zmieniamy prędkość i pozycję
        self.vel = self.vel + (accel * dt)
        self.pos = self.pos + (self.vel * dt)


# -------------------------
# GŁÓWNA LOGIKA GRY
# -------------------------
class GameState:
    def __init__(self):
        # Bazy graczy naprzeciw siebie
        self.base_positions = {
            "player1": Vector2(BASE_OFFSET, 0),   # (300, 0)
            "player2": Vector2(-BASE_OFFSET, 0),  # (-300, 0)
        }
        self.base_hp = {
            "player1": 100,
            "player2": 100,
        }
        self.planet_radius = PLANET_RADIUS
        self.rockets = {}  # { rocket_id: Rocket }

    def update(self, dt):
        """Aktualizuje położenia rakiet i wykrywa kolizje."""
        to_remove = []

        # Ruch rakiet (grawitacja)
        for rocket in self.rockets.values():
            rocket.move(dt, GRAVITY)

        # Kolizja rakieta-planeta
        for rid, rocket in list(self.rockets.items()):
            if rocket.get_distance_to_point(Vector2(0, 0)) <= self.planet_radius:
                to_remove.append(rid)

        # Kolizja rakieta-baza
        for rid, rocket in list(self.rockets.items()):
            if rid in to_remove:
                # Jeśli już oznaczony do usunięcia, nie sprawdzamy dalej
                continue
            for pid, base_pos in self.base_positions.items():
                dist_base = rocket.get_distance_to_point(base_pos)
                if dist_base < BASE_COLLISION_RADIUS:
                    to_remove.append(rid)
                    self.base_hp[pid] -= 10
                    break  # Nie ma sensu sprawdzać drugiej bazy

        # Kolizja rakieta-rakieta
        rocket_ids = list(self.rockets.keys())
        for i in range(len(rocket_ids)):
            for j in range(i + 1, len(rocket_ids)):
                r1_id = rocket_ids[i]
                r2_id = rocket_ids[j]
                if r1_id in to_remove or r2_id in to_remove:
                    continue

                r1 = self.rockets[r1_id]
                r2 = self.rockets[r2_id]
                if r1.get_distance_to_point(r2.pos) < ROCKET_COLLISION_RADIUS:
                    to_remove.append(r1_id)
                    to_remove.append(r2_id)

        # Usunięcie z gry rakiet z listy "to_remove"
        for rid in set(to_remove):
            if rid in self.rockets:
                del self.rockets[rid]

    def fire_rocket(self, player_id, angle_deg, power):
        """Tworzy nową rakietę z lekkim offsetem od bazy."""
        base_pos = self.base_positions[player_id]
        angle_rad = math.radians(angle_deg)
        direction = Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Przesunięcie startu rakiety o 10 px w kierunku strzału
        start_offset = 10
        start_pos = base_pos + (direction * start_offset)
        velocity = direction * power

        rocket_id = str(uuid.uuid4())
        rocket = Rocket(rocket_id, start_pos, velocity, player_id)
        self.rockets[rocket_id] = rocket

    def get_state(self):
        """Zwraca stan gry w formacie JSON-owalnym."""
        rockets_data = []
        for r in self.rockets.values():
            rockets_data.append({
                "id": r.id,
                "pos": {"x": r.pos.x, "y": r.pos.y},
                "owner_id": r.owner_id,
            })
        return {
            "type": "state",
            "rockets": rockets_data,
            "baseHP": self.base_hp,
        }

# -------------------------
# ZARZĄDZANIE POŁĄCZENIAMI
# -------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)


# -------------------------
# FASTAPI - KONFIGURACJA
# -------------------------
app = FastAPI()
manager = ConnectionManager()
game_state = GameState()

@app.websocket("/ws/{player_id}")
async def game_ws(websocket: WebSocket, player_id: str):
    """
    Każdy gracz łączy się np. ws://localhost:8000/ws/player1
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
    """Pętla gry – co klatkę aktualizuje stan i rozsyła do klientów."""
    while True:
        game_state.update(DELTA_TIME)
        current_state = game_state.get_state()
        await manager.broadcast(current_state)
        await asyncio.sleep(DELTA_TIME)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(game_loop())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)