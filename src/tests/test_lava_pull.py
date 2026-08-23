import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100
        self.speed = 100.0
        self.base_speed = 100.0
        self.vx = 0.0
        self.vy = 0.0

class MockHazard:
    def __init__(self, kind, x, y):
        self.id = 999
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 50.0
        self.damage = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self, arena):
        self.arena = arena
        self.game_mode = None
        self.events = []
        self.balls = []

def test_lava_pull():
    ball = MockBall(1, 20.0, 0.0) # Outside center, inside radius
    arena = MockArena()
    world = MockWorld(arena)
    world.balls.append(ball)
    hazard = MockHazard("lava_pool", 0.0, 0.0)
    arena.hazards.append(hazard)

    action = Action(ball, world)

    initial_x = ball.x
    action.execute("idle", 0.1)

    print(f"Ball x after lava_pool: {ball.x}")
    assert getattr(ball, "is_in_lava", False) == True
    assert ball.x < initial_x # Pulled towards center

if __name__ == "__main__":
    test_lava_pull()
