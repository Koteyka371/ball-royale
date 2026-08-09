
import pytest
from ai.game_modes import GAME_MODES, VolcanoBossMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []
        self.next_id = 100

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, team="player"):
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.team = team
        self.x = 100
        self.y = 100
        self.radius = 20
        self.speed = 100
        self.vx = 0
        self.vy = 0

def test_volcano_boss_setup():
    mode = GAME_MODES["volcano_boss_mode"]
    world = MockWorld()
    balls = []
    mode.setup(world, balls)

    boss = next((b for b in world.balls if getattr(b, "ball_type", "") == "volcano_boss"), None)
    assert boss is not None
    assert boss.x == 500
    assert boss.y == 500
    assert boss.hp == 5000
    assert boss.invulnerable == True
    assert boss.team == "boss"

def test_volcano_boss_tick_and_damage():
    mode = VolcanoBossMode()
    world = MockWorld()
    balls = []
    mode.setup(world, balls)

    player = MockBall(1)
    player.x = 10
    player.y = 10
    world.balls.append(player)

    # Fast forward to get water orb
    mode.item_timer = 4.0
    mode.tick(world, world.balls, 0.1)

    assert len(world.boosters) == 1
    orb = world.boosters[0]
    assert orb["kind"] == "water_orb"

    boss = next((b for b in world.balls if getattr(b, "ball_type", "") == "volcano_boss"), None)
    initial_hp = boss.hp

    # Player picks up orb
    player.x = orb["x"]
    player.y = orb["y"]

    mode.tick(world, world.balls, 0.1)

    assert boss.hp == initial_hp - 500
    assert len(world.boosters) == 0

def test_volcano_boss_hazards():
    mode = VolcanoBossMode()
    world = MockWorld()
    balls = []
    mode.setup(world, balls)

    mode.attack_timer = 3.0
    mode.geyser_timer = 6.0
    mode.tick(world, world.balls, 0.1)

    hazards = world.arena.hazards
    assert len(hazards) > 0
    assert any(getattr(h, "kind", "") == "lava_projectile" for h in hazards)
    assert any(getattr(h, "kind", "") == "lava_geyser" for h in hazards)
