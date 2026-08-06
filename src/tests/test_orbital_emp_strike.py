import sys
sys.path.append("src")
from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self, x=500, y=500, score=100):
        self.id = "p1"
        self.x = x
        self.y = y
        self.radius = 15.0
        self.score = score
        self.alive = True
        self.ball_type = "player"
        self.shield_active = True
        self.stamina = 100.0
        self.speed = 100.0
        self.base_speed = 50.0
        self.damage_boost_timer = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = 1

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0
    def get(self, key, default=None):
        return getattr(self, key, default)

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(1000, 1000)
        self.events = []
        self.boosters = []
        self.balls = []
        self.width = 1000
        self.height = 1000

def test_orbital_emp_strike_collection():
    world = MockWorld()

    b1 = MockBall(500, 500)
    world.balls.append(b1)

    # Give ball a booster
    booster = MockBooster("orbital_emp_strike_item", 510, 510)
    world.boosters = [booster]

    action = Action(b1, world)
    action._get_boosters = lambda: world.boosters
    action._collect_booster(0.016)

    assert len(world.events) > 0, "No events added!"
    assert any(e.get("type") == "orbital_emp_strike" for e in world.events), "No orbital_emp_strike event"
    assert any(h.kind == "emp_strike" for h in world.arena.hazards), "No emp_strike hazard spawned"

def test_orbital_emp_strike_active_strips_buffs():
    world = MockWorld()

    b1 = MockBall(500, 500)
    world.balls.append(b1)

    # Add active EMP strike over the ball
    strike = Hazard(id=1, x=500, y=500, radius=400.0, kind="emp_strike_active", damage=0.0)
    world.arena.hazards.append(strike)

    action = Action(b1, world)
    action.execute("idle", 0.016)

    # Stamina regenerates slightly in idle, but should be close to 0
    assert b1.stamina < 1.0, f"Stamina was {b1.stamina}"
    assert getattr(b1, "shield_active", True) == False
    assert getattr(b1, "damage_boost_timer", 10.0) == 0.0

if __name__ == "__main__":
    test_orbital_emp_strike_collection()
    test_orbital_emp_strike_active_strips_buffs()
    print("ALL TESTS PASSED")
