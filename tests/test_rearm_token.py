import pytest

class MockArena:
    def __init__(self):
        self.hazards = []
        self.boundary_states = {}

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.next_id = 100

class MockBall:
    def __init__(self, id, x=0, y=0, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.skill_timer = 5.0
        self.skill = "deploy_decoy"
        self.SKILL_COOLDOWN = 10.0
        self.speed = 5.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 10
        self.y = 10

def test_rearm_token():
    from ai.action import Action
    world = MockWorld()
    ball = MockBall(id=1, x=0, y=0)
    world.balls.append(ball)

    booster = MockBooster("rearm_token")
    world.boosters.append(booster)

    action = Action(ball, world)

    # 1. Collect booster
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._collect_booster(0.1)

    assert ball.skill_timer == 0.0
    assert getattr(ball, "rearm_damage_boost", False) == True
    assert len(world.boosters) == 0

    # 2. Deploy decoy
    action._use_skill()

    assert ball.rearm_damage_boost == False
    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) > 0
    decoy = decoys[0]
    assert getattr(decoy, "rearm_damage_boost", False) == True

    # 3. Explode decoy
    enemy = MockBall(id=2, x=decoy.x, y=decoy.y, team="B")
    world.balls.append(enemy)

    decoy.hp = 0 # Force explosion

    action.execute("idle", 0.1)

    assert enemy.hp < 100.0