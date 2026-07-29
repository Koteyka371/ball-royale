from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, balls=None, arena=None):
        self.balls = balls or []
        self.arena = arena or MockArena()
        self.next_id = 1

class MockBall:
    def __init__(self, x=0, y=0, ball_type="brawler"):
        self.id = id(self)
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.hp = 100
        self.damage = 10
        self.team = "team1"
        self.alive = True

    def take_damage(self, amount):
        self.hp -= amount

def test_cryogenic_booster_attack_triggers_leak():
    attacker = MockBall(0, 0, "attacker")
    target = MockBall(50, 50, "target")
    attacker.team = "team1"
    target.team = "team2"
    attacker.cryogenic_booster_timer = 5.0

    world = MockWorld([attacker, target])
    action = Action(attacker, world)

    # Try an attack
    action._attempt_damage(attacker, target)

    # Should imbue the target with a cryogenic leak
    assert hasattr(target, "cryogenic_leak_timer")
    assert target.cryogenic_leak_timer > 0.0

def test_cryogenic_leak_spawns_ice_patches():
    ball = MockBall(10, 10)
    ball.cryogenic_leak_timer = 5.0

    world = MockWorld([ball])
    action = Action(ball, world)

    # The tick logic is in _tick() which isn't available, but we can call _tick manually if we patch Action
    # Actually wait, let's just trigger the execution without testing coordinates strictly or record the coord before tick

    action.execute("idle", 0.4)
    assert len(world.arena.hazards) == 0

    # Tick exactly past 0.5s total
    old_x, old_y = ball.x, ball.y
    action.execute("idle", 0.1)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "ice_patch"

    # The hazard was spawned during the last tick, so its coordinates should be close to old_x/old_y or current ball.x/ball.y
    import math
    dist = math.hypot(world.arena.hazards[0].x - old_x, world.arena.hazards[0].y - old_y)
    dist2 = math.hypot(world.arena.hazards[0].x - ball.x, world.arena.hazards[0].y - ball.y)

    assert min(dist, dist2) < 5.0 # Just assert it spawned roughly where the ball is

    assert getattr(world.arena.hazards[0], "duration", 0) > 0
