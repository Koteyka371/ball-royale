from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.rooms = []
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.arena = MockArena()
        self.balls = []
        self.events = []

    def add_event(self, type_, data):
        self.events.append({"type": type_, "data": data})

class MockBall:
    def __init__(self, id, x=0, y=0, team="red", ball_type="scout"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.alive = True
        self.skill_timer = 0.0
        self.bounty_contract_xp_reward = 500
        self.active_skill = "bounty_trap"
        self.bounty_trap_variant = "default"
        self.stun_timer = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0

class MockHazard:
    def __init__(self, x=0, y=0, radius=20.0, team="red", active=True, owner_id=1, kind="bounty_trap", duration=60.0, variant="default"):
        self.x = x
        self.y = y
        self.radius = radius
        self.team = team
        self.active = active
        self.owner_id = owner_id
        self.kind = kind
        self.duration = duration
        self.variant = variant

def test_bounty_trap_explosive_deployment():
    world = MockWorld()
    ball = MockBall(1, 0, 0, team="red")
    ball.bounty_trap_variant = "explosive"
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    assert len(world.arena.hazards) > 0
    trap = world.arena.hazards[-1]
    assert getattr(trap, "kind", "") == "bounty_trap"
    assert getattr(trap, "variant", "") == "explosive"

def test_bounty_trap_explosive_trigger():
    world = MockWorld()
    ball1 = MockBall(1, 0, 0, team="red")
    ball2 = MockBall(2, 5, 0, team="blue")
    world.balls = [ball1, ball2]

    hazard = MockHazard(x=5, y=0, team="red", owner_id=1, variant="explosive")
    world.arena.hazards.append(hazard)

    action = Action(ball2, world)
    action.execute("idle", 0.016)

    # Check that ball2 was marked as bounty
    assert getattr(ball2, "is_bounty_target", False) == True

    # Check explosion event
    events = [e for e in world.events if e["type"] == "explosion"]
    assert len(events) == 1
    assert events[0]["data"]["damage"] == 50.0

    # Check damage on ball2
    assert ball2.hp == 50.0 # 100 - 50

def test_bounty_trap_stasis_trigger():
    world = MockWorld()
    ball1 = MockBall(1, 0, 0, team="red")
    ball2 = MockBall(2, 5, 0, team="blue")
    world.balls = [ball1, ball2]

    hazard = MockHazard(x=5, y=0, team="red", owner_id=1, variant="stasis")
    world.arena.hazards.append(hazard)

    action = Action(ball2, world)
    action.execute("idle", 0.016)

    # Check that ball2 was marked as bounty
    assert getattr(ball2, "is_bounty_target", False) == True

    # Check stasis (stun_timer)
    assert getattr(ball2, "stun_timer", 0.0) >= 3.0
