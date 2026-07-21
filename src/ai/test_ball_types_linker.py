import pytest
import sys
sys.path.append("src")
from ai.ball_types_linker import Linker
from ai.action import Action

class MockBall:
    def __init__(self, bid, ball_type="basic", team="red"):
        self.id = bid
        self.ball_type = ball_type
        self.team = team
        self.alive = True
        self.max_hp = 100.0
        self.hp = 100.0
        self.speed = 2.0
        self.x = 0.0
        self.y = 0.0
        self.radius = 10.0
        self.damage = 10.0

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.events = []
        self.boosters = []

        class Arena:
            def __init__(self):
                self.hazards = []
                self.width = 1000
                self.height = 1000
            def is_point_inside(self, x, y):
                return True
        self.arena = Arena()

    def clamp_position(self, x, y, r):
        return x, y, False

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_linker_pairing_and_damage_split():
    linker = Linker(1)
    linker.team = "blue"

    target = MockBall(2, ball_type="tank", team="red")
    target.max_hp = 300.0
    target.hp = 300.0
    target.speed = 1.5

    world = MockWorld(balls=[linker, target])

    # 1. Test pairing on execution
    action = Action(linker, world)
    # The Action object expects strategy to be a string normally, but using {} just passes kwargs check if any, use string instead.
    action.execute('aggressive', delta=0.016)

    assert linker.link_target == target
    assert linker.max_hp == 300.0
    assert linker.hp == 300.0
    assert linker.speed == 1.5

    # 2. Test take_damage logic
    linker.take_damage(100.0)

    # 50% distributed to target (50.0), 50% to linker (50.0)
    assert linker.hp == 250.0
    assert target.hp == 250.0

    # Test death of target if damage is too high
    linker.take_damage(500.0)

    assert target.hp == 0.0
    assert target.alive == False
    assert linker.hp == 0.0
    assert linker.alive == False

def test_linker_no_pairing_same_team():
    linker = Linker(1)
    linker.team = "blue"

    target = MockBall(2, ball_type="basic", team="blue")
    target.max_hp = 150.0
    target.hp = 150.0

    world = MockWorld(balls=[linker, target])
    action = Action(linker, world)
    action.execute({}, delta=0.016)

    # Same team, shouldn't pair
    assert linker.link_target is None
    assert linker.hp == 100.0 # default HP
