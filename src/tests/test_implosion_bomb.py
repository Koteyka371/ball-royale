import pytest
from ai.game_modes import ImplosionBombEventMode

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "warrior"
        self.team = "red"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

def test_implosion_bomb_spawn_and_pull():
    world = MockWorld()
    mode = ImplosionBombEventMode()
    balls = [MockBall(1, 500, 500)]

    # Fast forward to spawn
    mode.event_timer = 20.0
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    bomb = world.arena.hazards[0]
    assert getattr(bomb, "kind", "") == "implosion_bomb"
    assert getattr(bomb, "duration", 0) == 9.9

    # Check if pulled
    bomb.x = 800
    bomb.y = 500

    mode.tick(world, balls, 0.1)

    assert balls[0].vx > 0
    assert balls[0].x > 500

def test_implosion_bomb_explode():
    world = MockWorld()
    mode = ImplosionBombEventMode()
    balls = [MockBall(1, 500, 500)]

    # Fast forward to spawn
    mode.event_timer = 20.0
    mode.tick(world, balls, 0.1)

    bomb = world.arena.hazards[0]
    bomb.x = 500
    bomb.y = 500

    bomb.duration = 0.0

    mode.tick(world, balls, 0.1)

    # Explode and check if pushed
    assert len(world.arena.hazards) == 0
    assert len(world.events) == 2 # spawn and explode
    assert any(e["type"] == "visual_effect" and e["data"].get("type") == "implosion_bomb_explosion" for e in world.events)

    assert balls[0].hp < 100.0
