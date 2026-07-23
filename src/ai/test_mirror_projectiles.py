from ai.game_modes import GAME_MODES, MirrorProjectilesMode

class MockBall:
    def __init__(self, id, x, y, vx=0.0, vy=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0

class MockArena:
    def __init__(self):
        self.width = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.leaderboard_manager = type('Mock', (), {'data': {'current_season': 4}})()

def test_mirror_projectiles_mode_clones():
    mode = MirrorProjectilesMode()
    world = MockWorld()

    proj = MockBall(id=1, x=100, y=200, vx=50, vy=10)
    world.projectiles.append(proj)

    mode.tick(world, [], 0.016)

    assert len(world.projectiles) == 2, "Mirror clone was not created"

    clone = world.projectiles[1]
    assert getattr(clone, 'is_mirror_clone', False) == True, "Clone missing mirror flag"
    assert clone.x == 900, f"Expected clone x to be 900, got {clone.x}"
    assert clone.vx == -50, f"Expected clone vx to be -50, got {clone.vx}"
    assert clone.y == 200, "Clone y should match original"
    assert clone.vy == 10, "Clone vy should match original"

    # Tick again to make sure it doesn't clone again
    mode.tick(world, [], 0.016)
    assert len(world.projectiles) == 2, "Projectiles cloned multiple times"
