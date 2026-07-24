from unittest.mock import MagicMock
from ai.action import Action

def test_rooted_boots_reduces_knockback_multiplier():
    class MockBall:
        def __init__(self, x, y, cosmetic="rooted_boots"):
            self.id = 1
            self.x = x
            self.y = y
            self.vx = 0.0
            self.vy = 0.0
            self.cosmetic = cosmetic
            self.polarity_cooldown = 0
            self.alive = True
            self.team = 1
            self.hp = 100
            self.speed = 2.0
            self.skill = "dash"
            self.radius = 10.0
            self.mass = 1.0

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []

    class MockWorld:
        def __init__(self):
            self.balls = []
            self.arena = MockArena()
            self.boosters = []
            self.items = []
            self.tick = 0
            self.game_mode = None

        def get_nearby_entities(self, ball, radius):
            return {"enemies": [b for b in self.balls if b != ball], "allies": []}

    b1 = MockBall(100, 100, "none")
    b2 = MockBall(105, 100, "rooted_boots")  # Overlaps b1, distance 5, overlap 15
    b2.id = 2

    world = MockWorld()
    world.balls = [b1, b2]

    # Test b2 is pushed much less due to rooted_boots (multiplier 0.05)
    action_b2 = Action(b2.id, world)
    action_b2.ball = b2

    action_b2._resolve_collisions()

    # Overlap is 20 - 5 = 15. Normal multiplier is 1.0. Rooted boots is 0.05.
    # b2 should move by nx * overlap * knockback_multiplier
    # dx = b2.x - b1.x = 5. dist = 5. nx = 1.0
    # Expected x = 105 + (1.0 * 15 * 0.05) = 105 + 0.75 = 105.75

    assert abs(b2.x - 105.75) < 0.01
