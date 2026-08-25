import pytest
from ai.flood_arena import FloodArenaMode

class MockArena:
    def __init__(self):
        self.width = 800.0
        self.height = 600.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.hazards = []

class MockBall:
    def __init__(self, is_aquatic=False):
        self.alive = True
        self.type = 'aquatic' if is_aquatic else 'normal'
        self.speed = 10.0
        self.perception_radius = 100.0
        self.x = 400.0
        self.y = 300.0

def test_flood_arena_water_debuff():
    mode = FloodArenaMode()
    world = MockWorld()
    ball_normal = MockBall(is_aquatic=False)
    ball_aquatic = MockBall(is_aquatic=True)

    mode.tick(world, [ball_normal, ball_aquatic], 1.0)

    # Normal ball should be slowed down and blinded
    assert ball_normal.speed == pytest.approx(10.0 * mode.water_slow_factor)
    assert ball_normal.perception_radius == pytest.approx(100.0 * mode.water_perception_factor)

    # Aquatic ball should remain normal
    assert ball_aquatic.speed == 10.0
    assert ball_aquatic.perception_radius == 100.0

def test_flood_arena_debris_buff():
    mode = FloodArenaMode()
    world = MockWorld()
    ball = MockBall(is_aquatic=False)

    # Apply debris buff
    ball.has_floating_debris = True
    ball.floating_debris_timer = 5.0
    ball.stamina = 10.0

    # Initial state (should restore stats to normal immediately)
    # the buff means water debuffs aren't applied
    mode.tick(world, [ball], 1.0)

    assert ball.has_floating_debris is True
    assert ball.floating_debris_timer == pytest.approx(4.0)
    assert ball.speed == 10.0
    assert ball.perception_radius == 100.0

    # Wait for timer to run out
    mode.tick(world, [ball], 4.0)

    # Should lose buff and get debuffed
    assert ball.has_floating_debris is False
    assert ball.speed == pytest.approx(10.0 * mode.water_slow_factor)
    assert ball.perception_radius == pytest.approx(100.0 * mode.water_perception_factor)

def test_flood_arena_spawns():
    mode = FloodArenaMode()
    world = MockWorld()

    mode.tick(world, [], mode.debris_spawn_interval)
    assert len(world.boosters) == 1
    assert world.boosters[0].type == 'floating_debris'

    mode.tick(world, [], mode.whirlpool_spawn_interval)
    assert len(world.hazards) == 1
    assert world.hazards[0].kind == 'whirlpool'

def test_whirlpool_pull():
    mode = FloodArenaMode()
    world = MockWorld()

    # Spawn a whirlpool manually
    mode._spawn_whirlpool(world)
    whirlpool = world.hazards[0]

    if isinstance(whirlpool, dict):
        whirlpool['x'] = 400.0
        whirlpool['y'] = 300.0
        whirlpool['pull_strength'] = 100.0
        whirlpool['radius'] = 200.0
    else:
        whirlpool.x = 400.0
        whirlpool.y = 300.0
        whirlpool.pull_strength = 100.0
        whirlpool.radius = 200.0

    ball = MockBall()
    ball.x = 500.0  # 100 pixels to the right
    ball.y = 300.0

    # Update via tick
    mode.tick(world, [ball], 1.0)

    # Expected pull:
    # dx = -100, dy = 0, dist = 100
    # force = 100 * (1 - 100/200) = 50
    # ball.x += (-100/100) * 50 = -50

    assert ball.x == pytest.approx(450.0)
    assert ball.y == pytest.approx(300.0)
