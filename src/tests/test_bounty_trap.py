from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.rooms = []

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

class MockHazard:
    def __init__(self, x=0, y=0, radius=20.0, team="red", active=True, owner_id=1, kind="bounty_trap", duration=60.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.team = team
        self.active = active
        self.owner_id = owner_id
        self.kind = kind
        self.duration = duration

def test_bounty_trap_skill_activation():
    world = MockWorld()
    ball = MockBall(1, 0, 0, team="red")
    world.balls = [ball]

    action = Action(ball, world)
    action._use_skill()

    assert len(world.arena.hazards) > 0
    trap = world.arena.hazards[-1]
    assert getattr(trap, "kind", "") == "bounty_trap"
    assert getattr(trap, "team", "") == "red"
