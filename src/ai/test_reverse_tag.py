import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x=0, y=0, team="Red", ball_type="player"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.max_hp = 100.0
        self.hp = 100.0
        self.radius = 10
        self.is_reverse_it = False
        self.reverse_tag_cooldown = 0.0

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_reverse_tag_setup():
    mode = GAME_MODES["reverse_tag"]
    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    balls = [b1, b2]

    mode.setup(world, balls)

    # One and only one should be IT
    it_count = sum(1 for b in balls if b.is_reverse_it)
    assert it_count == 1

    # Both should have initial score 0
    assert mode.scores[1] == 0.0
    assert mode.scores[2] == 0.0

def test_reverse_tag_tick():
    mode = GAME_MODES["reverse_tag"]
    world = MockWorld()
    b1 = MockBall(1, x=0, y=0)
    b2 = MockBall(2, x=100, y=100) # Far apart
    b1.is_reverse_it = True
    b2.is_reverse_it = False
    balls = [b1, b2]

    mode.scores = {1: 0.0, 2: 0.0}

    delta = 1.0
    mode.tick(world, balls, delta)

    # IT player gains score
    assert mode.scores[1] == 10.0
    assert mode.scores[2] == 0.0

    # IT player loses max HP
    assert b1.max_hp == 95.0
    assert b1.hp == 95.0

    # Non-IT player keeps HP
    assert b2.max_hp == 100.0
    assert b2.hp == 100.0

def test_reverse_tag_collision():
    mode = GAME_MODES["reverse_tag"]
    world = MockWorld()
    b1 = MockBall(1, x=0, y=0)
    b2 = MockBall(2, x=5, y=0) # Overlapping
    b1.is_reverse_it = True
    b2.is_reverse_it = False
    balls = [b1, b2]

    mode.scores = {1: 0.0, 2: 0.0}

    delta = 1.0
    mode.tick(world, balls, delta)

    # b1 lost IT, b2 gained IT
    assert b1.is_reverse_it is False
    assert b2.is_reverse_it is True

    # Cooldown applied
    assert b1.reverse_tag_cooldown == 1.0
    assert b2.reverse_tag_cooldown == 1.0

def test_reverse_tag_check_winner():
    mode = GAME_MODES["reverse_tag"]
    world = MockWorld()
    b1 = MockBall(1, team="Red")
    b2 = MockBall(2, team="Red")
    b3 = MockBall(3, team="Blue")
    balls = [b1, b2, b3]

    mode.scores = {1: 50.0, 2: 100.0, 3: 20.0}

    # 2 teams alive
    assert mode.check_winner(world, balls) is None

    # Blue dies, Red is left
    b3.alive = False

    # Highest score in Red is b2
    winner = mode.check_winner(world, balls)
    assert winner == "Red"

    # All die, return highest overall score ID
    b1.alive = False
    b2.alive = False
    winner_id = mode.check_winner(world, balls)
    assert winner_id == "2"
