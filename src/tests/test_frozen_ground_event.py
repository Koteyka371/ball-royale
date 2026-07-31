def test_frozen_ground_event_registered():
    from ai.game_modes import GAME_MODES
    assert "frozen_ground_event" in GAME_MODES
    mode = GAME_MODES["frozen_ground_event"]
    assert mode.name == "Frozen Ground Event"

def test_frozen_ground_event_tick():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["frozen_ground_event"]

    class MockArena:
        base_friction = 1.0

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.events = []

        def add_event(self, e):
            self.events.append(e)

    class MockBall:
        def __init__(self):
            self.alive = True
            self.ball_type = "player"
            self.friction_multiplier = 1.0

    world = MockWorld()
    ball = MockBall()
    balls = [ball]

    mode.setup(world, balls)

    assert world.arena.base_friction == 0.1
    assert len(world.events) == 1
    assert world.events[0]["data"]["type"] == "frozen_ground_start"

    mode.tick(world, balls, delta=0.5)

    assert ball.friction_multiplier == 0.1

    mode.tick(world, balls, delta=20.0)

    assert not mode.active
    assert world.arena.base_friction == 1.0
    assert len(world.events) == 2
    assert world.events[1]["data"]["type"] == "frozen_ground_end"
