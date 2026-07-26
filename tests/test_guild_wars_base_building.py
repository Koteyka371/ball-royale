import pytest
from ai.guild_wars_base_building import GuildWarsBaseBuildingMode

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.radius = 20.0
        self.damage = 10.0
        self.hp = 100.0
        self.alive = True

def test_hq_initialization():
    mode = GuildWarsBaseBuildingMode()
    world = MockWorld()
    mode.setup(world, [])

    assert hasattr(world.arena, "hq")
    assert world.arena.hq["hp"] == 10000.0
    assert hasattr(world.arena, "defenses")
    assert len(world.arena.defenses) == 3

def test_turret_damage():
    mode = GuildWarsBaseBuildingMode()
    world = MockWorld()
    mode.setup(world, [])

    # Turret is at (100, 100) range 300, team "defender"
    enemy_ball = MockBall(150.0, 150.0, "attacker")
    balls = [enemy_ball]

    initial_hp = enemy_ball.hp
    mode.tick(world, balls, delta=1.0)

    assert enemy_ball.hp < initial_hp

def test_hq_damage():
    mode = GuildWarsBaseBuildingMode()
    world = MockWorld()
    mode.setup(world, [])

    # HQ is at (0,0) radius 100, team "defender"
    enemy_ball = MockBall(50.0, 50.0, "attacker")
    enemy_ball.damage = 100.0
    balls = [enemy_ball]

    initial_hq_hp = world.arena.hq["hp"]
    mode.tick(world, balls, delta=1.0)

    assert world.arena.hq["hp"] < initial_hq_hp
    assert world.arena.hq["hp"] == initial_hq_hp - 100.0

def test_trap_damage():
    mode = GuildWarsBaseBuildingMode()
    world = MockWorld()
    mode.setup(world, [])

    # Trap is at (0, 200) radius 40
    enemy_ball = MockBall(0.0, 200.0, "attacker")
    balls = [enemy_ball]

    initial_hp = enemy_ball.hp
    mode.tick(world, balls, delta=1.0)

    assert enemy_ball.hp < initial_hp
    # Trap should be deactivated
    trap_def = next(d for d in world.arena.defenses if d["x"] == 0.0 and d["y"] == 200.0)
    assert trap_def["type"] == "used_trap"
