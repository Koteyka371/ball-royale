import pytest
import sys
sys.path.append('src')
from ai.action import Action
import math

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = 20.0
        self.alive = True
        self.hp = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.damage = 10.0
        self._wall_knockback_combo = 0
        self._wall_knockback_combo_timer = 0.0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.width = 1000
        self.height = 1000
        self.events = []
        self.game_mode = None
        class Arena:
            def __init__(self):
                self.hazards = []
            def clamp_position(self, x, y, r):
                return x, y, False
        self.arena = Arena()

    def add_event(self, type, data):
        self.events.append({'type': type, 'data': data})

    def get_nearby_entities(self, pos, radius):
        return {"enemies": [b for b in self.balls if b != pos], "allies": []}

def test_wall_knockback_combo():
    b1 = MockBall(1, 100, 100, "team1")
    b2 = MockBall(2, 110, 110, "team2")
    world = MockWorld([b1, b2])

    # Setup combo on b1
    b1._wall_knockback_combo = 1
    b1._wall_knockback_combo_timer = 1.0

    # Distance between b1 and b2 is approx 14, radius sum is 40 -> overlap

    action = Action(b1, world)
    action._resolve_collisions()

    # Check if damage and knockback were applied and combo consumed
    assert b2.hp < 100.0 # Should be reduced by bonus damage (10 * 2.0 = 20.0, so hp should be 80, plus maybe standard separation logic)
    assert b2.vx != 0.0 or b2.vy != 0.0 # Should have been knocked back
    assert getattr(b1, "_wall_knockback_combo", 0) == 0
    assert getattr(b1, "_wall_knockback_combo_timer", 0.0) == 0.0

    # Check for explosion event
    assert any(e['type'] == 'explosion' for e in world.events)

if __name__ == "__main__":
    pytest.main([__file__])
