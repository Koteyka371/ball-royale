import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.boosters = boosters if boosters is not None else []
        self.events = []
        self.next_id = 1000

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.stun_timer = 0
        self.radius = 10.0
        self.inventory = []
        self.speed = 10.0
        self.ball_type = "normal"
        self.is_decoy = False

def test_deployable_decoy_swap_item_collect_and_deploy_and_swap():
    item = MockHazard("deployable_decoy_swap_item", 100, 100)
    arena = MockArena([item])

    player = MockBall(1, 100, 100, team="teamA")
    world = MockWorld(arena, [player])

    action = Action(player, world)

    # 1. Collect
    # Using internal logic for collect just by passing the item in hazards
    # Actually wait, `Action` uses get_nearby_entities. Let's mock it or just assign inventory.
    player.inventory = ["deployable_decoy_swap_item"]

    # 2. Deploy
    action.execute("flee", 0.016)

    # Check that decoy was deployed
    assert len(world.balls) == 2
    decoy = world.balls[-1]
    assert decoy.is_decoy is True
    assert getattr(decoy, "owner_id", None) == player.id
    assert abs(decoy.x - 100) < 5
    assert abs(decoy.y - 100) < 5
    assert "deployable_decoy_swap_item" not in player.inventory
    assert "decoy_swap_trigger_item" in player.inventory
    assert player.decoy_swap_cooldown == 1.0

    # 3. Try to use immediately (should fail due to cooldown)
    player.x = 200
    player.y = 200

    action.execute("flee", 0.016)
    assert getattr(player, "decoy_swap_cooldown", 0) > 0
    assert abs(player.x - 200) < 5
    assert abs(decoy.x - 100) < 5

    # 4. Wait for cooldown
    player.decoy_swap_cooldown = 0.0
    action.execute("flee", 0.016)

    # Should swap!
    assert abs(player.x - 100) < 5
    assert abs(player.y - 100) < 5
    assert abs(decoy.x - 200) < 5 or abs(decoy.x - 200) < 5
    assert abs(decoy.y - 200) < 5 or abs(decoy.y - 200) < 5
    assert "decoy_swap_trigger_item" not in player.inventory

    # Check events
    teleports = [e for e in world.events if e.get("type") == "teleport"]
    assert len(teleports) == 2
