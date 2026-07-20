import math
from ai.game_modes import UnstableTeleportDashesMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.safe_zone_center = (500.0, 500.0)
        self.safe_zone_radius = 500.0

    def clamp_position(self, x, y, radius):
        bounced = False
        new_x = x
        new_y = y
        if x < radius:
            new_x = radius
            bounced = True
        elif x > self.width - radius:
            new_x = self.width - radius
            bounced = True
        if y < radius:
            new_y = radius
            bounced = True
        elif y > self.height - radius:
            new_y = self.height - radius
            bounced = True
        return new_x, new_y, bounced

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.projectiles = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.base_damage = 10.0
        self.original_base_damage = 10.0
        self.traits = []
        self.weather_immunity_timer = 999.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 200.0
        self.invisible = False
        self.ball_type = "normal"
        self.is_dashing = True

def test_unstable_teleport_dashes_mode():
    mode = UnstableTeleportDashesMode()
    world = MockWorld()

    # Create multiple balls to ensure at least one teleports due to RNG
    balls = [MockBall(500.0, 500.0) for _ in range(100)]

    mode.tick(world, balls, 0.016)

    teleported_count = 0
    for b in balls:
        if b.x != 500.0 or b.y != 500.0:
            teleported_count += 1
            # Check cooldown is set
            assert getattr(b, "unstable_tp_cd", 0.0) > 0.0

    # With 20% chance and 100 balls, it's statistically extremely likely > 0
    assert teleported_count > 0, "No balls teleported. RNG might have failed or logic is broken."

    # Test cooldown prevents multiple teleports
    b = balls[0]
    b.x = 500.0
    b.y = 500.0
    b.unstable_tp_cd = 10.0

    mode.tick(world, [b], 0.016)

    # Position should be unchanged, cooldown decreased
    assert b.x == 500.0
    assert b.y == 500.0
    assert b.unstable_tp_cd < 10.0
