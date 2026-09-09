import pytest
from ai.action import Action

class MockWorld:
    def __init__(self, balls=None, arena=None):
        self.balls = balls or []
        self.arena = arena
        self.events = []
        self.next_id = 1000

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, bid, x, y, is_decoy=False, element=None):
        self.id = bid
        self.x = x
        self.y = y
        self.is_decoy = is_decoy
        self.element = element
        self.hp = 100
        self.alive = True
        self.decoy_timer = 5.0
        self.owner_id = 1

def test_elemental_resonance():
    arena = MockArena()
    b1 = MockBall(1, 100, 100, is_decoy=True, element="fire")
    b2 = MockBall(2, 110, 110, is_decoy=True, element="fire")
    b3 = MockBall(3, 90, 90, is_decoy=True, element="fire")
    b1.hp = 0
    b2.hp = 0
    b3.hp = 0
    b1.decoy_type = 'explosive'
    b2.decoy_type = 'explosive'
    b3.decoy_type = 'explosive'

    world = MockWorld([b1, b2, b3], arena)
    action = Action(b1, world)
    action.execute("idle", 0.1)

    assert b1.hp == 0
    assert not b1.alive

    hazards = world.arena.hazards
    assert len(hazards) == 1
    assert hazards[0].kind == "firenado"
    assert hazards[0].duration == 10.0
    assert hazards[0].radius == 450.0

def test_elemental_resonance_no_element():
    arena = MockArena()
    b1 = MockBall(1, 100, 100, is_decoy=True, element=None)
    b2 = MockBall(2, 110, 110, is_decoy=True, element=None)
    b3 = MockBall(3, 90, 90, is_decoy=True, element=None)
    b1.hp = 0
    b2.hp = 0
    b3.hp = 0
    b1.decoy_type = 'explosive'
    b2.decoy_type = 'explosive'
    b3.decoy_type = 'explosive'

    world = MockWorld([b1, b2, b3], arena)
    action = Action(b1, world)
    action.execute("idle", 0.1)

    hazards = world.arena.hazards
    assert len(hazards) == 1
    assert hazards[0].kind == "scorched_earth"

def test_elemental_resonance_mixed_elements():
    arena = MockArena()
    b1 = MockBall(1, 100, 100, is_decoy=True, element="fire")
    b2 = MockBall(2, 110, 110, is_decoy=True, element="water")
    b3 = MockBall(3, 90, 90, is_decoy=True, element="ice")
    b1.hp = 0
    b2.hp = 0
    b3.hp = 0
    b1.decoy_type = 'explosive'
    b2.decoy_type = 'explosive'
    b3.decoy_type = 'explosive'

    world = MockWorld([b1, b2, b3], arena)
    action = Action(b1, world)
    action.execute("idle", 0.1)

    hazards = world.arena.hazards
    assert len(hazards) == 1
    assert hazards[0].kind == "scorched_earth"
