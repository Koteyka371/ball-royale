import pytest
from ai.game_modes import RhythmPanelsMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.leaderboard_manager = type('LBM', (), {'data': {'current_season': 0}})()

class MockBall:
    def __init__(self, x, y):
        self.id = id(self)
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "normal"
        self.speed = 100.0
        self.base_speed = 100.0

def test_rhythm_panels_mode():
    mode = RhythmPanelsMode()
    world = MockWorld()

    # Place a ball in the center
    ball = MockBall(500.0, 500.0)

    mode.setup(world, [ball])

    assert len(world.arena.hazards) == 8

    # Find a panel and move ball precisely onto it
    panel = world.arena.hazards[0]
    ball.x = panel.x
    ball.y = panel.y

    # Tick the mode at start (phase = 0.0 < 0.4 -> lit)
    ball.hp = 90.0 # to test healing
    mode.tick(world, [ball], 0.1)

    # Should be lit
    assert getattr(panel, "is_lit") is True

    # Should be buffed
    assert ball.speed in [150.0, 225.0]
    assert ball.hp > 90.0
    assert ball.hp <= 100.0

    # Advance time to debuff phase (> 0.4)
    mode.rhythm_timer = 0.9 # so tick(0.1) makes it 1.0
    mode.tick(world, [ball], 0.1)

    # Should be unlit
    assert getattr(panel, "is_lit") is False

    # Should be debuffed and damaged
    assert ball.speed in [50.0, 75.0]
    assert ball.hp < 91.0

    # Move ball off panel
    ball.x = 0.0
    ball.y = 0.0

    mode.tick(world, [ball], 0.1)

    # Should restore base speed
    assert ball.speed in [100.0, 150.0]
