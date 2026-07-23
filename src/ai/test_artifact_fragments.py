import pytest
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.ball_type = "normal"
        self.max_hp = 100.0
        self.hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.items = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def add_event(self, kind, data):
        self.events.append((kind, data))

def test_artifact_fragments():
    mode = GAME_MODES["artifact_fragments"]
    world = MockWorld()
    b = MockBall(1, 500.0, 500.0)
    balls = [b]

    # Fast forward to spawn
    mode.fragment_spawn_timer = 0.0
    mode.tick(world, balls, delta=0.016)

    assert len(world.arena.items) == 1
    frag = world.arena.items[0]

    # Move fragment to ball
    frag["x"] = b.x
    frag["y"] = b.y

    # Collect 1
    mode.tick(world, balls, delta=0.016)
    assert len(world.arena.items) == 0
    assert hasattr(b, "artifact_fragments")
    art_type = frag["artifact_type"]
    assert b.artifact_fragments[art_type] == 1

    # Collect 2 more manually
    world.arena.items.append(frag.copy())
    world.arena.items[-1]["active"] = True
    mode.tick(world, balls, delta=0.016)

    world.arena.items.append(frag.copy())
    world.arena.items[-1]["active"] = True
    mode.tick(world, balls, delta=0.016)

    assert b.artifact_fragments[art_type] == 0 # Reset after 3
    assert hasattr(b, "completed_artifacts")
    assert art_type in b.completed_artifacts

    if art_type == "aegis_shield":
        assert b.max_hp == 150.0
    elif art_type == "hermes_boots":
        assert b.speed == 130.0


def test_artifact_active_ability():
    from ai.action import Action
    world = MockWorld()
    b = MockBall(1, 500.0, 500.0)
    b.completed_artifacts = ["aegis_shield"]
    world.balls = [b]

    action = Action(b, world)
    action.execute("use_artifact", 0.016)

    assert getattr(b, "invulnerable_timer", 0.0) >= 3.0
    assert getattr(b, "artifact_aegis_cd", 0.0) == 15.0


def test_artifact_cooldown():
    from ai.game_modes import GAME_MODES
    world = MockWorld()
    b = MockBall(1, 500.0, 500.0)
    b.artifact_aegis_cd = 15.0
    world.balls = [b]

    mode = GAME_MODES["artifact_fragments"]
    mode.tick(world, world.balls, 1.0)

    assert b.artifact_aegis_cd == 14.0
