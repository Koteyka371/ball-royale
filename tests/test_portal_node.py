import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ai.game_modes import GAME_MODES

class MockVector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class MockArena:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.hazards = []

class MockWorld:
    def __init__(self, w, h):
        self.arena = MockArena(w, h)
        self.dead_balls = []
        self.game_mode = None

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.position = MockVector2(x, y)
        self.alive = True
        self.velocity = MockVector2(0, 0)
        self.radius = 10.0
        self.hp = 100.0

def test_portal_node_mode():
    mode = GAME_MODES["portal_node"]
    world = MockWorld(1000, 1000)
    world.game_mode = mode

    b1 = MockBall(1, "TeamA", 100, 100)
    b2 = MockBall(2, "TeamB", 800, 800)
    balls = [b1, b2]

    mode.setup(world, balls)
    assert mode.team_scores["TeamA"] == 1000.0
    assert mode.team_scores["TeamB"] == 1000.0
    assert mode.portal_x == 500.0
    assert mode.portal_y == 500.0

    # Tick without capture
    mode.tick(world, balls, 1.0)
    assert mode.team_scores["TeamA"] == 1000.0
    assert mode.team_scores["TeamB"] == 1000.0

    # TeamA captures portal
    b1.position.x = mode.portal_x
    b1.position.y = mode.portal_y
    mode.tick(world, balls, 1.0)

    # TeamB's score should drain, TeamA's should remain
    assert mode.team_scores["TeamA"] == 1000.0
    assert mode.team_scores["TeamB"] == 995.0

    # Portal timer trigger
    mode.portal_timer = 9.9
    mode.tick(world, balls, 0.2)
    assert mode.portal_timer < 10.0 # reset
    # Now portal is moved somewhere random
