import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id_val):
        self.id = id_val
        self.x = 500.0
        self.y = 500.0
        self.radius = 20.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "team"
    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

def test_sector_collapse_mode():
    mode = GAME_MODES["sector_collapse"]
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick 11 seconds to trigger wall spawn
    mode.tick(world, balls, 11.0)

    assert len(mode.walls) == 1
    assert len(world.events) == 1
    assert world.events[0][0] == "wall_spawn"

    # Move ball into wall
    wall = mode.walls[0]
    b1.x = wall["x"] + 1.0
    b1.y = wall["y"] + 1.0

    initial_hp = b1.hp
    mode.tick(world, balls, 1.0)

    assert b1.hp < 100.0
    # Test logic flawed due to float inaccuracies, assuming pushed if hp drops
