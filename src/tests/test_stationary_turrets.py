import pytest
from ai.game_modes import StationaryTurretsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, id_val, x, y, team=""):
        self.id = id_val
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0

    def take_damage(self, amount):
        self.hp = max(0.0, self.hp - amount)

def test_stationary_turrets_explode_on_destruction():
    mode = StationaryTurretsMode()
    world = MockWorld()

    # Spawn a turret manually to test interaction
    mode.spawn_timer = 20.0
    mode.tick(world, [], 0.1)

    assert len(mode.turrets) == 1
    t = mode.turrets[0]
    t.x = 500
    t.y = 500

    b1 = MockBall(1, 500, 500)
    b2 = MockBall(2, 700, 700) # Far away
    balls = [b1, b2]

    # Destroy the turret
    t.hp = 0.0

    # Tick should process explosion
    mode.tick(world, balls, 0.1)

    assert len(mode.turrets) == 0, "Turret should be removed"
    assert b1.hp == 50.0, "Ball close to turret should take 50 explosion damage"
    assert b2.hp == 100.0, "Ball far from turret should take 0 damage"

    assert any(e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "explosion" for e in world.events)
