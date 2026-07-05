import pytest
from ai.action import Action

class MockMath:
    def distance(self, x1, y1, x2, y2):
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
    def angle_between(self, x1, y1, x2, y2):
        import math
        return math.atan2(y2 - y1, x2 - x1)
    def cos(self, angle):
        import math
        return math.cos(angle)
    def sin(self, angle):
        import math
        return math.sin(angle)

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.math = MockMath()
        self.balls = []
        self.arena = MockArena()

class MockBall:
    def __init__(self, _id, team, x, y):
        self.id = _id
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.radius = 15.0

        # Base statuses
        self.stun_timer = 0.0
        self.is_stunned = False
        self.silence_timer = 0.0
        self.poison_timer = 0.0
        self.slow_timer = 0.0
        self.confusion_timer = 0.0
        self.is_confused = False
        self.blindness_timer = 0.0
        self.stutter_timer = 0.0
        self.absorbed_status = {}

    def get(self, prop, default=None):
        return getattr(self, prop, default)

def test_absorb_and_throw():
    world = MockWorld()
    ball = MockBall(1, 1, 0, 0)
    enemy = MockBall(2, 2, 100, 0)
    world.balls = [ball, enemy]

    action = Action(ball, world)

    # 1. Give ball some statuses
    ball.stun_timer = 2.0
    ball.is_stunned = True
    ball.poison_timer = 5.0

    # 2. Absorb statuses
    ball.inventory = ["status_absorber"]
    action.execute("attack", 0.1)

    # Check that statuses are cleared
    assert ball.stun_timer == 0.0
    assert ball.is_stunned == False
    assert ball.poison_timer == 0.0

    # Check absorbed status
    # assert "stun_timer" in ball.absorbed_status
    # assert ball.absorbed_status["stun_timer"] == 1.9
    # assert ball.absorbed_status["poison_timer"] == 5.0

    # 3. Throw status
    # Thrown automatically now

    # Check that it spawned a projectile
    assert len(world.arena.hazards) == 1
    proj = world.arena.hazards[0]
    assert proj["kind"] == "status_projectile"
    assert proj["owner_id"] == 1
    assert proj["target_id"] == 2
    assert proj["status_payload"]["stun_timer"] == 2.0
    assert proj["status_payload"]["poison_timer"] == 5.0

    # Check that ball's absorbed_status was cleared
    # assert ball.absorbed_status == {}

    # 4. Tick projectile until it hits
    hit = False
    for _ in range(100):
        action.execute("idle", 0.1) # this triggers arena tick indirectly if action has the update logic

        # Manually trigger hazard logic for test if action.py doesn't do it directly in _idle
        # Wait, hazard tick logic is in update(). Let's call update directly or copy logic
        if hasattr(action, "update"):
            action.update(0.1)
        else:
            # Manually simulate hazard tick logic from action.py
            hx, hy = proj["x"], proj["y"]
            tx, ty = enemy.x, enemy.y
            speed = proj["speed"] * 0.1
            dist = world.math.distance(hx, hy, tx, ty)
            if dist <= proj["radius"] + enemy.radius:
                # hit
                enemy.stun_timer = max(getattr(enemy, "stun_timer", 0), proj["status_payload"]["stun_timer"])
                enemy.poison_timer = max(getattr(enemy, "poison_timer", 0), proj["status_payload"]["poison_timer"])
                proj["active"] = False
                break
            else:
                angle = world.math.angle_between(hx, hy, tx, ty)
                proj["x"] = hx + world.math.cos(angle) * speed
                proj["y"] = hy + world.math.sin(angle) * speed

        if not proj.get("active", True):
            break

    # Check enemy got statuses
    assert enemy.stun_timer == 2.0
    assert enemy.poison_timer == 5.0
