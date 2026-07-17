import pytest
from ai.game_modes import ExtremeWeatherMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []
        self.next_id = 1000
        self.balls = []

class MockEntity:
    def __init__(self, id, name, team, x, y):
        self.id = id
        self.name = name
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.radius = 10.0

def test_starlight_boss_tracking_projectile():
    world = MockWorld()
    mode = ExtremeWeatherMode()
    mode.current_weather = "celestial_alignment"

    boss = MockEntity(1, "Starlight Boss", "boss", 500, 500)
    boss.starlight_fire_timer = 0.0

    player1 = MockEntity(2, "Player1", "red", 600, 500)

    world.balls = [boss, player1]

    # Tick 1: Boss should fire a projectile
    mode.tick(world, world.balls, 0.1)

    # Projectile should be spawned
    assert len(world.arena.hazards) == 1
    proj = world.arena.hazards[0]
    assert getattr(proj, "kind", "") == "starlight_projectile"
    assert getattr(proj, "target_id", None) == 2
    assert getattr(boss, "starlight_fire_timer", 0.0) > 0.0

    # Check that projectile moved towards target (player is at 600,500, projectile started at 500,500)
    # move_dist = 200 * delta = 20
    assert proj.x == 520
    assert proj.y == 500

    # Tick again to move it closer
    # We set boss fire timer > 0 so it doesn't fire again
    boss.starlight_fire_timer = 1.0

    mode.tick(world, world.balls, 0.1)
    assert proj.x == 540
    assert len(world.arena.hazards) == 1

    # Force collision
    proj.x = 590
    mode.tick(world, world.balls, 0.1)

    # It hits player1
    assert player1.hp < 100
    assert len(world.arena.hazards) == 0
