import pytest
from arena.arena_types import PinballArena

def test_pinball_arena_generation():
    arena = PinballArena(arena_size=2000)

    assert len(arena.rooms) == 3
    assert len(arena.corridors) == 2

    # Verify hazards
    bumpers = [h for h in arena.hazards if getattr(h, "kind", "") == "bumper"]
    flippers = [h for h in arena.hazards if getattr(h, "kind", "") == "pinball_flipper"]

    assert len(bumpers) >= 12
    assert len(flippers) == 2

    f_left = next(f for f in flippers if getattr(f, "flipper_side", "") == "left")
    f_right = next(f for f in flippers if getattr(f, "flipper_side", "") == "right")

    assert f_left.radius == 50.0
    assert f_right.radius == 50.0

    # Test update_zone flipping logic
    original_left_ft = getattr(f_left, "flip_timer", 0.0)
    original_right_ft = getattr(f_right, "flip_timer", 0.0)

    import random
    random.seed(42) # Ensure predictable random for flip logic if possible

    arena.update_zone(1, 0.016)

    # Just asserting the update_zone didn't crash, the random flip is hard to guarantee
    # without mocking random, but we can verify timer decrement
    setattr(f_left, "flip_timer", 1.0)
    arena.update_zone(2, 0.016)
    assert getattr(f_left, "flip_timer") == 1.0 - 0.016
