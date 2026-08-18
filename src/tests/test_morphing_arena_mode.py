import pytest
from ai.morphing_arena_mode import MorphingArenaMode
from arena.morphing_arena import MorphingArena

class MockWorld:
    def __init__(self):
        from arena.basic_arena import BasicArena
        self.arena = BasicArena()

class MockBall:
    def __init__(self):
        self.x = 1000.0
        self.y = 1000.0

def test_morphing_arena_mode():
    mode = MorphingArenaMode()
    world = MockWorld()
    balls = [MockBall()]

    mode.setup(world, balls)

    assert isinstance(world.arena, MorphingArena)
    assert world.arena.current_shape_idx == 0

    # Tick for 10 seconds to test transition
    for _ in range(100):
        world.arena.update_zone(0, 0.1)

    assert world.arena.morph_timer >= 9.9
    assert world.arena.transition_progress > 0.99

    # Test point inside square (idx 0) vs circle vs cross
    # With base_radius = width/2 - 100 = 900
    base_r = 900.0
    # In square, corner is at (+900, +900) relative to center. Center is 1000, 1000.
    # So 1900, 1900 should be inside square, but not circle.

    world.arena.current_shape_idx = 0 # square
    world.arena.target_shape_idx = 0
    world.arena.transition_progress = 0.0

    assert world.arena.is_point_inside(1850, 1850, 10.0) == True

    # In circle, 1850, 1850 is distance sqrt(850^2 + 850^2) = 1202 from center.
    # base_r = 900. So it is outside.
    world.arena.current_shape_idx = 1 # circle
    world.arena.target_shape_idx = 1

    assert world.arena.is_point_inside(1850, 1850, 10.0) == False

    # Test clamping
    new_x, new_y, bounced = world.arena.clamp_position(1850, 1850, 10.0)
    assert bounced == True

    # new_x, new_y should be pushed inside the circle
    import math
    dist = math.hypot(new_x - 1000.0, new_y - 1000.0)
    # The circle radius is 900. Ball radius 10. So it should be at dist <= 891
    assert dist <= 895.0
