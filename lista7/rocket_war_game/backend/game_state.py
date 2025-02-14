"""
Klasa przechowująca informacje o stanie gry oraz zmieniająca go
"""
import math
import uuid

from vector2 import Vector2
from rocket import Rocket
from collision import detect_collisions

# Stałe offset bazy + grawitacja
BASE_OFFSET = 300
GRAVITY = 40

class GameState:
    def __init__(self):
        # Położenia baz 
        self.base_positions = {
            "player1": Vector2(BASE_OFFSET, 0),
            "player2": Vector2(-BASE_OFFSET, 0),
        }
        # Punkty życia baz
        self.base_hp = {
            "player1": 100,
            "player2": 100,
        }
        # Zbiór rakiet na planszy w postaci {rocket_id: Rocket()}
        self.rockets = {}

    def update(self, dt):
        """Aktualizacja ruchu i kolizji."""
        # Zmiana pozycji rakiety
        for rocket in self.rockets.values():
            rocket.move(dt, GRAVITY)

        # Sprawdzenie kolizji
        to_remove = detect_collisions(self)

        # Usunięcie rakiet w kolizji
        for rid in to_remove:
            if rid in self.rockets:
                del self.rockets[rid]

    def fire_rocket(self, player_id: str, angle_deg: float, power: float):
        """Tworzy nową rakietę z lekkim offsetem od bazy."""
        base_pos = self.base_positions[player_id]
        angle_rad = math.radians(angle_deg)
        direction = Vector2(math.cos(angle_rad), math.sin(angle_rad))

        # Offset, by rakieta startowała obok bazy (Aby uniknąć instant kolizji)
        start_offset = 10
        start_pos = base_pos + (direction * start_offset)
        velocity = direction * power

        rocket_id = str(uuid.uuid4())
        new_rocket = Rocket(rocket_id, start_pos, velocity, player_id)
        self.rockets[rocket_id] = new_rocket

    def get_state(self):
        """Zwraca stan gry w JSON'ie."""
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
