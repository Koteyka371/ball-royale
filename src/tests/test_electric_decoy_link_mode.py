import math
import pytest
from ai.game_modes import GameMode, GAME_MODES

class MockBall:
    def __init__(self, id, x, y, team="neutral", is_decoy=False, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.is_decoy = is_decoy
        self.owner_id = owner_id
        self.alive = True
        self.hp = 100.0
        self.radius = 10.0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []

def test_electric_decoy_link_mode():
    mode = GAME_MODES.get("electric_decoy_link")
    assert mode is not None, "Mode not found."

    owner = MockBall(1, 0, 0, "A")
    decoys = []
    # Spawn 6 decoys so that we meet the "> 5" condition
    for i in range(6):
        # We put them in a line: (0, 0) to (50, 0)
        decoys.append(MockBall(10+i, i*10, 0, "A", True, 1))

    # Put enemy right on the line, let's say at (25, 0)
    enemy = MockBall(2, 25, 0, "B")

    world = MockWorld([owner, enemy] + decoys)
    mode.tick(world, world.balls, 1.0)

    assert enemy.hp < 100.0, "Enemy should have taken damage."

    events_spark = [e for e in world.events if e.get("type") == "electric_link_spark"]
    assert len(events_spark) > 0, "Should have created an electric link spark event."
