import pytest

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, arena, boosters, balls):
        self.arena = arena
        self.boosters = boosters
        self.balls = balls
        self.next_id = 9000

class MockBall:
    def __init__(self, x, y, vx, vy, speed):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = speed
        self.intangible = False
        self.intangible_timer = 0.0

class MockBooster(dict):
    def __init__(self, x, y, kind):
        super().__init__()
        self['x'] = x
        self['y'] = y
        self['kind'] = kind
        self.x = x
        self.y = y
        self.kind = kind

class MockAction:
    def __init__(self, ball, world):
        self.ball = ball
        self.world = world
    def _idle(self, delta):
        pass
    def _get_boosters(self):
        return self.world.boosters
    def _get_enemies(self):
        return []
    def _apply_obstacle_avoidance(self, nx, ny, nearest, ignore_enemies=False):
        return nx, ny
    def _apply_boid_rules(self, nx, ny):
        return nx, ny

def test_mirage_booster_spawns_clones():
    import sys
    import os
    sys.path.append(os.path.abspath("src"))
    from ai.action import Action
    from ai.game_modes import GameMode

    ball = MockBall(50, 50, 10, 0, 100)
    booster = MockBooster(50, 50, "mirage_booster")
    world = MockWorld(MockArena([]), [booster], [ball])

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._apply_obstacle_avoidance = lambda nx, ny, nearest, ignore_enemies=False: (nx, ny)
    action._apply_boid_rules = lambda nx, ny: (nx, ny)

    # Distance will be 0, so it will collect the booster immediately
    action._collect_booster(0.016)

    assert len(world.balls) == 3
    clones = [b for b in world.balls if getattr(b, "is_clone", False)]
    assert len(clones) == 2

    c1, c2 = clones
    assert c1.intangible
    assert c2.intangible
    assert c1.clone_timer == 5.0
    assert c2.clone_timer == 5.0
    assert c1.hp == 1
    assert c2.hp == 1
    assert c1.damage == 0.0

    assert c1.vx == 10
    assert c1.vy == 0
    assert c2.vx == -10
    assert c2.vy == 0

def test_mirage_booster_gamemode_tick():
    import sys
    import os
    sys.path.append(os.path.abspath("src"))
    from ai.game_modes import GameMode

    ball = MockBall(50, 50, 10, 0, 100)

    c1 = MockBall(50, 50, 10, 0, 100)
    c1.is_clone = True
    c1.clone_timer = 5.0
    c1.alive = True
    c1.hp = 1

    c2 = MockBall(50, 50, -10, 0, 100)
    c2.is_clone = True
    c2.clone_timer = 0.01
    c2.alive = True
    c2.hp = 1

    balls = [ball, c1, c2]

    gm = GameMode()
    gm.apply_dynamic_traits(None, balls, 0.016)

    assert c1.clone_timer < 5.0
    assert c1.alive == True

    assert c2.clone_timer < 0
    assert c2.alive == False
    assert c2.hp == 0
