from ai.game_modes import GameMode
from ai.action import Action
import math

class MockArena:
    def __init__(self, name="water_park", width=1000, height=1000):
        self.name = name
        self.width = width
        self.height = height
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.whirlpool_spawn_timer = 0.1 # trigger next tick

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id=1, x=500, y=500):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "basic"
        self.base_speed = 100.0
        self.speed = 100.0
        self.hp = 100.0

def test_whirlpool_spawns_and_pulls():
    mode = GameMode()
    world = MockWorld()
    b = MockBall(x=500, y=500)
    balls = [b]

    # Tick 1: trigger spawn
    mode.tick(world, balls, delta=0.2)
    assert len(world.arena.hazards) > 0
    whirlpool = world.arena.hazards[-1]
    assert getattr(whirlpool, "kind", "") == "whirlpool"

    # Tick 2: get pulled
    b.x = whirlpool.x + 50.0
    b.y = whirlpool.y
    initial_x = b.x
    mode.tick(world, balls, delta=0.1)

    assert b.x < initial_x # Pulled towards center (which is smaller x)
    assert b.speed < 100.0 # Slowed down

    # Tick 3: submerge
    b.x = whirlpool.x + 10.0
    mode.tick(world, balls, delta=0.1)
    assert getattr(b, "is_submerged", False) == True

    # Tick 4: resurface
    b.submerge_timer = 0.05
    mode.tick(world, balls, delta=0.1)
    assert getattr(b, "is_submerged", False) == False
    assert b.hp < 100.0
    assert getattr(b, "wet_debuff_timer", 0.0) > 0.0
    assert getattr(b, "defense_multiplier", 1.0) > 1.0

if __name__ == "__main__":
    test_whirlpool_spawns_and_pulls()
    print("Whirlpool test passed")
