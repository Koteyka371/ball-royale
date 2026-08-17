import pytest
from ai.game_modes import EscortMode

class MockPayload:
    def __init__(self):
        self.team = "Defenders"
        self.ball_type = "payload"
        self.alive = True
        self.x = 100.0
        self.y = 100.0
        self.radius = 15.0

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = "player"
        self.alive = True
        self.mass = 1.0
        self.vy = 100.0

def test_escort_mode_low_gravity():
    mode = EscortMode()
    payload = MockPayload()
    mode.payload = payload

    b1 = MockBall(1, 100.0, 100.0, "Defenders")  # Near payload
    b2 = MockBall(2, 500.0, 500.0, "Attackers")  # Far from payload
    balls = [payload, b1, b2]

    world = type('MockWorld', (), {'events': []})()

    # Fast forward low gravity timer
    for _ in range(160): # 16 seconds
        mode.tick(world, balls, 0.1)

    assert mode.low_gravity_active == True, "Low gravity should be active"

    # Tick again to apply effect
    mode.tick(world, balls, 0.1)

    assert b1._low_gravity_zone_active == True, "b1 should be in low gravity zone"
    assert b1.mass == 0.2, "b1 mass should be reduced"
    assert b1.vy < 100.0, "b1 vy should be reduced"

    assert getattr(b2, "_low_gravity_zone_active", False) == False, "b2 should NOT be in low gravity zone"
    assert b2.mass == 1.0, "b2 mass should not be reduced"

    # Fast forward to end of low gravity
    for _ in range(60): # 6 seconds
        mode.tick(world, balls, 0.1)

    assert mode.low_gravity_active == False, "Low gravity should be inactive"
    assert b1._low_gravity_zone_active == False, "b1 should not be in low gravity zone anymore"
    assert b1.mass == 1.0, "b1 mass should be restored"

print("Test written")
