import pytest

class MockBall:
    def __init__(self, id=None, x=0.0, y=0.0, team="none"):
        self.id = id if id is not None else 1
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.speed = 100
        self.base_speed = 100
        self.max_hp = 100
        self.ball_type = "normal"

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls if balls else []
        self.events = []
        self.arena = type('MockArena', (), {})()

def test_trickster_decoy_confetti():
    from ai.action import Action

    trickster = MockBall(1, 100, 100, team="trickster")

    decoy = MockBall(2, 100, 100, team="trickster")
    decoy.is_decoy = True
    decoy.alive = False  # Trigger explosion
    decoy.decoy_timer = 0
    decoy.hp = 0
    decoy.ball_type = "trickster"

    enemy = MockBall(3, 110, 100, team="enemy")

    world = MockWorld([trickster, decoy, enemy])

    action = Action(trickster, world)
    action.execute("idle", 0.1)

    # Check if enemy is blinded and confused
    assert getattr(enemy, "is_blinded", False)
    assert getattr(enemy, "is_confused", False)
    assert getattr(enemy, "blindness_timer", 0.0) > 0
    assert getattr(enemy, "confusion_timer", 0.0) > 0

    # Check events for confetti
    confetti_events = [e for e in world.events if e.get("type") == "visual_effect" and e.get("data", {}).get("type") == "confetti"]
    assert len(confetti_events) > 0
