import pytest
from ai.action import Action
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.safe_zone_x = 500
        self.safe_zone_y = 500

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.dead_balls = []

class MockEntity:
    def __init__(self, id, x, y, kind="enemy"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.team = "bad"
        self.hp = 100
        self.max_hp = 100
        self.ball_type = "basic"
        self.inventory = []
        self.state_history = []
        self.suspended_projectiles = []
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.speed = 100.0
        self.base_speed = 100.0
        self.speed_boost_timer = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0

class MockHazard:
    def __init__(self, id, x, y, radius, kind):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.active = True
        self.damage = 0.0
        self.owner_id = -1

def test_decoy_flare():
    world = MockWorld()
    player = MockEntity(1, 100, 100, "player")
    world.balls.append(player)

    item = MockHazard(2, 100, 100, 15.0, "decoy_flare_item")
    world.boosters.append(item)
    world.arena.hazards.append(item)

    action = Action(player, world)
    action.execute("collect_booster", 1.0)

    assert "deployable_flare" in player.inventory

    action.execute("defend", 1.0)

    flares = [h for h in world.arena.hazards if h.kind == "flare"]
    assert len(flares) == 1

    flare = flares[0]
    assert flare.x == 100
    assert flare.y == 100
    assert getattr(flare, 'duration', 0.0) == 5.0

    missile = MockHazard(3, 500, 500, 10.0, "homing_missile")
    world.arena.hazards.append(missile)

    gm = GameMode()
    gm.tick(world, world.balls, 0.016)

    assert getattr(missile, "vx", 0) < 0
    assert getattr(missile, "vy", 0) < 0
