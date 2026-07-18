from ai.action import Action

class MockBall:
    def __init__(self, id=1, x=0, y=0):
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0
        self.skill = None
        self.active_skill = None
        self.damage = 10
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100

class MockHazard:
    def __init__(self):
        self.id = 100
        self.kind = "decoy_trap_booster"
        self.x = 5
        self.y = 5
        self.radius = 15.0
        self.damage = 0.0
        self.duration = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()
        self.tick = 0
        self.next_id = 9999

def test_decoy_trap_booster_collection():
    b1 = MockBall(id=1, x=0.0, y=0.0)
    world = MockWorld()
    world.balls.append(b1)

    booster = MockHazard()
    world.boosters.append(booster)
    world.arena.hazards.append(booster)

    action = Action(b1.id, world)
    action.ball = b1

    action.execute('collect_booster', 0.0) # Delta 0 to prevent timer decrement in idle fallback

    assert getattr(b1, "has_stealth_drone", False) == True
    assert getattr(b1, "stealth_drone_timer", 0.0) >= 3.0
    assert len(world.boosters) == 0
    assert len(world.arena.hazards) == 0

    decoy = [b for b in world.balls if getattr(b, "is_decoy", False)][0]
    assert decoy.decoy_type == "siren"
    assert decoy.owner_id == b1.id
