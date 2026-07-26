import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.boosters = []
        self.arena = type('Arena', (), {'hazards': []})

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, attacker, target, amount=None):
        target.hp -= attacker.damage

class MockEntity:
    def __init__(self, id, team="A"):
        self.id = id
        self.team = team
        self.alive = True
        self.x = 0
        self.y = 0
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.speed = 2.0
        self.radius = 10.0
        self.stutter_timer = 0.0

def test_bounty_contract_collect_and_payout():
    world = MockWorld()
    hunter = MockEntity(1, "A")
    enemy = MockEntity(2, "B")
    world.balls = [hunter, enemy]

    item = type('Item', (), {'kind': 'bounty_contract', 'x': 5, 'y': 5, 'radius': 500, 'active': True})()
    world.boosters = [item]

    action = Action(hunter, world)

    # 1. Collect
    # Override _get_boosters to force pick up
    action._get_boosters = lambda: [item]

    # We must patch _get_enemies so it correctly returns enemy
    action._get_enemies = lambda: [enemy]

    action._collect_booster(0.1)

    # Check if target was assigned
    assert getattr(enemy, "is_bounty_contract_target", False) == True
    assert getattr(enemy, "bounty_contract_hunter_id", None) == 1
    assert enemy.bounty_contract_timer == 60.0

    # 2. Tick timer
    enemy_action = Action(enemy, world)
    enemy_action.execute("idle", 1.0)
    assert enemy.bounty_contract_timer == 59.0

    # 3. Payout on kill
    action._award_xp = lambda *args: None

    enemy.hp = 10.0
    action._attempt_damage_internal(hunter, enemy) # this deals 10 dmg (from attacker.damage), so enemy hp -> 0

    assert enemy.hp <= 0

    assert hunter.damage == 15.0
    assert hunter.base_damage == 15.0
    assert hunter.max_hp == 150.0
    assert hunter.speed == 2.5

    events = [e for e in world.events if e[0] == "bounty_contract_completed"]
    assert len(events) == 1
