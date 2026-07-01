import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/')))
from ai.game_modes import GuildVsGuildMode

class MockBall:
    def __init__(self, id, x, y, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.alive = alive

class MockWorld:
    def __init__(self):
        self.balls = []

def test_gvg_mode():
    mode = GuildVsGuildMode()
    world = MockWorld()

    b1 = MockBall(1, 200, 200) # on point 1
    b2 = MockBall(2, 800, 800) # on point 2
    b3 = MockBall(3, 500, 500) # on point 3
    b4 = MockBall(4, 0, 0) # off point

    world.balls = [b1, b2, b3, b4]
    mode.setup(world, world.balls)

    # GuildA has b1, b2. GuildB has b3, b4

    for _ in range(15):
        mode._tick(1.0)

    # b1 and b2 should capture their points for GuildA
    assert mode.control_points[0]["owner"] == "GuildA"
    assert mode.control_points[1]["owner"] == "GuildA"
    # b3 captures for GuildB
    assert mode.control_points[2]["owner"] == "GuildB"

    # move b3 and b4 to point 1 and 2, b1 and b2 to point 3 (GuildA swaps to point 3, GuildB to 1,2)
    b3.x, b3.y = 200, 200
    b4.x, b4.y = 800, 800

    # GuildA all to point 3
    b1.x, b1.y = 500, 500
    b2.x, b2.y = 500, 500

    for _ in range(25):
        mode._tick(1.0)

    assert mode.control_points[0]["owner"] == "GuildB"
    assert mode.control_points[1]["owner"] == "GuildB"
    assert mode.control_points[2]["owner"] == "GuildA"

    # Move b1 and b2 back to capture everything for GuildA
    b1.x, b1.y = 200, 200
    b2.x, b2.y = 800, 800
    b3.x, b3.y = 0, 0
    b4.x, b4.y = 0, 0

    # add a new ball for GuildA on point 3
    b5 = MockBall(5, 500, 500)
    world.balls.append(b5)
    mode.guilds["GuildA"].append(5)

    for _ in range(30):
        mode._tick(1.0)
        if mode.territory_captured:
            break

    assert mode.territory_captured == True
