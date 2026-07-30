import pytest

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.ball_type = f"team{bid}"
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.weather_immunity_timer = 0.0

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append(data)

def test_shifting_maze_win_condition():
    from ai.game_modes import ShiftingMazeMode
    mode = ShiftingMazeMode()
    world = MockWorld()

    # Place a ball outside center
    b1 = MockBall(1, 100, 100)
    # Place a ball near center (500, 500)
    b2 = MockBall(2, 510, 510)

    balls = [b1, b2]
    mode.setup(world, balls)

    # Tick so the center check is made
    mode.tick(world, balls, 0.1)

    # Winner should be team2 because b2 is near center
    assert mode.check_winner(world, balls) == "team2"
