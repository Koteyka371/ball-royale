import pytest
from ai.game_modes import HauntedEventMode

class MockArena:
    def __init__(self):
        self.is_night = False
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val):
        self.id = id_val
        self.alive = True
        self.ball_type = "basic"
        self.x = 500.0
        self.y = 500.0
        self.vx = 0.0
        self.vy = 0.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.radius = 20.0
        self.emotion = "neutral"
        self.siren_feared_timer = 0.0
        self.invert_timer = 0.0
        self.hide_hp_bar = False
        self.hide_team_color = False

def test_nightmare_hazard():
    mode = HauntedEventMode()
    world = MockWorld()

    # Create target ball (low stamina)
    b1 = MockBall(1)
    b1.stamina = 20.0
    b1.max_stamina = 100.0
    b1.x = 800.0
    b1.y = 800.0

    # Create non-target ball (high stamina)
    b2 = MockBall(2)
    b2.stamina = 100.0
    b2.max_stamina = 100.0
    b2.x = 200.0
    b2.y = 200.0

    mode.setup(world, [b1, b2])

    # Fast forward to nightmare spawn (10 seconds)
    mode.tick(world, [b1, b2], delta=10.0)

    nightmares = [h for h in world.arena.hazards if getattr(h, "kind", "") == "nightmare"]
    assert len(nightmares) == 1
    nightmare = nightmares[0]

    # Manually place nightmare away from target
    nightmare.x = 500.0
    nightmare.y = 500.0

    # Tick again to move nightmare towards target
    mode.tick(world, [b1, b2], delta=0.5)

    # Check that nightmare moved towards b1
    # distance was sqrt(300^2 + 300^2) = 424.26
    # speed is 400.0, delta is 0.5 => moved 200 units towards b1
    assert nightmare.x > 500.0
    assert nightmare.y > 500.0

    # Now simulate a catch by placing it exactly on b1
    nightmare.x = b1.x
    nightmare.y = b1.y

    mode.tick(world, [b1, b2], delta=0.1)

    # Check that the target was caught and given feared/invert status
    assert b1.emotion == "fear"
    assert b1.siren_feared_timer >= 2.0
    assert b1.invert_timer >= 3.0

    # Check that the nightmare despawned (active = False)
    assert not nightmare.active
