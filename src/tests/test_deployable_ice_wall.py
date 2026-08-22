import pytest
from ai.action import Action

class MockBall:
    def __init__(self, x=100, y=100):
        self.id = 1
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_max_speed = 100
        self.perception_radius = 500
        self.alive = True
        self.team = "A"
        self.in_mirror_dimension = False
        self.BALL_TYPE = "normal"
        self.stealth_drone_timer = 0
        self.is_disguised = False
        self.chameleon_hidden = False
        self.stealth_booster_timer = 0
        self.radius = 10.0
        self.inventory = []
        self.speed_multiplier = 1.0

class MockHazard:
    def __init__(self, x, y, kind="deployable_ice_wall"):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 15.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.projectiles = []

def test_deploy_ice_wall():
    ball = MockBall(100, 100)
    ball.inventory = ["deployable_ice_wall"]
    enemy = MockBall(150, 100)
    enemy.id = 2
    enemy.team = "B"

    world = MockWorld()
    world.balls = [ball, enemy]
    action = Action(ball, world)
    action._get_enemies = lambda: [enemy]
    action._get_enemies_internal = lambda: [enemy]

    action.execute("attack", 0.1)

    # Check if wall was deployed
    print(world.arena.hazards, ball.inventory, enemy.x)
    assert len(world.arena.hazards) == 1
    wall = world.arena.hazards[0]
    assert getattr(wall, "kind", "") == "ice_wall"
    assert getattr(wall, "owner_id", None) == 1
    assert "deployable_ice_wall" not in ball.inventory

def test_ice_wall_mechanics():
    ball = MockBall(100, 100)
    enemy = MockBall(105, 100) # Close enough to be pushed
    enemy.id = 2
    enemy.team = "B"

    world = MockWorld()
    world.balls = [ball, enemy]
    action = Action(ball, world)
    action._get_enemies = lambda: [enemy]
    action._get_enemies_internal = lambda: [enemy]

    # Add an ice wall owned by ball 1
    wall = MockHazard(100, 100, "ice_wall")
    setattr(wall, "owner_id", 1)
    setattr(wall, "wall_dx", 1.0)
    setattr(wall, "wall_dy", 0.0)
    setattr(wall, "wall_width", 100.0)
    setattr(wall, "duration", 1.0)
    setattr(wall, "hp", 100.0)
    world.arena.hazards.append(wall)

    # Process for enemy
    action = Action(enemy, world)
    action.execute("idle", 0.1)

    # Enemy should be pushed away and wall takes damage
    assert enemy.x > 105 or enemy.x < 105 or enemy.y != 100
    assert getattr(wall, "hp") < 100.0

def test_ice_wall_shatter():
    ball = MockBall(100, 100)

    world = MockWorld()
    world.balls = [ball]

    wall = MockHazard(100, 100, "ice_wall")
    setattr(wall, "owner_id", 2) # Owned by enemy
    setattr(wall, "wall_dx", 1.0)
    setattr(wall, "wall_dy", 0.0)
    setattr(wall, "wall_width", 100.0)
    setattr(wall, "duration", 0.1) # Will expire soon
    setattr(wall, "hp", 1.0) # Will melt soon
    world.arena.hazards.append(wall)

    action = Action(ball, world)
    action.execute("idle", 0.2)

    # Wall should be shattered into 8 shrapnel pieces
    assert len(world.arena.hazards) >= 8
    shrapnels = [h for h in world.arena.hazards if getattr(h, "kind", "") == "ice_wall_shrapnel"]
    assert len(shrapnels) == 8

def test_ice_wall_shrapnel_slow():
    ball = MockBall(100, 100)

    world = MockWorld()
    world.balls = [ball]

    shrapnel = MockHazard(110, 100, "ice_wall_shrapnel") # Close enough (dist=10 < 50)
    setattr(shrapnel, "owner_id", 2) # Owned by enemy
    setattr(shrapnel, "duration", 4.0)
    world.arena.hazards.append(shrapnel)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Shrapnel slows the ball
    assert ball.speed_multiplier <= 0.6
