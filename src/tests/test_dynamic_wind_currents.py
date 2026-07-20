import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True, is_projectile=False):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.max_hp = 100
        self.hp = 100
        self.damage = 10
        self.vx = 0.0
        self.vy = 0.0
        self.is_projectile = is_projectile
        self.max_stamina = 100
        self.stamina = 100
        self.base_speed = 100
        self.speed = 100
        self.base_damage = 10
        self.original_base_damage = 10
        self.traits = []
        self.weather_immunity_timer = 0.0
        self.in_mirror_dimension = False
        self.intangible = False
        self.vision_radius = 50.0
        self.invisible = False
        self.team = "team1"

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

def test_dynamic_wind_currents():
    mode = GAME_MODES.get("dynamic_wind_currents")
    assert mode is not None, "Mode not registered!"

    world = MockWorld()
    warrior = MockBall(1)
    spectator = MockBall(3, "spectator")
    dead = MockBall(4, alive=False)
    balls = [warrior, spectator, dead]

    projectile = MockBall(2, "projectile", alive=True, is_projectile=True)
    world.projectiles = [projectile]

    mode.setup(world, balls)
    assert mode.wind_timer == 15.0

    # Tick with large delta to trigger timer reset
    mode.wind_timer = 0.1
    mode.tick(world, balls, 0.2)

    assert mode.wind_timer > 0.1 # Has been reset

    # Verify vx and vy are updated for alive balls and projectiles, but not spectator or dead
    assert warrior.vx != 0.0 or warrior.vy != 0.0
    assert projectile.vx != 0.0 or projectile.vy != 0.0
    assert spectator.vx == 0.0 and spectator.vy == 0.0
    assert dead.vx == 0.0 and dead.vy == 0.0

    assert math.isclose(warrior.vx, projectile.vx)
    assert math.isclose(warrior.vy, projectile.vy)

if __name__ == "__main__":
    test_dynamic_wind_currents()
