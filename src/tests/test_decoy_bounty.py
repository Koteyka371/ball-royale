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
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

class MockEntity:
    def __init__(self, id, x, y, team="bad", kind="enemy"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.team = team
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

def test_decoy_bounty():
    world = MockWorld()
    player = MockEntity(1, 100, 100, "Red", "player")
    world.balls.append(player)

    item = MockHazard(2, 100, 100, 15.0, "decoy_bounty_item")
    world.boosters.append(item)
    world.arena.hazards.append(item)

    action = Action(player, world)
    action.execute("collect_booster", 1.0)

    assert "deployable_decoy_bounty" in player.inventory

    action.execute("defend", 1.0)

    decoys = [h for h in world.arena.hazards if h.kind == "decoy_bounty"]
    assert len(decoys) == 1

    decoy = decoys[0]
    assert decoy.x == 100
    assert decoy.y == 100
    assert getattr(decoy, 'duration', 0.0) == 15.0

    compass_events = [e for e in world.events if e["type"] == "bounty_compass"]
    assert len(compass_events) == 1
    assert compass_events[0]["data"]["x"] == 100
    assert compass_events[0]["data"]["y"] == 100
    assert compass_events[0]["data"]["owner_id"] == 1

    # Test AI targeting
    enemy = MockEntity(2, 120, 120, "Blue", "enemy")
    world.balls.append(enemy)

    enemy_action = Action(enemy, world)
    enemies = enemy_action._get_enemies()

    assert any(getattr(e, "kind", "") == "decoy_bounty" for e in enemies)
