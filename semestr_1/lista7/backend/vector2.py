"""
Klasa reprezentująca ektor dwuwymiarowy z podstawowymi operacjami
"""
import math

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
    
    def __repr__(self):
        """Returns representation of a Vector2D object"""
        return f'({self.x}, {self.y})'
    
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + self.other.y)
    
    def __iadd__(self,other):
        self.x += other.x
        self.y += other.y
        return self
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __mul__(self, number: float):
        return Vector2(self.x * number, self.y * number)
    
    def __getitem__(self, index: int):
        if index == 0:
            return self.x
        if index == 1:
            return self.y
        return IndexError("I'm soory to disapoint you but the index is out of range :(")
    
    def __len__(self):
        return 2
    
    def copy(self):
        return Vector2(self.x, self.y)
