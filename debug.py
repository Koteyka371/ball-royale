import math

class DummyHazard:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

d = DummyHazard(500, 500, 120)
print(d.x)
