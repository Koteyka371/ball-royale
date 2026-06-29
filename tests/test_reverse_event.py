from ai.game_modes import ReverseEventMode

class MockBall:
    def __init__(self, id, ball_type="basic"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.x = 100.0
        self.y = 100.0
        self.vx = 5.0
        self.vy = 5.0

class MockWorld:
    pass

def test_reverse_event_mode():
    mode = ReverseEventMode()
    world = MockWorld()
    ball = MockBall(1)
    balls = [ball]

    # Verify initial state
    assert not mode.event_active
    assert mode.event_timer == 0.0

    # Tick up to just before 20s
    mode.tick(world, balls, delta=19.0)
    assert not mode.event_active
    assert mode.event_timer == 19.0
    assert ball.x == 100.0
    assert ball.y == 100.0

    # Force event to trigger by monkeypatching random.random
    import random
    original_random = random.random
    random.random = lambda: 0.05
    try:
        # Tick past 20s to trigger
        mode.tick(world, balls, delta=2.0)

        assert mode.event_active
        # The first tick that triggers the event ALSO runs the event block
        # so event_duration is reduced by delta (2.0) right away
        assert mode.event_duration == 8.0
        assert mode.event_timer == 0.0

        # Test reverse logic applied to ball
        assert ball.x == 100.0 - (5.0 * 2.0 * 2.0)
        assert ball.y == 100.0 - (5.0 * 2.0 * 2.0)

        # Tick to end event
        mode.tick(world, balls, delta=10.0)
        assert not mode.event_active

    finally:
        random.random = original_random
