def test_bounty_hunter_damage():
    from ai.action import Action
    from ai.ball_types_bounty_hunter import BountyHunter

    class MockWorld:
        def _deal_damage(self, attacker, target):
            target.hp -= attacker.damage

    class MockTarget:
        def __init__(self, is_bounty=False, high_threat=False):
            self.hp = 100.0
            self.max_hp = 100.0
            self.is_bounty = is_bounty
            self.high_threat = high_threat

    world = MockWorld()
    hunter = BountyHunter(1)

    # Normal target
    target1 = MockTarget()
    action = Action(hunter, world)
    action._attempt_damage(hunter, target1)
    assert target1.hp == 100.0 - 25.0

    # Bounty target
    target2 = MockTarget(is_bounty=True)
    action = Action(hunter, world)
    action._attempt_damage(hunter, target2)
    assert target2.hp == 100.0 - 25.0

    # High threat target
    target3 = MockTarget(high_threat=True)
    action = Action(hunter, world)
    action._attempt_damage(hunter, target3)
    assert target3.hp == 100.0 - 25.0

def test_bounty_hunter_kill_buff():
    from ai.action import Action
    from ai.ball_types_bounty_hunter import BountyHunter

    class MockWorld:
        def _deal_damage(self, attacker, target):
            target.hp -= attacker.damage

    class MockTarget:
        def __init__(self, hp, is_bounty=False, high_threat=False):
            self.hp = hp
            self.max_hp = 100.0
            self.is_bounty = is_bounty
            self.high_threat = high_threat
            self.id = 2

    world = MockWorld()
    hunter = BountyHunter(1)
    hunter.hp = 10.0 # start at low health

    # Kill a normal target
    target1 = MockTarget(hp=10.0)
    action = Action(hunter, world)
    action._attempt_damage(hunter, target1)
    assert target1.hp <= 0.0
    assert hunter.hp == 10.0 # No heal

    # Kill a bounty target
    target2 = MockTarget(hp=10.0, is_bounty=True)
    action = Action(hunter, world)
    action._attempt_damage(hunter, target2)
    assert target2.hp <= 0.0
    assert hunter.hp == hunter.max_hp # Full heal!
    assert getattr(hunter, "speed_boost_timer", 0.0) == 3.0 # Speed boost

def test_bounty_hunter_indicator():
    from ai.action import Action
    from ai.ball_types_bounty_hunter import BountyHunter

    class MockWorld:
        def __init__(self):
            self.events = []
            self.balls = []

    class MockTarget:
        def __init__(self, id, is_bounty=False, high_threat=False, alive=True):
            self.id = id
            self.is_bounty = is_bounty
            self.high_threat = high_threat
            self.alive = alive
            self.x = 100.0
            self.y = 100.0
            self.team = "Blue"

    world = MockWorld()
    hunter = BountyHunter(1)
    hunter.team = "Red"
    hunter.bounty_indicator_timer = 0.0
    target = MockTarget(2, is_bounty=True)
    world.balls = [hunter, target]

    action = Action(hunter, world)
    action.execute("idle", 0.1)

    assert any(e["type"] == "bounty_compass" for e in world.events)
    assert any(e["type"] == "visual_effect" and e["data"]["color"] == "orange" for e in world.events)

def test_bounty_hunter_indicator_high_threat():
    from ai.action import Action
    from ai.ball_types_bounty_hunter import BountyHunter

    class MockWorld:
        def __init__(self):
            self.events = []
            self.balls = []

    class MockTarget:
        def __init__(self, id, is_bounty=False, high_threat=False, alive=True):
            self.id = id
            self.is_bounty = is_bounty
            self.high_threat = high_threat
            self.alive = alive
            self.x = 100.0
            self.y = 100.0
            self.team = "Blue"

    world = MockWorld()
    hunter = BountyHunter(1)
    hunter.team = "Red"
    hunter.bounty_indicator_timer = 0.0
    target = MockTarget(2, is_bounty=False, high_threat=True)
    world.balls = [hunter, target]

    action = Action(hunter, world)
    action.execute("idle", 0.1)

    assert any(e["type"] == "bounty_compass" for e in world.events)
    assert any(e["type"] == "visual_effect" and e["data"]["color"] == "orange" for e in world.events)
