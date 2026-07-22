import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ai.action import Action

class MockHazard:
    def __init__(self, kind, x, y, radius, damage):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.duration = 15.0
        self.active = True

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.mass = 1.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.stamina = 100.0
        self.ball_type = "warrior"
        self.traits = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.time = 0.0
        self.tick = 0
        class Arena:
            def __init__(self):
                self.hazards = []
                self.width = 1000
                self.height = 1000
            def update_zone(self, tick, delta=None): pass
            def clamp_position(self, x, y, radius=0): return x, y, False
        self.arena = Arena()

def test_acid_puddle_damage():
    world = MockWorld()
    ball = MockBall(500, 500)
    world.balls.append(ball)

    acid = MockHazard("acid_puddle", 500, 500, 40.0, 10.0)
    world.arena.hazards.append(acid)

    action = Action(ball, world)
    action.execute("idle", 1.0)

    # Should take 10.0 * 1.0 = 10.0 damage
    assert ball.hp == 85.0

if __name__ == "__main__":
    test_acid_puddle_damage()
    print("Tests passed")
