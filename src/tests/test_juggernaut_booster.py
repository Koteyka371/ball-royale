import pytest
from ai.action import Action

class DummyArena:
    def __init__(self, hazards):
        self.hazards = hazards

class DummyWorld:
    def __init__(self, boosters):
        self.boosters = boosters
        self.arena = DummyArena(hazards=boosters)

class DummyBall:
    def __init__(self):
        self.x, self.y = 10, 10
        self.radius = 10.0
        self.base_radius = 10.0
        self.mass = 1.0
        self.base_mass = 1.0
        self.speed = 5.0
        self.base_speed = 5.0
        self._base_speed_set = True # PREVENTS overriding base_speed during first tick
        self.hp = 100
        self.max_hp = 100

class DummyBooster:
    def __init__(self):
        self.x, self.y = 10, 10
        self.kind = "juggernaut_booster"
        self.mutated_env = None

    def get(self, key, default=None):
        return getattr(self, key, default)

def test_juggernaut_booster_collection_and_tick():
    ball = DummyBall()
    booster = DummyBooster()
    world = DummyWorld([booster])
    action = Action(ball, world)

    # Patch get_boosters/enemies
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []

    # Collect
    action._collect_booster(0.1)

    assert getattr(ball, "juggernaut_booster_timer", 0.0) == 15.0
    assert len(world.boosters) == 0

    # Tick
    action.execute("idle", 0.1)
    assert ball.radius == 20.0
    assert ball.mass == 5.0
    assert ball.hp == 600
    assert ball.speed == 2.5

    # Expire
    ball.juggernaut_booster_timer = 0.001
    action.execute("idle", 0.1)
    assert ball.radius == 10.0
    assert ball.mass == 1.0
    assert ball.hp == 100 # Capped at max_hp which returned to 100
    assert ball.speed == 5.0
