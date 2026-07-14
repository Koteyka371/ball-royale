import sys
sys.path.insert(0, 'src')
from ai.action import Action
from ai.ball_types_scavenger import Scavenger

class MockBooster:
    def __init__(self, x, y, kind="hp_booster"):
        self.x = x
        self.y = y
        self.kind = kind
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.events = []

    def _deal_damage(self, attacker, target):
        pass

    def _collect_booster(self, ball, bst):
        self.boosters.remove(bst)

def test_scavenger_collect_booster():
    ball = Scavenger(1, 0, 0)
    ball.damage = 8.0

    booster = MockBooster(0, 5, "hp_booster")
    world = MockWorld()
    world.balls = [ball]
    world.boosters = [booster]

    action = Action(ball, world)
    # The default behavior for scavengers isn't explicitly tested unless we trigger the booster logic
    action.execute("collect_booster", 1.0)

    assert getattr(ball, "materials_collected", 0) == 1
    assert ball.max_hp == 95.0
    assert ball.hp == 95.0
    assert ball.damage == 9.0
    assert len(world.boosters) == 0
