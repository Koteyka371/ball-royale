from ai.action import Action
from ai.ball_types_necromancer import Necromancer

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 9999
        self.hazards = []

class MockBall:
    def __init__(self, ball_id, ball_type, team, x, y):
        self.id = ball_id
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100

def test_necro_aura_healing():
    w = MockWorld()
    n = Necromancer(1, 0, 0)
    n.team = "A"
    n.hp = 50.0  # needs healing
    n.max_hp = 100.0

    e = MockBall(2, "warrior", "B", 50, 0)
    w.balls = [n, e]
    n.world = w

    a = Action(n, w)
    a._apply_friendly_aura(1.0) # 1 second delta

    # dealt 10 dmg to e, healed 5
    assert e.hp == 90.0
    assert n.hp == 55.0

def test_necro_aura_stacks():
    w = MockWorld()
    n = Necromancer(1, 0, 0)
    n.team = "A"
    n.hp = 100.0  # max hp, will gain stacks
    n.max_hp = 100.0
    n.bone_armor_stacks = 0

    e = MockBall(2, "warrior", "B", 50, 0)
    w.balls = [n, e]
    n.world = w

    a = Action(n, w)

    # 10 dmg -> 5 acc. Needs 15 acc for 1 stack.
    a._apply_friendly_aura(1.0)
    assert n.bone_armor_stacks == 0
    assert getattr(n, "_necro_aura_dmg_acc", 0.0) == 5.0

    a._apply_friendly_aura(1.0)
    assert n.bone_armor_stacks == 0
    assert getattr(n, "_necro_aura_dmg_acc", 0.0) == 10.0

    a._apply_friendly_aura(1.0)
    assert n.bone_armor_stacks == 1
    assert getattr(n, "_necro_aura_dmg_acc", 0.0) == 0.0
