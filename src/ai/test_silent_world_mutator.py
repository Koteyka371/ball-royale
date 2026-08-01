from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id_val, ball_type):
        self.id = id_val
        self.ball_type = ball_type
        self.alive = True
        self.silence_timer = 0.0
        self.silencer_timer = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []

def test_silent_world_mutator():
    mode = GAME_MODES.get("silent_world_mutator")
    assert mode is not None
    assert mode.mutators_active == True
    assert "silent_world" in mode.mutators

    world = MockWorld()
    balls = [MockBall(1, "tank"), MockBall(2, "spectator"), MockBall(3, "ninja")]
    world.balls = balls

    mode.tick(world, balls, 0.1)

    assert balls[0].silence_timer >= 2.0
    assert balls[0].silencer_timer >= 2.0
    assert balls[1].silence_timer == 0.0
    assert balls[1].silencer_timer == 0.0
    assert balls[2].silence_timer >= 2.0
    assert balls[2].silencer_timer >= 2.0
