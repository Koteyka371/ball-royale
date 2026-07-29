import pytest
from ai.action import Action
class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.is_snowing = False
        self.is_heatwave = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.tick_count = 0

    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, "damage", 10.0)

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 2.0
        self.damage = 10.0
        self.attack_timer = 0.0
        self.attack_range = 50.0
        self.ball_type = "normal"
        self.is_hologram = False
        self.perception_radius = 50.0

def test_holographic_clone_attack_repeat():
    world = MockWorld()
    attacker = MockBall(1, 500, 500, "A")
    target = MockBall(2, 520, 500, "B")
    world.balls = [attacker, target]
    action = Action(attacker, world)

    # Pre-condition: Attack happens
    action._attempt_damage(attacker, target)
    assert target.hp == 90.0

    # Test logic goes here...
    assert hasattr(attacker, "pending_holographic_attacks")
    assert len(attacker.pending_holographic_attacks) == 1
    assert attacker.pending_holographic_attacks[0]["target"] == target
    assert attacker.pending_holographic_attacks[0]["timer"] == 2.0

    action.execute("attack", 1.0)
    assert target.hp == 90.0
    assert attacker.pending_holographic_attacks[0]["timer"] == 1.0

    action.execute("attack", 1.0)
    assert target.hp == 80.0
    assert len(attacker.pending_holographic_attacks) == 0

    # Ensure clone visual event was created
    clone_events = [e for e in world.events if e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "holographic_attack_clone"]
    assert len(clone_events) == 1
    assert clone_events[0]["data"]["x"] == 500
    assert clone_events[0]["data"]["y"] == 500
