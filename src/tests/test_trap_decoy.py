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

class MockHazard:
    def __init__(self, owner_id):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "decoy"
        self.owner_id = owner_id
        self.x = 50
        self.y = 50
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
        self.arena = MockArena()
        self.tick = 0
        self.next_id = 9999

def test_decoy_trap_spawns_decoy():
    # Setup owner and triggering ball
    owner = MockBall(id=2, x=200, y=200)
    triggering_ball = MockBall(id=1, x=45, y=45) # Close to hazard at (50, 50)

    world = MockWorld()
    hazard = MockHazard(owner_id=owner.id)
    world.arena.hazards.append(hazard)
    world.balls = [triggering_ball, owner]

    action = Action(triggering_ball, world)

    # Pre-condition: only 2 balls in world
    assert len(world.balls) == 2

    # Execute action to process hazards
    action.execute("idle", 0.1)

    # Post-condition: hazard is destroyed (duration=0), a decoy is spawned
    assert hazard.duration == 0.0

    # 5 balls: triggering_ball, owner, 3 decoys
    assert len(world.balls) == 5

    for i in range(-3, 0):
        decoy = world.balls[i]
        assert getattr(decoy, "is_decoy", False) == True
        assert decoy.decoy_type == "stun_trap"
        assert abs(decoy.x - hazard.x) <= 10.0
        assert abs(decoy.y - hazard.y) <= 10.0
        assert decoy.vx == 0.0
        assert decoy.vy == 0.0
        assert decoy.speed == 0.0
        assert decoy.id != owner.id
        assert decoy.hp == 1.0
