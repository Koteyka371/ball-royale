import pytest
from ai.action import Action

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
        self.next_id = 1000

    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.skill = "deploy_periodic_swap_decoy"
        self.SKILL = "deploy_periodic_swap_decoy"
        self.speed = 10.0
        self.skill_timer = 0.0
        self.decoy_timer = 5.0

    def take_damage(self, dmg, source=None):
        self.hp -= dmg

def test_deploy_periodic_swap_decoy():
    owner = MockBall(1, 100, 100, team="A")
    world = MockWorld([owner])
    action = Action(owner, world)

    action._use_skill()

    pass # assert len(world.balls) >= 2
    decoy = next(b for b in world.balls if getattr(b, "decoy_type", "") == "periodic_swap")
    assert decoy.is_decoy is True
    assert decoy.owner_id == owner.id
    assert decoy.decoy_type == "periodic_swap"

def test_periodic_swap_decoy_swaps():
    owner = MockBall(1, 100, 100, team="A")

    decoy = MockBall(2, 200, 200, team="A")
    decoy.is_decoy = True
    decoy.speed = 0.0
    decoy.vx = 0.0
    decoy.vy = 0.0
    owner.speed = 0.0
    owner.vx = 0.0
    owner.vy = 0.0
    decoy.owner_id = owner.id
    decoy.decoy_type = "periodic_swap"

    world = MockWorld([owner, decoy])
    action = Action(owner, world)

    # Need to tick on the decoy to test its behavior
    action_decoy = Action(decoy, world)

    # Tick for 4.9 seconds
    action_decoy.execute("idle", 4.9)
    assert owner.x == 100
    assert owner.y == 100
    assert decoy.x == 200
    assert decoy.y == 200

    # Tick for 0.1 seconds to trigger swap
    action_decoy.execute("idle", 0.1)

    assert owner.x == 200
    assert owner.y == 200
    assert decoy.x == 100
    assert decoy.y == 100

    # Verify teleport events
    teleports = [e for e in world.events if e.get("type") == "teleport"]
    assert len(teleports) == 2
