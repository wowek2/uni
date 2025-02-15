"""
Plik odpowiedzialny za wykrywanie kolizji i modyfikację stanu gry
"""
from vector2 import Vector2

#Stałe promienie po przekroczeniu, których zaliczamy uderzenie
BASE_COLLISION_RADIUS = 10  
ROCKET_COLLISION_RADIUS = 8
PLANET_RADIUS = 290

def detect_collisions(game_state):
    """
    Sprawdza kolizje: 
    -> rakieta-planeta, 
    -> rakieta-baza, 
    -> rakieta-rakieta
    Zwraca zbiór ID rakiet do usunięcia.
    Modyfikuje HP baz w przypadku trafienia w bazę.
    """
    # Zbiór rakiet do usunięcia
    to_remove = set()

    # Kolizja rakieta-planeta
    for rid, rocket in list(game_state.rockets.items()):
        if rocket.get_distance_to_point(Vector2(0, 0)) <= PLANET_RADIUS:
            to_remove.add(rid)

    # Kolizja rakieta-baza
    for rid, rocket in list(game_state.rockets.items()):
        if rid in to_remove:
            continue
        for pid, base_pos in game_state.base_positions.items():
            dist_base = rocket.get_distance_to_point(base_pos)
            if dist_base < BASE_COLLISION_RADIUS:
                to_remove.add(rid)
                game_state.base_hp[pid] -= 10
                break  # Jeśli rakieta uderzy w bazę gracza, koniec sprawdzania

    # Kolizja rakieta-rakieta
    rocket_ids = list(game_state.rockets.keys())
    for i in range(len(rocket_ids)):
        for j in range(i + 1, len(rocket_ids)):
            r1_id = rocket_ids[i]
            r2_id = rocket_ids[j]
            # Jeśli któraś jest już do usunięcia, pomijamy
            if r1_id in to_remove or r2_id in to_remove:
                continue

            r1 = game_state.rockets[r1_id]
            r2 = game_state.rockets[r2_id]
            if r1.get_distance_to_point(r2.pos) < ROCKET_COLLISION_RADIUS:
                to_remove.add(r1_id)
                to_remove.add(r2_id)

    return to_remove
