from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, balls, arena, boosters=None):
        self.balls = balls
        self.arena = arena
        self.boosters = boosters if boosters is not None else []

class MockBooster:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockBall:
    def __init__(self, x, y, team, hp, id_val):
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.id = id_val
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0

def test_cryo_booster_collection():
    booster = MockBooster(10, 0, "cryo_booster")
    ball = MockBall(0, 0, "team1", 100, 1)
    world = MockWorld([ball], MockArena([booster]), [booster])

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]
    action._collect_booster(0.016)

    assert getattr(ball, "cryo_booster_timer", 0.0) >= 10.0
    assert not booster.active
    assert booster not in world.boosters
    assert booster not in world.arena.hazards

def test_cryo_booster_damage_and_affliction():
    attacker = MockBall(0, 0, "team1", 100, 1)
    target = MockBall(10, 0, "team2", 100, 2)
    world = MockWorld([attacker, target], MockArena([]))

    attacker.cryo_booster_timer = 5.0

    action = Action(attacker, world)
    action._attempt_damage(attacker, target)

    assert getattr(target, "cryo_affliction_timer", 0.0) == 3.0
    assert getattr(target, "cryo_affliction_spawn_timer", 0.0) == 0.0

    # Simulate movement
    target.vx = 50.0
    target.vy = 0.0

    target_action = Action(target, world)
    target_action.execute("idle", 0.1)

    assert getattr(target, "cryo_affliction_spawn_timer", 0.0) > 0.0
    assert len(world.arena.hazards) > 0
    assert world.arena.hazards[-1].kind == "ice_patch"
