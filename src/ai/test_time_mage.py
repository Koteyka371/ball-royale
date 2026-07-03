import pytest
from ai.ball_types_time_mage import Time_Mage
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

def test_time_mage_initialization():
    mage = Time_Mage(1, x=10, y=20)
    assert mage.BALL_TYPE == "time_mage"
    assert mage.hp == 90.0
    assert mage.SKILL == "temporal_recall"
    assert hasattr(mage, "state_history")
    assert len(mage.state_history) == 0

def test_temporal_recall_skill():
    world = MockWorld()
    mage = Time_Mage(1, x=50, y=50)
    mage.team = "a"
    mage.hp = 20
    mage.stun_timer = 2.0
    mage.is_stunned = True
    mage.poison_timer = 5.0

    mage.state_history = [{"x": 100, "y": 100, "hp": 90}]

    action = Action(mage, world)
    mage.skill = "temporal_recall"
    mage.skill_timer = 0

    action._use_skill()

    assert mage.x == 100
    assert mage.y == 100
    assert mage.hp == 90
    assert mage.stun_timer == 0.0
    assert mage.is_stunned == False
    assert mage.poison_timer == 0.0
    assert len(mage.state_history) == 0
    assert any(e[0] == "play_sound" and e[1].get("sound") == "rewind" for e in world.events)

def test_temporal_recall_no_history():
    world = MockWorld()
    mage = Time_Mage(1, x=50, y=50)
    mage.team = "a"
    mage.hp = 20

    action = Action(mage, world)
    mage.skill = "temporal_recall"
    mage.skill_timer = 0

    action._use_skill()

    assert mage.x == 50
    assert mage.y == 50
    assert mage.hp == 20
