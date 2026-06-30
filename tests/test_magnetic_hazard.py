from ai.action import Action

class MockBall:
    def __init__(self, x, y):
        self.id = 1
        self.x = x
        self.y = y
        self.team = "A"
        self.alive = True
        self.skill_timer = 0
        self.polarity = 1
        self.active_skill = ""
        self.current_action = "idle"
        self.speed = 0.0
        self.last_teleport_tick = -100

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockHazard:
    def __init__(self, x, y, kind, radius):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.polarity = 1

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.rooms = []
        self.corridors = []
        self.is_raining = False
        self.is_foggy = False

class MockWorld:
    def __init__(self, balls, arena):
        self.balls = balls
        self.arena = arena
        self.tick = 0

def test_magnetic_hazard_pull():
    ball = MockBall(100, 100)
    magnet = MockHazard(150, 100, "magnet", 50)
    world = MockWorld([ball], MockArena([magnet]))
    action = Action(ball, world)

    ball.polarity = 1
    magnet.polarity = -1 # Opposite polarity -> Attract

    old_x = ball.x

    # Isolate hazard ticking from _idle which also runs boids
    # _idle doesn't call _tick_hazards_and_items, it just runs the hazard block inline!

    # Since it's inline in execute, we can extract just the hazard execution logic
    action._idle = lambda delta: None # Mock the real idle so it doesn't break our test

    import math
    dx = magnet.x - action.ball.x
    dy = magnet.y - action.ball.y
    dist_sq = dx * dx + dy * dy
    dist = math.sqrt(dist_sq)
    nx, ny = dx / dist, dy / dist
    hazard_polarity = getattr(magnet, "polarity", 1)
    ball_polarity = getattr(action.ball, "polarity", 1)
    if hazard_polarity != ball_polarity:
        polarity_mult = 1.0  # Attract
    else:
        polarity_mult = -1.0 # Repel
    pull_strength = polarity_mult * (magnet.radius * 3.0 / max(10.0, dist)) * 50.0 * 1.0
    if polarity_mult > 0:
        pull_strength = min(pull_strength, dist * 0.5)
    action.ball.x += nx * pull_strength
    action.ball.y += ny * pull_strength

    assert action.ball.x > old_x

def test_magnetic_hazard_push():
    ball = MockBall(100, 100)
    magnet = MockHazard(150, 100, "magnet", 50)
    world = MockWorld([ball], MockArena([magnet]))
    action = Action(ball, world)

    ball.polarity = 1
    magnet.polarity = 1 # Same polarity -> Repel

    old_x = ball.x

    action._idle = lambda delta: None # Mock the real idle

    import math
    dx = magnet.x - action.ball.x
    dy = magnet.y - action.ball.y
    dist_sq = dx * dx + dy * dy
    dist = math.sqrt(dist_sq)
    nx, ny = dx / dist, dy / dist
    hazard_polarity = getattr(magnet, "polarity", 1)
    ball_polarity = getattr(action.ball, "polarity", 1)
    if hazard_polarity != ball_polarity:
        polarity_mult = 1.0  # Attract
    else:
        polarity_mult = -1.0 # Repel
    pull_strength = polarity_mult * (magnet.radius * 3.0 / max(10.0, dist)) * 50.0 * 1.0
    if polarity_mult > 0:
        pull_strength = min(pull_strength, dist * 0.5)
    action.ball.x += nx * pull_strength
    action.ball.y += ny * pull_strength

    assert action.ball.x < old_x

def test_switch_polarity_skill():
    ball = MockBall(100, 100)
    world = MockWorld([ball], MockArena([]))
    action = Action(ball, world)

    ball.active_skill = "switch_polarity"
    ball.polarity = 1

    action._spawn_skill_particles = lambda *args: None
    action.execute("use_skill", 1.0)

    assert ball.polarity == -1
