import pytest
from ai.game_modes import OccasionalMirrorWallsMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []

class MockBall:
    def __init__(self):
        self.alive = True

class MockProjectile:
    def __init__(self, x, y, vx, vy, radius=5, ball_type="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.ball_type = ball_type

def test_occasional_mirror_walls():
    mode = OccasionalMirrorWallsMode()
    world = MockWorld()

    mode.setup(world, [])
    assert mode.active is False

    # Fast forward to activation
    mode.timer = 0.1
    mode.tick(world, [], 0.2)
    assert mode.active is True

    # Projectile hits wall while active -> bounces BACK AT ATTACKER (vx = -vx, vy = -vy)
    proj = MockProjectile(1, 100, -100, 50)
    world.projectiles.append(proj)

    mode.tick(world, [], 0.016)
    assert proj.vx == 100
    assert proj.vy == -50 # It reversed BOTH vx and vy to go straight back
    assert proj.x > 1 # It didn't get stuck

    # Wait for deactivation
    mode.active_timer = 0.1
    mode.tick(world, [], 0.2)
    assert mode.active is False

    # Normal bounce or pass through? The prompt says "Walls around the map occasionally become mirrors". So usually they might not be mirrors, meaning projectiles either pass through or are destroyed, or maybe this mode just doesn't reflect them back at the attacker when inactive. If it doesn't reflect them, they would retain their vx/vy until the engine handles wall collision (or engine destroys them).
    proj2 = MockProjectile(1, 100, -100, 50)
    world.projectiles.append(proj2)
    mode.tick(world, [], 0.016)
    assert proj2.vx == -100 # No interference from the mode when not active
