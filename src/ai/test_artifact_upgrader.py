import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.x = 500.0
        self.y = 500.0
        self.team = "TeamA"

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

def test_artifact_upgrader_setup():
    mode = GAME_MODES["artifact_upgrader"]
    world = MockWorld()
    balls = [MockBall(1), MockBall(2, ball_type="spectator")]

    mode.setup(world, balls)

    assert hasattr(mode, "npc")
    assert mode.npc.ball_type == "crafter_npc"
    assert mode.npc.max_hp == 500.0
    assert mode.npc.hp == 500.0

    assert balls[0].npc_protection_time == 0.0
    assert not balls[0].artifact_upgraded

    # spectator should be ignored
    assert not hasattr(balls[1], "npc_protection_time")

def test_artifact_upgrader_tick_protection():
    mode = GAME_MODES["artifact_upgrader"]
    world = MockWorld()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    mode.npc.x = 500.0
    mode.npc.y = 500.0
    mode.npc.vx = 0.0
    mode.npc.vy = 0.0
    balls[0].x = 550.0
    balls[0].y = 500.0 # Distance = 50 < 150

    mode.tick(world, balls, delta=1.0)
    assert balls[0].npc_protection_time == 1.0
    assert not balls[0].artifact_upgraded

    mode.tick(world, balls, delta=30.0)
    assert balls[0].npc_protection_time == 31.0
    assert balls[0].artifact_upgraded
    assert balls[0].max_hp == 150.0
    assert balls[0].hp == 150.0
    assert balls[0].base_damage == 15.0
    assert balls[0].base_speed == 120.0 or balls[0].base_speed == 144.0

def test_artifact_upgrader_tick_hazard_damage():
    mode = GAME_MODES["artifact_upgrader"]
    world = MockWorld()
    balls = [MockBall(1)]
    mode.setup(world, balls)

    mode.npc.x = 500.0
    mode.npc.y = 500.0
    mode.npc.vx = 0.0
    mode.npc.vy = 0.0

    class MockHazard:
        def __init__(self):
            self.x = 500.0
            self.y = 500.0
            self.radius = 40.0
            self.damage = 100.0

    world.arena.hazards.append(MockHazard())

    mode.tick(world, balls, delta=1.0)
    assert mode.npc.hp == 390.0 or mode.npc.hp == 400.0

    mode.tick(world, balls, delta=5.0)
    assert not mode.npc.alive
    assert mode.npc.hp == 0.0
