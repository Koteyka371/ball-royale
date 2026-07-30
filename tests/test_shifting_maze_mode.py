import pytest
import math
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events_list = []

    def add_event(self, event_type, data):
        self.events_list.append({"type": event_type, "data": data})

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.hp = 100
        self.alive = True
        self.ball_type = "player"

def test_shifting_maze_setup():
    mode = GAME_MODES["shifting_maze"]
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    mode.setup(world, balls)

    # Check that walls and win zone are created
    assert len(world.arena.hazards) == 21
    win_zones = [h for h in world.arena.hazards if h.kind == "win_zone"]
    assert len(win_zones) == 1
    assert win_zones[0].x == 500.0
    assert win_zones[0].y == 500.0

def test_shifting_maze_tick_shifting():
    mode = GAME_MODES["shifting_maze"]
    world = MockWorld()
    balls = [MockBall(1, 100, 100)]

    mode.setup(world, balls)

    initial_walls = [{"x": w.x, "y": w.y} for w in mode.maze_walls]

    mode.tick(world, balls, delta=5.1)

    # Check that walls shifted
    shifted = False
    for i, w in enumerate(mode.maze_walls):
        if w.x != initial_walls[i]["x"] or w.y != initial_walls[i]["y"]:
            shifted = True
            break

    assert shifted
    assert any(e["type"] == "maze_shift" for e in world.events_list)

def test_shifting_maze_win_condition():
    mode = GAME_MODES["shifting_maze"]
    world = MockWorld()
    b1 = MockBall(1, 500, 500) # In center
    b2 = MockBall(2, 100, 100) # Away from center
    balls = [b1, b2]

    mode.setup(world, balls)
    mode.tick(world, balls, delta=0.1)

    assert any(e["type"] == "maze_win" for e in world.events_list)
    assert any(e["type"] == "kill" and e["data"]["killer"] == 1 and e["data"]["victim"] == 2 for e in world.events_list)

    assert b1.hp == 100
    assert b1.alive == True
    assert b2.hp == 0
    assert b2.alive == False
