from ai.game_modes import LunarEclipseEventMode
from unittest.mock import MagicMock
import random

def test_lunar_eclipse_boss_spawn():
    mode = LunarEclipseEventMode()
    world = MagicMock()
    world.arena = MagicMock()
    world.arena.hazards = []
    world.arena.width = 1000
    world.arena.height = 1000
    world.add_event = MagicMock()

    ball = MagicMock()
    ball.radius = 15.0
    balls = [ball]

    original_random = random.random
    try:
        random.random = lambda: 0.1
        mode.event_timer = 31.0
        mode.tick(world, balls, 0.016)

        assert mode.event_active
        assert any(h.kind == "eclipse_boss" for h in world.arena.hazards)
        assert getattr(mode, 'boss_spawned', False)
    finally:
        random.random = original_random

def test_lunar_eclipse_boss_conversion():
    mode = LunarEclipseEventMode()
    world = MagicMock()
    world.arena = MagicMock()
    class MockHazard:
        def __init__(self, id, x, y, radius, kind, damage):
            self.id, self.x, self.y, self.radius, self.kind, self.damage = id, x, y, radius, kind, damage
            self.dx, self.dy = 1.0, 0.0

    boss = MockHazard(60000, 500, 500, 40.0, "eclipse_boss", 0.0)
    world.arena.hazards = [boss]
    world.arena.width = 1000
    world.arena.height = 1000
    world.add_event = MagicMock()

    ball = MagicMock()
    ball.x, ball.y, ball.radius, ball.alive, ball.team, ball.hp, ball.max_hp = 510, 510, 15.0, True, "Red", 50.0, 100.0
    balls = [ball]
    mode.event_active = True
    mode.event_duration = 5.0

    mode.tick(world, balls, 0.016)
    assert ball.team == "Shadow"
    assert ball.hp == 100.0
