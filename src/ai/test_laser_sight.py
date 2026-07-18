from ai.action import Action

class MockTarget:
    def __init__(self):
        self.id = 2
        self.team = "enemy"
        self.hp = 100
        self.max_hp = 100
        self.x = 10
        self.y = 10
        self.intangible = False
        self.in_mirror_dimension = False

class MockAttacker:
    def __init__(self):
        self.id = 1
        self.team = "friendly"
        self.skill_timer = 5.0
        self.skill_cooldown = 10.0
        self.laser_sight_timer = 10.0
        self.laser_sight_applied = True
        self.attack_range = 225.0
        self.base_attack_range = 150.0
        self.x = 0
        self.y = 0
        self.in_mirror_dimension = False
        self.ball_type = "base"
        self.base_speed = 100
        self.max_stamina = 100
        self.stamina = 100
        self.traits = []
        self.alive = True

class MockEntity:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
    def _deal_damage(self, attacker, target):
        pass

def test_laser_sight_cooldown_reduction():
    attacker = MockAttacker()
    target = MockTarget()
    world = MockWorld()

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    assert attacker.skill_timer == 4.5, f"Skill timer should be reduced to 4.5, got {attacker.skill_timer}"

def test_laser_sight_collection():
    attacker = MockAttacker()
    attacker.laser_sight_timer = 0.0
    attacker.laser_sight_applied = False
    attacker.attack_range = 150.0
    del attacker.base_attack_range

    world = MockWorld()
    booster = MockEntity("laser_sight_attachment")
    world.boosters = [booster]

    action = Action(attacker, world)
    action._get_boosters = lambda: [booster]

    action.world.get_nearby_entities = lambda *args, **kwargs: {'boosters': [booster], 'enemies': [], 'allies': [], 'hazards': []}

    action._collect_booster(0.1)

    assert attacker.laser_sight_timer == 15.0
    assert attacker.laser_sight_applied == True
    assert attacker.attack_range == 225.0
    assert attacker.base_attack_range == 150.0
    assert booster not in world.boosters

def test_laser_sight_expiration():
    attacker = MockAttacker()
    attacker.laser_sight_timer = 0.1

    world = MockWorld()
    action = Action(attacker, world)

    action.execute("idle", 0.2)

    assert attacker.laser_sight_timer <= 0.0
    assert attacker.laser_sight_applied == False
    assert attacker.attack_range == 150.0
