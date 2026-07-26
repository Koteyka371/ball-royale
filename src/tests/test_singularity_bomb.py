import pytest
from ai.game_modes import SingularityBombEventMode

class MockProjectile:
    def __init__(self, x, y, damage=20):
        self.x = x
        self.y = y
        self.damage = damage
        self.vx = 0.0
        self.vy = 0.0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.alive = True
        self.ball_type = "warrior"
        self.team = "red"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.projectiles = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

def test_singularity_bomb_spawn_and_pull():
    world = MockWorld()
    mode = SingularityBombEventMode()
    balls = [MockBall(1, 500, 500)]

    # Fast forward to spawn
    mode.event_timer = 20.0
    mode.tick(world, balls, 0.1)

    assert len(world.arena.hazards) == 1
    bomb = world.arena.hazards[0]
    assert getattr(bomb, "kind", "") == "singularity_bomb"
    assert getattr(bomb, "hp", 0) == 150.0

    # Add projectile
    proj = MockProjectile(bomb.x + 100, bomb.y)
    world.projectiles.append(proj)

    mode.tick(world, balls, 0.1)

    # Check if pulled
    assert proj.vx < 0 # Moving left towards bomb (assuming bomb.x < proj.x)

def test_singularity_bomb_absorb_and_explode():
    world = MockWorld()
    mode = SingularityBombEventMode()
    balls = [MockBall(1, 500, 500)]

    mode.event_timer = 20.0
    mode.tick(world, balls, 0.1)

    bomb = world.arena.hazards[0]
    bomb.x = 500
    bomb.y = 500

    # Add projectile right on top to absorb
    proj = MockProjectile(500, 500, damage=160.0) # Enough to kill bomb
    world.projectiles.append(proj)

    mode.tick(world, balls, 0.1)

    # Bomb should absorb and explode
    assert len(world.projectiles) == 0
    assert len(world.arena.hazards) == 0 # Bomb destroyed

    # Explosion should damage ball at 500, 500 (dist 0 -> 100 damage)
    assert balls[0].hp == 0
    assert not balls[0].alive
    assert any(e["type"] == "visual_effect" and e["data"].get("type") == "singularity_bomb_explosion" for e in world.events)
