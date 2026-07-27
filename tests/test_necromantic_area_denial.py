import pytest
import math
from ai.necromantic_area_denial import NecromanticAreaDenialMode, VolatilePoisonCloud

class MockBall:
    def __init__(self, id, x, y, team, hp=100.0, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = hp
        self.alive = alive
        self.skill = ""
        self.skill_active = False

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append({'type': type, 'data': data})

def test_necromantic_area_denial_creation():
    mode = NecromanticAreaDenialMode()
    world = MockWorld()

    # User with skill
    user = MockBall(1, 0, 0, "red")
    user.skill = "necromantic_denial"
    user.skill_active = True

    # Dead enemies
    dead1 = MockBall(2, 50, 50, "blue", hp=0, alive=False)
    dead2 = MockBall(3, -50, -50, "blue", hp=0, alive=False)

    # Dead ally (should not be consumed)
    dead3 = MockBall(4, 10, 10, "red", hp=0, alive=False)

    world.dead_balls = [dead1, dead2, dead3]
    balls = [user]

    mode.tick(world, balls, delta=1.0)

    assert not user.skill_active
    assert len(world.arena.hazards) == 2
    assert len(world.dead_balls) == 1
    assert world.dead_balls[0].team == "red"

    for h in world.arena.hazards:
        assert getattr(h, "kind") == "volatile_poison_cloud"
        assert getattr(h, "team") == "red"

def test_necromantic_area_denial_expansion_and_damage():
    mode = NecromanticAreaDenialMode()
    world = MockWorld()

    cloud = VolatilePoisonCloud(0, 0, "red")
    cloud.timer = 5.0 # Won't explode yet
    world.arena.hazards.append(cloud)

    # Enemy in range
    enemy1 = MockBall(1, 15, 0, "blue")

    # Enemy out of range initially
    enemy2 = MockBall(2, 30, 0, "blue")

    # Ally in range
    ally = MockBall(3, 5, 0, "red")

    balls = [enemy1, enemy2, ally]

    # Initial radius is 10, growth is 15. After 1s delta, radius is 25.
    mode.tick(world, balls, delta=1.0)

    assert world.arena.hazards[0].radius == 25.0

    # Enemy1 is at 15 distance. Should take damage (25 dps * 1s = 25 damage)
    assert enemy1.hp == 75.0

    # Enemy2 is at 30 distance. Out of radius 25.
    assert enemy2.hp == 100.0

    # Ally should take no damage
    assert ally.hp == 100.0

def test_necromantic_area_denial_explosion():
    mode = NecromanticAreaDenialMode()
    world = MockWorld()

    cloud = VolatilePoisonCloud(0, 0, "red")
    cloud.radius = 50.0
    cloud.timer = 0.5 # Explodes this tick
    world.arena.hazards.append(cloud)

    # Enemy in range
    enemy = MockBall(1, 20, 0, "blue")

    balls = [enemy]

    mode.tick(world, balls, delta=1.0)

    # Cloud removed
    assert len(world.arena.hazards) == 0

    # Enemy takes explosion damage (50) + tick damage (25 * 1.0 = 25) ?
    # Wait, in the tick it applies tick damage, then timer decreases to -0.5, then it explodes and applies explosion damage.
    # Total damage: 25 + 50 = 75.
    assert enemy.hp == 25.0

    assert len(world.events) == 1
    assert world.events[0]['type'] == 'explosion'
