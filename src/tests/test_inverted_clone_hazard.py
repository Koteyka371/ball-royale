import pytest
from ai.game_modes import InvertedCloneHazardMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 20.0
        self.alive = True
        self.radius = 15.0
        self.max_hp = 100.0

def test_inverted_clone_hazard():
    mode = InvertedCloneHazardMode()
    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    world.balls.append(b1)
    world.entities.append(b1)

    mode.setup(world, world.balls)
    assert len(world.arena.hazards) == 1

    hazard = world.arena.hazards[0]
    assert hazard.kind == "inverted_clone_hazard"

    # Move ball into hazard
    b1.x = hazard.x
    b1.y = hazard.y

    # Tick to spawn clone
    mode.tick(world, world.balls, 0.016)

    # Clone should be spawned
    clones = [b for b in world.balls if getattr(b, "is_inverted_clone", False)]
    assert len(clones) == 1

    clone = clones[0]
    assert clone.inverted_clone_owner == 1
    assert clone.team == 999

    # Tick again to make sure it doesn't spawn another clone for the same ball
    mode.tick(world, world.balls, 0.016)
    clones = [b for b in world.balls if getattr(b, "is_inverted_clone", False)]
    assert len(clones) == 1

def test_inverted_clone_early_return():
    import ai.action as action

    world = MockWorld()
    b1 = MockBall(1, 500, 500)
    world.balls.append(b1)

    clone = MockBall(2, 500, 500)
    clone.is_inverted_clone = True
    clone.inverted_clone_owner = 1
    world.balls.append(clone)

    act = action.Action(clone, world)
    act.execute("aggressive", 0.016)

    # Assert inverted velocity
    assert clone.vx == -10.0
    assert clone.vy == -20.0
