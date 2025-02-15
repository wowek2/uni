from dataclasses import dataclass
import numpy as np
from itertools import combinations
from enum import Enum
import math


@dataclass
class Object:
    """A class representing a physical object."""
    coordinates: np.ndarray
    velocity: np.ndarray
    force: np.ndarray = 0
    mass: float = 0

    
    def __post_init__(self):
        for (name, field_type) in self.__annotations__.items():
            value = self.__dict__[name]

            if type(value) != field_type and not(not field_type == type((int,float)) or value.isdigit()):    # Jeśli typy są różne i jeśli oczekiwany typ jest liczbą to typ wpisany też musi być liczbą 
                raise TypeError(f'The {name} field should be a: {field_type}. Instead of: {type(value)}')

            if field_type is np.ndarray:
                if len(value) != 2:
                    raise ValueError(f'The {name} array should have 2 elements.')

@dataclass
class Sphere(Object):
    radius: float = 0


@dataclass
class Rectangle(Object):
    height: float = 0

@dataclass 
class CollisionPoints():
    a: np.ndarray       # Furthest point of A into B
    b: np.ndarray       # Furthest point of B into A
    normal: np.ndarray  # B - A vector normalized
    distance: float     # B - A


@dataclass
class Collision():
    obj1: Object
    obj2: Object
    collision_points: CollisionPoints

class CollisionSolver():
    def resolve_elastic():
        pass
    
@dataclass 
class CollisionPoints():
    a: np.ndarray       # Furthest point of A into B
    b: np.ndarray       # Furthest point of B into A
    normal: np.ndarray  # B - A vector normalized
    distance: float     # B - A

def test_circle_circle(a,b):
    dist = np.linalg.norm(a.coordinates - b.coordinates)
    if dist <= a.radius + b.radius:
        # Calculate distance between centers
        d = np.linalg.norm(a.coordinates - b.coordinates)

        # normalized vector (From B to A)
        unit_vector = (a.coordinates - b.coordinates) / d

        # Furthest point of A into B
        furthest_A = a.coordinates - (a.radius * unit_vector)

        # Furthest point of B into A
        furthest_B = b.coordinates + (b.radius * unit_vector)

        # Distance B - A
        dist_B_A = np.linalg.norm(furthest_B - furthest_A)

        # Distance B - A normalized
        dist_B_A_normalized = (furthest_A - furthest_B) / dist_B_A
        

        coll_points = CollisionPoints(furthest_A, furthest_B, dist_B_A_normalized, dist_B_A)
        return Collision(a,b, coll_points)
    
def test_circle_rectangle(a,b):
    pass

collision_handlers = {}

def add_collision_handler(type1, type2, handler):
    collision_handlers[(type1, type2)] = handler
    collision_handlers[(type2, type1)] = handler

add_collision_handler(Sphere, Sphere, test_circle_circle)
add_collision_handler(Sphere, Rectangle, test_circle_rectangle)


def check_collision(obj1, obj2):
    obj1_type = type(obj1)
    obj2_type = type(obj2)

    handler = collision_handlers.get((obj1_type, obj2_type))
    if handler:
        return handler(obj1, obj2)
    return False

class PhysicSimulation:
    """A class representing the physics simulation."""
    GRAVITY_FORCE = 0
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        """Add object to the simulation."""
        self.objects.append(obj)

    def remove_object(self, obj):
        """Remove object from the simulation."""
        self.objects.remove(obj)

    def step(self, dt):
        for obj in self.objects:
            obj.force = np.array([0,1]) * self.GRAVITY_FORCE * obj.mass     # Apply the force F = g*m
            obj.velocity = obj.velocity + (obj.force / obj.mass) * dt       # Calculate velocity v = (F/m) * t
            obj.coordinates = obj.coordinates + obj.velocity * dt           # Calculate new position pos x = v*t  
            obj.force.fill(0)                                               # Set force vector working on object to (0,0)

    
    def resolve_collision(self, dt):
        collisions = list(map(lambda pair: check_collision(*pair), combinations(self.objects, 2)))
        for c in collisions:
            if c is not None:
                m_1 = c.obj1.mass
                m_2 = c.obj2.mass
                v_1 = c.obj1.velocity
                v_2 = c.obj2.velocity

                cor_1 = c.obj1.coordinates
                cor_2 = c.obj2.coordinates
                r_1 = c.obj1.radius
                r_2 = c.obj2.radius
                    
                # Wektor normalny
                normal = v_2 - v_1
                # Wektor jednostkowy normalny
                normal_unit = normal / np.linalg.norm(normal)

                c.obj1.coordinates += np.array(normal_unit * c.collision_points.distance)
                
                # Wektor styczny (prostopadły do normalnego)
                tangent_unit = np.array([-normal_unit[1], normal_unit[0]])


                v1_normal = np.dot(v_1, normal_unit)
                v1_tangent = np.dot(v_1, tangent_unit)

                v2_normal = np.dot(v_2, normal_unit) 
                v2_tangent = np.dot(v_2, tangent_unit) 

                v1_normal_final = ((m_1 - m_2) * v1_normal + 2 * m_2 * v2_normal) / (m_1 + m_2)
                v2_normal_final = ((m_2 - m_1) * v2_normal + 2 * m_1 * v1_normal) / (m_1 + m_2)

                # Rekonstrukcja końcowych wektorów prędkości
                v1_final = v1_normal_final * normal_unit + v1_tangent * tangent_unit
                v2_final = v2_normal_final * normal_unit + v2_tangent * tangent_unit
                    
                c.obj1.velocity = v1_final
                c.obj2.velocity = v2_final

        

