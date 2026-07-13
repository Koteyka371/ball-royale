import pytest
from ai.action import Action
from ai.game_modes import BlacksmithBossMode
import math
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, x=0, y=0, radius=20, team=1, id=1):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = radius
        self.team = team
        self.id = id
        self.alive = True
        self.active_skill = None
        self.hp = 100
        self.max_hp = 100
        self.is_boss = False
        self.is_turret = False
        self.mass = 1.0
        self.damage = 10.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.mode = None
        self.arena = MagicMock()
        self.arena.width = 1000
        self.arena.height = 1000
        self.arena.hazards = []
        self.next_id = 1000

def test_anvil_collection():
    world = MockWorld()
    world.mode = BlacksmithBossMode()
    world.mode.setup(world, [])

    world.mode.tick(world, [], 0.1)

    assert len(world.boosters) == 3
    assert len(world.arena.hazards) == 3

    ball = MockBall(x=500, y=500)
    world.balls.append(ball)

    # Store references to all 3 anvils before collecting any
    anvils = list(world.boosters)
    anvil_1 = anvils[0]
    anvil_2 = anvils[1]
    anvil_3 = anvils[2]

    # move ball to first anvil piece
    ball.x = anvil_1.x
    ball.y = anvil_1.y

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert world.mode.anvil_pieces_collected == 1
    assert anvil_1 not in world.boosters

    # tick mode
    world.mode.tick(world, world.balls, 0.1)
    assert not world.mode.boss_spawned

    # collect remaining
    ball.x = anvil_2.x
    ball.y = anvil_2.y
    action._collect_booster(0.1)

    ball.x = anvil_3.x
    ball.y = anvil_3.y
    action._collect_booster(0.1)

    assert world.mode.anvil_pieces_collected == 3

    # tick mode
    world.mode.tick(world, world.balls, 0.1)

    assert world.mode.boss_spawned
    # find the boss
    boss = next((b for b in world.balls if getattr(b, 'is_world_boss', False)), None)
    assert boss is not None
    assert boss.max_hp == 2000
    assert boss.damage == 30.0

    # kill boss
    boss.hp = 0
    boss.alive = False

    world.mode.tick(world, world.balls, 0.1)

    # check loot dropped
    loot = next((h for h in world.boosters if getattr(h, 'kind', None) == 'legendary_loot'), None)
    assert loot is not None
    assert loot.x == boss.x
    assert loot.y == boss.y

def test_legendary_loot_collection():
    world = MockWorld()
    world.mode = BlacksmithBossMode()
    world.mode.setup(world, [])

    ball = MockBall(x=500, y=500)
    world.balls.append(ball)

    class MockHazard:
        def __init__(self, x, y, kind):
            self.x = x
            self.y = y
            self.kind = kind
            self.active = True

    loot = MockHazard(500, 500, "legendary_loot")
    world.boosters.append(loot)
    world.arena.hazards.append(loot)

    action = Action(ball, world)
    action._collect_booster(0.1)

    assert loot not in world.boosters
    assert loot not in world.arena.hazards

    assert hasattr(ball, 'inventory')
    assert "legendary_loot" in ball.inventory
    assert ball.damage == 30.0  # 10.0 * 3.0
    assert ball.speed == 150.0  # 100.0 * 1.5
