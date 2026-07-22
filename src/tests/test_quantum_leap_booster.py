import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id, hp, max_hp, is_decoy=False, owner_id=None):
        self.id = id
        self.hp = hp
        self.max_hp = max_hp
        self.alive = True
        self.is_decoy = is_decoy
        self.owner_id = owner_id
        self.x = 0.0
        self.y = 0.0
        self.quantum_leap_active = False

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockHazard:
    def __init__(self, kind, owner_id):
        self.kind = kind
        self.owner_id = owner_id
        self.x = 0.0
        self.y = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []

def test_quantum_leap_decoy():
    ball = MockBall(id=1, hp=100, max_hp=100)
    ball.quantum_leap_active = True
    ball.x, ball.y = 10, 10

    decoy = MockBall(id=2, hp=1, max_hp=1, is_decoy=True, owner_id=1)
    decoy.x, decoy.y = 50, 50

    world = MockWorld()
    world.balls.extend([ball, decoy])
    action = Action(ball, world)

    # Take lethal damage
    ball.take_damage(90) # Now at 10 HP, which is <= 20%

    ball.vx = 0
    ball.vy = 0
    ball.speed = 0

    action.execute("idle", 0.0) # Delta 0 to prevent physics movement

    # Should have teleported to decoy and consumed it
    assert ball.x == 50
    assert ball.y == 50
    assert not decoy.alive
    assert not ball.quantum_leap_active
    assert ball.hp == 20 # 20% of max_hp
