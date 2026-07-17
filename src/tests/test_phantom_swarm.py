import pytest
from ai.game_modes import GAME_MODES, PhantomSwarmMode

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 10.0
        self.vy = 5.0
        self.alive = True
        self.is_decoy = False
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "A"
        self.ball_type = "basic"

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.next_id = 1000
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

def test_phantom_swarm_spawning():
    mode = GAME_MODES["phantom_swarm"]
    world = MockWorld()

    player1 = MockBall(1, 100.0, 100.0)
    world.balls.append(player1)

    mode.setup(world, world.balls)

    # Tick for 15 seconds to trigger spawn
    for _ in range(int(15.0 / 0.1) + 1):
        mode.tick(world, world.balls, 0.1)

    # Spawn happens at 15.0 seconds
    assert len(world.balls) > 1, "Phantoms should be spawned"

    phantoms = [b for b in world.balls if getattr(b, "kind", "") == "phantom_decoy"]
    assert len(phantoms) > 0, "There should be at least one phantom"

    phantom = phantoms[0]
    assert phantom.is_decoy == True
    assert phantom.hp == 1.0
    assert phantom.vx == 10.0
    assert phantom.vy == 5.0

def test_phantom_swarm_movement():
    mode = GAME_MODES["phantom_swarm"]
    world = MockWorld()
    player1 = MockBall(1, 100.0, 100.0)
    world.balls.append(player1)
    mode.setup(world, world.balls)

    for _ in range(int(15.0 / 0.1) + 1):
        mode.tick(world, world.balls, 0.1)

    phantoms = [b for b in world.balls if getattr(b, "kind", "") == "phantom_decoy"]
    phantom = phantoms[0]

    init_x = phantom.x
    init_y = phantom.y

    # Tick to update phantom
    mode.tick(world, world.balls, 1.0)

    assert phantom.x == init_x + 10.0
    assert phantom.y == init_y + 5.0

def test_phantom_swarm_dissipation():
    mode = GAME_MODES["phantom_swarm"]
    world = MockWorld()

    player1 = MockBall(1, 100.0, 100.0)
    world.balls.append(player1)

    mode.setup(world, world.balls)

    # Force spawn
    mode.timer = 15.0
    mode.tick(world, world.balls, 0.1)

    phantoms = [b for b in world.balls if getattr(b, "kind", "") == "phantom_decoy"]
    phantom = phantoms[0]

    assert phantom.alive == True

    # Take damage
    phantom.take_damage(10.0)

    assert phantom.hp == 0.0
    assert phantom.alive == False

    # Next tick it should be removed
    mode.tick(world, world.balls, 0.1)
    assert phantom not in world.balls
