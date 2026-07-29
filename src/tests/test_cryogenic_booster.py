import pytest
from ai.action import Action
from arena.arena_types import Hazard

class MockEntity:
    def __init__(self, x=0.0, y=0.0, id=1, team="team1", kind="ball"):
        self.x = x
        self.y = y
        self.id = id
        self.team = team
        self.kind = kind
        self.ball_type = kind
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.width = 1000.0
        self.height = 1000.0
        self.safe_zone_radius = 5000.0

class MockWorld:
    def __init__(self, arena=None, boosters=None):
        self.arena = arena if arena is not None else MockArena()
        self.boosters = boosters if boosters is not None else []
        self.next_id = 100
        self.events = []

def test_cryogenic_booster():
    booster = MockEntity(x=10.0, y=10.0, kind="cryogenic_booster")
    ball = MockEntity(x=10.0, y=10.0)
    world = MockWorld(boosters=[booster], arena=MockArena(hazards=[booster]))
    action = Action(ball, world)

    # 1. Collect booster
    action._get_boosters = lambda: [booster]
    action._collect_booster(0.1)

    assert booster not in world.boosters
    assert booster not in world.arena.hazards
    assert ball.cryogenic_booster_timer == 10.0

    # 2. Attack another ball
    enemy = MockEntity(x=20.0, y=20.0, team="team2")
    action._attempt_damage(ball, enemy)

    assert getattr(enemy, "cryogenic_leak_timer", 0.0) == 5.0

    # 3. Enemy ticks and spawns ice patches
    enemy_action = Action(enemy, world)
    enemy_action.execute("idle", 0.5) # tick timer by 0.5 to spawn patch

    ice_patches = [h for h in world.arena.hazards if getattr(h, "kind", "") == "ice_patch"]
    assert len(ice_patches) == 1
    assert pytest.approx(ice_patches[0].x, abs=1.0) == enemy.x
    assert pytest.approx(ice_patches[0].y, abs=1.0) == enemy.y
