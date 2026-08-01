import pytest
from ai.game_modes import MoltenGolemMode
from ai.test_game_modes import MockBall

class MockArena:
    def __init__(self):
        self.hazards = []
        self.projectiles = []
        self.items = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.next_id = 100
        self.events = []
        self.is_test = True

def test_molten_golem_mode_spawn():
    mode = MoltenGolemMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    world.arena.weather = "heatwave"
    balls[0].ball_type = "juggernaut"
    balls[0].speed = 100.0

    mode.setup(world, balls)

    # Tick for 5 seconds to spawn
    mode.tick(world, balls, delta=5.1)

    assert len(balls) == 2
    golem = balls[1]
    assert getattr(golem, "ball_type", "") == "molten_golem"
    assert getattr(golem, "hp", 0) == 2000.0

def test_molten_golem_mode_death_and_drops():
    mode = MoltenGolemMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    world.arena.weather = "heatwave"
    balls[0].ball_type = "juggernaut"
    balls[0].speed = 100.0

    mode.setup(world, balls)
    mode.tick(world, balls, delta=5.1)

    golem = balls[1]
    golem.hp = 0  # Kill the golem

    mode.tick(world, balls, delta=0.1)

    # Golem should be removed
    assert len(balls) == 1

    # Check lava puddles
    lavas = [h for h in world.arena.hazards if getattr(h, "kind", "") == "lava_puddle"]
    assert len(lavas) == 4

    # Check fire core item
    cores = [i for i in world.arena.items if i.get("kind") == "booster" and i.get("booster_type") == "fire_core"]
    assert len(cores) == 1
