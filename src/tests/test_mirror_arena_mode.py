import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.next_id = 1000

class MockProjectile:
    def __init__(self, x, y, vx, vy, radius=5, hp=1, alive=True, ball_type="projectile"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.hp = hp
        self.alive = alive
        self.ball_type = ball_type

def test_mirror_arena_mode():
    if "mirror_arena" not in GAME_MODES:
        return
    mode = GAME_MODES["mirror_arena"]
    world = MockWorld()

    proj1 = MockProjectile(100, 500, 200, 0)
    world.projectiles.append(proj1)

    mode.tick(world, [], 0.016)

    # Should have spawned a phantom
    assert len(world.projectiles) == 2
    phantom = world.projectiles[1]
    assert phantom.is_mirrored_phantom
    assert proj1.has_mirrored

    assert phantom.x == 900
    assert phantom.vx == -200
    assert phantom.y == 500
    assert phantom.vy == 0
