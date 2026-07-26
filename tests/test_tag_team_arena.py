import pytest
from arena.tag_team_arena import TagTeamArena

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def test_tag_team_arena_initialization():
    arena = TagTeamArena(2000.0)
    assert arena.width == 2000.0
    assert arena.name == "Tag Team Arena"

def test_tag_team_arena_cooldown():
    arena = TagTeamArena(2000.0)
    assert hasattr(arena, "swap_cooldown")
    assert arena.swap_cooldown > 0

def test_tag_team_swap():
    arena = TagTeamArena(2000.0)
    b1 = MockBall(10.0, 10.0)
    b2 = MockBall(100.0, 100.0)

    # Successful swap
    assert arena.trigger_swap(1, b1, b2) == True
    assert b1.x == 100.0
    assert b1.y == 100.0
    assert b2.x == 10.0
    assert b2.y == 10.0

    # Cooldown check
    assert arena.trigger_swap(1, b1, b2) == False

    # Tick down cooldown
    arena.update_zone(1, 5.0)
    assert arena.trigger_swap(1, b1, b2) == True
