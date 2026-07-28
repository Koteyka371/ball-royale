import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, id=1, team="red", x=0, y=0, hp=100):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100
        self.speed = 5.0
        self.is_decoy = False
        self.decoy_type = ""
        self.alive = True
        self.silence_timer = 0.0
        self.decoy_timer = 5.0

    def take_damage(self, amount):
        self.hp -= amount

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __contains__(self, key):
        return hasattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)

def test_emp_decoy_explosion():
    world = MockWorld()
    decoy = MockBall(id=2, team="red", x=0, y=0, hp=0)
    decoy.is_decoy = True
    decoy.decoy_type = "emp_decoy"
    decoy.owner_id = 1

    enemy = MockBall(id=3, team="blue", x=10, y=0, hp=100)

    world.balls = [decoy, enemy]

    action = Action(decoy, world)
    action.execute("idle", 0.016)

    assert enemy.silence_timer == 3.0

def test_emp_decoy_max_silence():
    world = MockWorld()
    decoy = MockBall(id=2, team="red", x=0, y=0, hp=0)
    decoy.is_decoy = True
    decoy.decoy_type = "emp_decoy"
    decoy.owner_id = 1

    enemy = MockBall(id=3, team="blue", x=10, y=0, hp=100)
    enemy.silence_timer = 5.0 # Should keep max

    world.balls = [decoy, enemy]

    action = Action(decoy, world)
    action.execute("idle", 0.016)

    assert enemy.silence_timer == 5.0
