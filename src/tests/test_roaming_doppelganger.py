import pytest
from ai.game_modes import RoamingDoppelgangerMode

class MockArena:
    def __init__(self):
        self.width = 10000
        self.height = 10000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 1

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x, y):
        self.id = 10
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 20.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "basic"
        self.team = "Player"
        self.speed = 200.0
        self.base_speed = 200.0
        self.damage = 10.0
        self.base_damage = 10.0

def test_roaming_doppelganger_spawn_and_mimic():
    mode = RoamingDoppelgangerMode()
    world = MockWorld()
    # Place player very far away so boss doesn't immediately mimic them
    player = MockBall(50000, 50000)
    world.balls.append(player)

    # Tick 1: Spawn boss
    mode.tick(world, world.balls, 0.016)

    assert hasattr(world, "doppelganger_spawned")
    assert hasattr(world, "doppelganger_boss")
    boss = world.doppelganger_boss
    assert boss in world.balls
    assert boss.ball_type == "elite_doppelganger"

    # Move boss close to player
    boss.x = 49990
    boss.y = 49990

    # Tick 2: Boss spots player and mimics
    mode.tick(world, world.balls, 0.016)

    assert boss.mimic_timer == 30.0
    assert boss.mimic_target_id == player.id
    assert boss.speed == player.speed
    assert boss.radius == player.radius
    assert boss.max_hp == player.max_hp

    # Make player run away
    player.x = 100
    player.y = 100

    # Tick 3: Boss should chase
    mode.tick(world, world.balls, 0.016)
    assert boss.vx != 0.0 or boss.vy != 0.0
