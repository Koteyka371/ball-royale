import math
from ai.ball_types_phantom import Phantom
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.arena = MockArena()
        self.balls = []
        self.game_mode = None

    def get_nearby_entities(self, entity, radius):
        return {"enemies": [], "allies": []}

def test_phase_through_skill():
    w = MockWorld()
    b = Phantom(1, 10, 10)
    w.balls.append(b)

    a = Action(b, w)

    # Use skill to become intangible
    b.skill_timer = 0
    b.skill = "phase_through" # ensure skill is set
    a._use_skill()

    assert getattr(b, "intangible_timer", 0) == 3.0, f"Expected 3.0, got {getattr(b, 'intangible_timer', 0)}"
    assert getattr(b, "intangible", False) == True

    # Try taking damage from attack
    b2 = Phantom(2, 20, 20)
    a._attempt_damage(b2, b)
    assert b.hp == 65.0 # Should not have taken damage

    # Try clamping position (should pass through walls)
    b.x = -100
    b.y = -100
    a._clamp_position()
    assert b.x == -100 # Not clamped

    # Intangible ball should not attack
    b3 = Phantom(3, 20, 20)
    a._attempt_damage(b, b3)
    assert b3.hp == 65.0, "Intangible ball should not deal damage"

    # Decrement timer
    a.execute("idle", 3.0)
    assert b.intangible_timer == 0.0
    assert getattr(b, "intangible", False) == False
