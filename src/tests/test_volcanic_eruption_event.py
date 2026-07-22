import pytest
from ai.game_modes import VolcanicEruptionEventMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20.0
        self.alive = True
        self.hp = 100.0

    def take_damage(self, damage):
        self.hp -= damage

def test_volcanic_eruption_logic():
    mode = VolcanicEruptionEventMode()
    world = MockWorld()
    ball = MockBall(500, 500)
    balls = [ball]

    mode.setup(world, balls)

    # Tick until eruption starts
    mode.eruption_timer = 9.9
    mode.tick(world, balls, delta=0.2)

    assert mode.is_erupting == True
    assert mode.projectiles_to_spawn == 15
    assert any(e[0] == "visual_effect" and e[1]["type"] == "volcano_warning" for e in world.events)

    world.events.clear()

    # Tick to spawn a projectile
    mode.tick(world, balls, delta=2.0) # Spawn rate is 2.0 / 15.0 ~ 0.133

    assert len(mode.lava_puddles) > 0
    assert len(world.arena.hazards) > 0
    assert any(e[0] == "visual_effect" and e[1]["type"] == "meteor_fall" for e in world.events)

    puddle = mode.lava_puddles[0]
    puddle.x = ball.x
    puddle.y = ball.y

    initial_hp = ball.hp
    mode.tick(world, balls, delta=1.0)

    # Check if damage is applied
    assert ball.hp < initial_hp

    # Check if puddle expires
    puddle.duration = 0.0
    mode.tick(world, balls, delta=0.1)

    assert puddle not in mode.lava_puddles
    assert puddle not in world.arena.hazards
