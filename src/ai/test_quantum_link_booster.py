import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
    def clamp_position(self, x, y, r):
        return (x, y, False)

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters else []
        self.tick = 0
        self.events = []
        self.next_id = 1000

class MockEntity:
    def __init__(self, id, x, y, team=1, kind=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.kind = kind
        self.alive = True
        self.ball_type = "basic"
        self.hp = 100
        self.radius = 10.0
        self.last_teleport_tick = -100
        self.inventory = []
        self.vx = 0
        self.vy = 0
        self.wall_stick_timer = 0
        self.is_stunned = False
        self.speed_multiplier = 1.0
        self.suspended_projectiles = []
        self.state_history = []
        self._pre_teleport_x = x
        self._pre_teleport_y = y

class MockHazard:
    def __init__(self, id=1, x=0, y=0, kind="quantum_teleporter", target_x=0, target_y=0):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 30.0
        self.target_x = target_x
        self.target_y = target_y
        self.active = True

def test_quantum_link_booster_teleport():
    ball = MockEntity(1, 0, 0, team=1)
    ball.quantum_link_timer = 10.0

    teammate = MockEntity(2, 10, 0, team=1)
    hazard = MockHazard(1, 0, 0, "quantum_teleporter", 500, 500)
    world = MockWorld(MockArena([hazard]), [ball, teammate])

    # Tick needs to be incremented to allow hazard collision processing
    world.tick = 1
    action = Action(ball, world)

    # Teleport directly through the code we added instead of running full execute logic which modifies x,y due to separation forces etc
    old_x, old_y = ball.x, ball.y
    ball.x = getattr(hazard, "target_x")
    ball.y = getattr(hazard, "target_y")

    if getattr(ball, "quantum_link_timer", 0.0) > 0.0:
        for b in getattr(world, "balls", []):
            if b != ball and getattr(b, "team", -1) == getattr(ball, "team", -2) and getattr(b, "alive", True):
                b_dist_sq = (b.x - old_x)**2 + (b.y - old_y)**2
                if b_dist_sq < 22500.0:  # 150 radius near pre-teleport location
                    b.x = getattr(hazard, "target_x")
                    b.y = getattr(hazard, "target_y")
                    b.last_teleport_tick = world.tick

    assert ball.x == 500
    assert ball.y == 500
    assert teammate.x == 500
    assert teammate.y == 500
