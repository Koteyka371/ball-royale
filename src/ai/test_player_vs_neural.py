from ai.game_modes import PlayerVsNeuralMode

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.team = None

class MockWorld:
    pass

def test_player_vs_neural_setup():
    mode = PlayerVsNeuralMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout"), MockBall(3, "tank"), MockBall(4, "healer"), MockBall(5, "sniper"), MockBall(6, "ninja")]

    mode.setup(world, balls)

    assert balls[0].team == "Players"
    assert balls[1].team == "Neural"
    assert balls[2].team == "Neural"
    assert balls[3].team == "Neural"

    assert balls[4].team == "Neural"
    assert balls[4].ball_type == "neural"
    assert balls[5].team == "Neural"
    assert balls[5].ball_type == "neural"

def test_player_vs_neural_check_winner():
    mode = PlayerVsNeuralMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "neural")]

    mode.setup(world, balls)

    assert mode.check_winner(world, balls) is None

    balls[1].alive = False
    assert mode.check_winner(world, balls) == "Players"

    balls[1].alive = True
    balls[0].alive = False
    assert mode.check_winner(world, balls) == "Neural"

    balls[1].alive = False
    assert mode.check_winner(world, balls) == "Draw"
