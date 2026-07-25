import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_expanding_hazard_bubbles_mode():
    mode = GAME_MODES['expanding_hazard_bubbles']
    world = MockWorld()
    ball = MockBall(500, 500)
    balls = [ball]

    mode.setup(world, balls)
    assert len(mode.bubbles) == 0
    assert mode.bubble_spawn_timer == 2.0

    # Advance until a bubble spawns
    mode.tick(world, balls, delta=2.1)
    assert len(mode.bubbles) == 1
    bubble = mode.bubbles[0]

    # Check initial properties - Note: it expands on the same tick it spawns by 15.0 * 2.1 = 31.5, so 20 + 31.5 = 51.5
    assert bubble["radius"] == 51.5

    # Move ball exactly to bubble center to guarantee hit
    ball.x = bubble["x"]
    ball.y = bubble["y"]

    # Tick to expand bubble and apply damage
    mode.tick(world, balls, delta=1.0)

    assert bubble["radius"] > 51.5 # Expanded by 15.0 * 1.0 = 15.0
    assert ball.hp < 100.0 # Took damage

    # Fast forward to bubble popping
    mode.tick(world, balls, delta=15.0)
    assert len(mode.bubbles) == 0 # Timer expired
