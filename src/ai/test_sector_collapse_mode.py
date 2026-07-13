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
    # Move them far away from center to avoid random wall spawning on them during the time skip
    b1.x = 10.0
    b1.y = 10.0
    b2.x = 10.0
    b2.y = 10.0
    balls = [b1, b2]

    mode.setup(world, balls)

    # Tick 11 seconds to trigger wall spawn
    mode.tick(world, balls, 11.0)

    assert len(mode.walls) == 1
    assert len(world.events) == 1
    assert world.events[0][0] == "wall_spawn"

    # Reset HP and Alive in case outside-zone damage killed them during the 11s tick
    b1.hp = 100.0
    b1.alive = True

    # Move ball into wall intentionally to test wall damage
    wall = mode.walls[0]
    b1.x = wall["x"] + 1.0
    b1.y = wall["y"] + 1.0

    initial_hp = b1.hp
    # A small delta to test damage correctly without sending HP to -1000
    mode.tick(world, balls, 0.1)

    assert b1.hp < initial_hp
