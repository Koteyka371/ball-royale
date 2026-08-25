from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y, alive=True, ball_type="player", hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive
        self.ball_type = ball_type
        self.hp = hp
        self.radius = 15.0

class MockWorld:
    pass

def test_infection_aura():
    mode = GAME_MODES["infection_aura"]
    world = MockWorld()

    b1 = MockBall(1, 0, 0)
    b2 = MockBall(2, 50, 0) # Close enough to get infected
    b3 = MockBall(3, 500, 0) # Too far

    balls = [b1, b2, b3]

    mode.setup(world, balls)

    infected_count = sum(1 for b in balls if getattr(b, "is_infected", False))
    assert infected_count == 1

    # Make b1 infected manually for test stability
    for b in balls:
        b.is_infected = False

    b1.is_infected = True

    # Tick for 1.9 seconds
    for _ in range(19):
        mode.tick(world, balls, 0.1)

    assert not getattr(b2, 'is_infected', False)

    # Tick for another 0.2 seconds
    for _ in range(2):
        mode.tick(world, balls, 0.1)

    assert getattr(b2, 'is_infected', False)
    assert not getattr(b3, 'is_infected', False)

    assert b1.hp < 100.0
