import math

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "default"
        self.team = "team1"
        self.speed = 100.0

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True

class MockWorld:
    def __init__(self):
        self.events = []
        self.game_mode = None
        self.arena = lambda: None
        self.arena.hazards = []
        self.boosters = []
        self.projectiles = []

    def add_event(self, type, data):
        pass

def test_mirror_shield_booster_pickup():
    from ai.action import Action
    ball = MockBall(1, 10, 10)
    world = MockWorld()
    action = Action(ball, world)

    booster = MockBooster(15, 15, "mirror_shield_booster")
    world.boosters.append(booster)

    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.016)

    assert getattr(ball, "mirror_shield_active", False) == True
    assert getattr(ball, "mirror_shield_timer", 0.0) == 5.0
    assert len(world.boosters) == 0

def test_mirror_shield_reflection():
    from ai.action import Action
    ball = MockBall(1, 0, 0)
    world = MockWorld()
    action = Action(ball, world)

    attacker = MockBall(2, 100, 100)
    attacker.ball_type = "projectile"
    target = MockBall(1, 0, 0)
    target.mirror_shield_active = True

    # Ranged attack reflection
    action._attempt_damage(attacker, target)

    # Target shouldn't take damage (simulated, no hp change logic directly here but suspended projectile)
    assert hasattr(target, "suspended_projectiles")
    assert len(target.suspended_projectiles) == 1
    sp = target.suspended_projectiles[0]
    assert sp["target"] == attacker
    assert sp["type"] == "reflected_projectile"
    assert sp["speed"] == 600.0

def test_mirror_shield_timer():
    from ai.action import Action
    ball = MockBall(1, 0, 0)
    world = MockWorld()
    action = Action(ball, world)

    ball.mirror_shield_active = True
    ball.mirror_shield_timer = 5.0

    action.execute("idle", 2.0)
    assert ball.mirror_shield_timer == 3.0
    assert ball.mirror_shield_active == True

    action.execute("idle", 3.0)
    assert ball.mirror_shield_timer == 0.0
    assert ball.mirror_shield_active == False
