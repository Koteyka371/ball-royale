from ai.game_modes import DynamicBountyMode
from ai.action import Action

class MockEntity:
    def __init__(self, entity_id, kills=0):
        self.id = entity_id
        self.alive = True
        self.ball_type = "warrior"
        self.kills = kills
        self.x = 100.0
        self.y = 100.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.loadout_fragments = 0
        self.is_dynamic_bounty = False
        self.team = "Red"
        self.stun_timer = 0.0
        self.charge_level = 0.0

class MockWorld:
    def __init__(self):
        self.events = []
        self.balls = []
        self.profile_manager = MockProfileManager()

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

class MockProfileManager:
    def add_kill(self, attacker_type, target_type):
        pass

    def is_nemesis(self, target_type, attacker_type):
        return False

def test_dynamic_bounty_assignment():
    mode = DynamicBountyMode()
    world = MockWorld()

    b1 = MockEntity(1, kills=0)
    b2 = MockEntity(2, kills=2)
    b3 = MockEntity(3, kills=1)

    balls = [b1, b2, b3]

    # Tick should assign bounty to b2
    mode.tick(world, balls, delta=0.5)

    assert b1.is_dynamic_bounty is False
    assert b2.is_dynamic_bounty is True
    assert b3.is_dynamic_bounty is False

    # Tick again with time increment to trigger VFX
    mode.tick(world, balls, delta=0.6)

    assert any(e[0] == "visual_effect" and e[1]["type"] == "bounty_mark" for e in world.events)

def test_dynamic_bounty_buffs_on_kill():
    world = MockWorld()

    attacker = MockEntity(1)
    target = MockEntity(2)
    target.hp = 5.0 # Low HP so attacker kills it in one hit
    target.is_dynamic_bounty = True

    world.balls = [attacker, target]

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    assert target.hp <= 0.0
    assert attacker.damage == 15.0 # 10.0 * 1.5
    assert attacker.base_damage == 15.0 # 10.0 * 1.5
    assert attacker.max_hp == 150.0 # 100.0 * 1.5
    # HP should go up by the diff: 50.0. Current HP was 100.0. Max is 150.0, so should be 150.0
    assert attacker.hp == 150.0
    assert attacker.loadout_fragments == 1

    assert any(e[0] == "dynamic_bounty_claimed" for e in world.events)
