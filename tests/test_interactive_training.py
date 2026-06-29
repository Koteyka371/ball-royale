from ai.interactive_training import InteractiveTrainingMode

class MockBall:
    def __init__(self, id_val, x=500.0, y=500.0):
        self.id = id_val
        self.x = x
        self.y = y
        self.ball_type = "basic"
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.perception_radius = 300.0

class MockWorld:
    def __init__(self):
        self.dead_balls = []

def test_interactive_training_setup():
    mode = InteractiveTrainingMode()
    world = MockWorld()

    user_ball = MockBall("user")
    neural_ball_1 = MockBall("ai1")
    neural_ball_2 = MockBall("ai2")
    balls = [user_ball, neural_ball_1, neural_ball_2]

    mode.setup(world, balls)

    assert mode.user_ball_id == "user"
    assert user_ball.team == "User"
    assert user_ball.is_user is True

    assert neural_ball_1.team == "Learning"
    assert neural_ball_1.ball_type == "neural"
    assert hasattr(neural_ball_1, "interactive_fitness")

def test_interactive_training_tick_fitness_increase():
    mode = InteractiveTrainingMode()
    world = MockWorld()

    # Place user and AI close to each other
    user_ball = MockBall("user", x=500, y=500)
    neural_ball = MockBall("ai1", x=550, y=500) # Distance 50 < 300
    balls = [user_ball, neural_ball]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # The neural ball should have gained fitness for being close
    assert neural_ball.interactive_fitness > 0.0

def test_interactive_training_tick_low_hp_penalty():
    mode = InteractiveTrainingMode()
    world = MockWorld()

    user_ball = MockBall("user", x=500, y=500)
    neural_ball = MockBall("ai1", x=550, y=500)
    neural_ball.hp = 10 # 10% of 100
    balls = [user_ball, neural_ball]

    mode.setup(world, balls)

    # Reset fitness after setup
    neural_ball.interactive_fitness = 0.0

    mode.tick(world, balls, delta=1.0)

    # It gains 1.0 for proximity, but loses 0.5 for low HP -> net should be 0.5
    assert neural_ball.interactive_fitness == 0.5

def test_interactive_training_tick_damage_dealt_reward():
    mode = InteractiveTrainingMode()
    world = MockWorld()

    user_ball = MockBall("user", x=500, y=500)
    neural_ball = MockBall("ai1", x=1000, y=1000) # Far away, no proximity bonus
    neural_ball.damage_dealt = 5.0
    balls = [user_ball, neural_ball]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    # Should get 5.0 * 2.0 * 1.0 = 10.0 fitness
    assert neural_ball.interactive_fitness == 10.0

def test_interactive_training_check_winner():
    mode = InteractiveTrainingMode()
    world = MockWorld()

    user_ball = MockBall("user")
    neural_ball = MockBall("ai1")
    balls = [user_ball, neural_ball]

    mode.setup(world, balls)

    # Both alive, no winner
    assert mode.check_winner(world, balls) is None

    # Neural dies
    neural_ball.alive = False
    assert mode.check_winner(world, balls) == "User"
