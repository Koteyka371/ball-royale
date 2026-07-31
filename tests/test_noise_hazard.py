import math
from ai.noise_hazard_mode import NoiseHazardMode

class DummyHazard:
    pass

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.damage_events = []

    def _deal_damage(self, attacker, target, amount):
        self.damage_events.append((attacker, target, amount))
        target.hp -= amount

class MockBall:
    def __init__(self, id, x, y, vx, vy):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hp = 100.0
        self.alive = True

def test_noise_hazard_pulse_damage():
    mode = NoiseHazardMode()
    world = MockWorld()

    # Tick down to spawn hazard
    mode.tick(world, [], delta=5.0)

    # Tick again to bypass first frame init issues if any, just trigger the pulse
    world.events = []

    h = world.arena.hazards[0]
    h.pulse_timer = -1.0 # Force pulse on next tick
    h.duration = 10.0

    b_fast = MockBall(1, h.x + 50, h.y, 400, 0) # speed = 400
    b_slow = MockBall(2, h.x - 50, h.y, 0, 10)  # speed = 10
    b_still = MockBall(3, h.x, h.y + 50, 0, 0)  # speed = 0
    b_far = MockBall(4, h.x + 300, h.y, 1000, 0) # far away

    balls = [b_fast, b_slow, b_still, b_far]

    mode.tick(world, balls, delta=0.1)

    # Fast ball took damage (400 * 0.1 = 40)
    assert math.isclose(b_fast.hp, 60.0)
    # Slow ball didn't take damage (10 * 0.1 = 1 < 2.0 threshold)
    assert math.isclose(b_slow.hp, 100.0)
    # Still ball didn't take damage
    assert math.isclose(b_still.hp, 100.0)
    # Far ball didn't take damage despite being fast
    assert math.isclose(b_far.hp, 100.0)

    # Pulse event generated
    assert any(e["type"] == "visual_effect" and e["data"]["type"] == "noise_pulse" for e in world.events)

if __name__ == "__main__":
    test_noise_hazard_pulse_damage()
    print("Tests passed!")
