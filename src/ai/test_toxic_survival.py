import pytest
from ai.game_modes import ToxicSurvivalMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.boosters = []
        self.arena = MockArena()

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockBall:
    def __init__(self, id, team):
        self.id = id
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.ball_type = "warrior"
        self.toxic_immune_timer = 0.0
        self.time_since_death = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_toxic_survival_damage():
    mode = ToxicSurvivalMode()
    world = MockWorld()
    ball1 = MockBall(1, 1)
    ball2 = MockBall(2, 2)
    ball2.toxic_immune_timer = 5.0 # Immune
    balls = [ball1, ball2]

    # Tick 1 second
    mode.tick(world, balls, 1.0)

    # Ball 1 should take 5 damage
    assert ball1.hp == 95.0
    # Ball 2 should take 0 damage because of immunity
    assert ball2.hp == 100.0

def test_toxic_survival_booster_spawn():
    mode = ToxicSurvivalMode()
    world = MockWorld()
    balls = []

    # Tick 5 seconds to trigger booster spawn
    mode.tick(world, balls, 5.0)

    assert hasattr(world, "boosters")
    assert len(world.boosters) == 1
    assert world.boosters[0].kind == "immune_booster"

def test_toxic_survival_winner():
    mode = ToxicSurvivalMode()
    world = MockWorld()
    ball1 = MockBall(1, 1)
    ball2 = MockBall(2, 2)
    balls = [ball1, ball2]

    assert mode.check_winner(world, balls) is None

    ball2.alive = False
    assert mode.check_winner(world, balls) == "1"

    ball1.alive = False
    assert mode.check_winner(world, balls) == "Draw"
