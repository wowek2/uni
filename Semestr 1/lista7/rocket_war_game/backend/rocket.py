"""
Klasa przechowująca dane o rakiecie i metody z nią związane
"""
from vector2 import Vector2

class Rocket:
    def __init__(self, rocket_id, position: Vector2, velocity: Vector2, owner_id: str):
        self.id = rocket_id
        self.pos = position
        self.vel = velocity
        self.owner_id = owner_id

    def get_position(self):
        """Zwraca pozycję rakiety jako krotkę (x, y)."""
        return (self.pos.x, self.pos.y)

    def get_distance_to_point(self, point: Vector2) -> float:
        """Zwraca dystans rakiety do innego punktu (Vector2)."""
        return (self.pos - point).length()

    def move(self, dt: float, gravity: float):
        """
        Aktualizuje prędkość i pozycję rakiety w oparciu o grawitację
        skierowaną do środka układu (0,0).
        """
        center_vec = Vector2(0, 0) - self.pos
        dist = center_vec.length()
        accel_dir = center_vec.normalize() if dist > 0 else Vector2()
        accel = accel_dir * gravity

        # Zmiana wektora prędkości i położenia
        self.vel = self.vel + (accel * dt)
        self.pos = self.pos + (self.vel * dt)
