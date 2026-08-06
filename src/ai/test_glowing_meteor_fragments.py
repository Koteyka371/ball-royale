import pytest
from .game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return (x, y, False)

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, id="b1"):
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = "player"
        self.damage_boost_timer = 0.0
        self.id = id
        self.is_decoy = False
        self.is_pet = False
        self.spawned_by_decoy_spawner = False
        self.is_final_boss = False
        self.is_behemoth = False
        self.team = "t1"
        self.max_hp = 100
        self.hp = 100
        self.stats = {}
        self.damage = 10

def test_glowing_meteor_fragments_mode():
    mode = GAME_MODES.get("glowing_meteor_fragments")
    assert mode is not None

    world = MockWorld()
    balls = [MockBall(500, 500, "b1")]

    mode.setup(world, balls)
    mode.setup_done = True

    assert len(mode.active_meteors) == 0

    # Advance time to spawn meteor, 51 ticks of 0.1 = 5.1s which > 5.0s
    for _ in range(51):
        mode.tick(world, balls, 0.1)

    assert len(mode.active_meteors) > 0
    assert any(getattr(h, "kind", "") == "meteor_indicator" for h in world.arena.hazards)

    # Store meteor position and move ball there
    meteor = mode.active_meteors[0]
    balls[0].x = meteor["x"]
    balls[0].y = meteor["y"]
    meteor_id = meteor["id"]

    # Advance time until meteor impacts
    for _ in range(25):
        mode.tick(world, balls, 0.1)

    # The meteor should have been removed and replaced by glowing_fragment, and since the ball is right there, it should collect it immediately in the same tick or next.
    assert getattr(balls[0], "damage_boost_timer", 0.0) == 10.0

    # The fragment corresponding to this meteor should be removed from hazards
    for h in world.arena.hazards:
        if getattr(h, "kind", "") == "glowing_fragment":
            # The remaining fragments must be at different positions since we only collected one
            assert getattr(h, "x", 0.0) != balls[0].x or getattr(h, "y", 0.0) != balls[0].y
