from unittest.mock import MagicMock
from ai.ghost_companion import GhostCompanionMode
import pytest

class MockBall:
    def __init__(self, id, hp=100.0, alive=True, team="A"):
        self.id = id
        self.hp = hp
        self.alive = alive
        self.team = team
        self.ball_type = "player"
        self.is_ghost = False
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100

class MockHazard:
    def __init__(self, id, x=0, y=0, radius=20, team="B", triggered=False):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.team = team
        self.triggered = triggered
        self.active = False

class MockArena:
    def __init__(self):
        self.hazards = []

def test_ghost_possession():
    world = MagicMock()
    del world.leaderboard_manager
    del world.profile_manager
    world.arena = MockArena()
    world.dead_balls = []

    b1 = MockBall(1, hp=0, alive=False, team="A")
    h1 = MockHazard(101, x=100, y=100, team="A")
    # enemy
    e1 = MockBall(2, hp=100, alive=True, team="B")
    # put enemy far away initially
    e1.x = 500
    e1.y = 500

    world.arena.hazards = [h1]
    balls = [b1, e1]

    mode = GhostCompanionMode()
    mode.setup(world, balls)

    # Run a tick - b1 should become a ghost and target h1 because e1 is not alive? Wait, e1 is alive.
    # Ah, if e1 is alive, it will target e1 first because we prioritize balls. Let's make e1 a ghost too, or make b1 the only ghost and there are no other valid targets.
    # We want to test hazard possession.
    # Let's make e1 dead or something.
    e1.alive = False

    mode.tick(world, balls, 0.016)

    # b1 became a ghost. It should have targeted h1.
    assert b1.is_ghost
    assert b1.ghost_target_id == 101

    # Now that it's attached to h1, let's revive e1 and place it near h1 (within 100 units)
    e1.alive = True
    e1.hp = 100
    e1.x = 110
    e1.y = 110

    mode.tick(world, balls, 0.016)

    # Ghost should have triggered the hazard because enemy is near
    assert h1.active == True
    assert h1.triggered == True
    assert b1.ghost_target_id == None
