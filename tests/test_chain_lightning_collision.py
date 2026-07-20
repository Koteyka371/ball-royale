import math
from dataclasses import dataclass
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = None
        self.balls = []

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [b for b in self.balls if b != entity and getattr(b, "team", None) != getattr(entity, "team", None)],
                "allies": [b for b in self.balls if b != entity and getattr(b, "team", None) == getattr(entity, "team", None)]}

class MockBall:
    def __init__(self, id, x, y, hp=100.0, team="", ball_type="basic", radius=10.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.radius = radius
        self.damage = 10.0

def test_chain_lightning_collision():
    world = MockWorld()
    # Intersecting balls to trigger collision
    b1 = MockBall(1, 100, 100, team="A")
    b1.chain_lightning_timer = 5.0
    b2 = MockBall(2, 110, 100, team="B")
    b3 = MockBall(3, 160, 100, team="B") # within 200 of b2
    b4 = MockBall(4, 210, 100, team="B") # within 200 of b3
    b5 = MockBall(5, 500, 500, team="B") # out of range

    world.balls = [b1, b2, b3, b4, b5]

    action = Action(b1, world)
    action._spawn_directed_particles = lambda s, t, kind: None
    action._resolve_collisions()

    assert b1._cl_collision_cd == 0.5
    # b2 gets hit by collision chain: damage = 3.5
    assert b2.hp == 96.5
    # b3 gets chained from b2: damage = 3.5
    assert b3.hp == 96.5
    # b4 gets chained from b3: damage = 3.5
    assert b4.hp == 96.5
    # b5 is too far
    assert b5.hp == 100.0
