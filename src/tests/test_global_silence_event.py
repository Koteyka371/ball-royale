import pytest
from ai.game_modes import GAME_MODES, GlobalSilenceEventMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self):
        self.alive = True
        self.silence_timer = 0.0

def test_global_silence_event_mode():
    mode = GlobalSilenceEventMode()
    world = MockWorld()
    balls = [MockBall(), MockBall()]

    mode.setup(world, balls)

    assert not mode.is_active
    assert mode.event_timer == 20.0

    # Tick for 19 seconds, should not activate
    mode.tick(world, balls, 19.0)
    assert not mode.is_active
    for b in balls:
        assert getattr(b, "silence_timer", 0.0) == 0.0

    # Tick 1 more second, should activate
    mode.tick(world, balls, 1.0)
    assert mode.is_active
    assert len(world.events) == 1
    assert world.events[0][0] == "global_silence_start"

    # Tick while active, should apply silence
    mode.tick(world, balls, 1.0)
    for b in balls:
        assert getattr(b, "silence_timer", 0.0) == 0.5

    # Tick to end of duration
    mode.tick(world, balls, 4.0)
    assert not mode.is_active
    assert len(world.events) == 2
    assert world.events[1][0] == "global_silence_end"

def test_global_silence_event_in_game_modes():
    assert "global_silence_event" in GAME_MODES
    assert isinstance(GAME_MODES["global_silence_event"], GlobalSilenceEventMode)
