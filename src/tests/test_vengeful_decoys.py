import pytest
from ai.game_modes import GAME_MODES, VengefulDecoysMode

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.alive = True
        self.is_decoy = False
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "A"
        self.ball_type = "basic"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000

def test_vengeful_decoys_creation_and_properties():
    mode = GAME_MODES["vengeful_decoys"]
    world = MockWorld()

    player1 = MockBall(1, 100.0, 100.0)
    world.balls.append(player1)

    mode.setup(world, world.balls)

    # Tick for 10 seconds
    for _ in range(int(10.0 / 0.016) + 1):
        player1.x += 1.0 * 0.016
        mode.tick(world, world.balls, 0.016)

    assert len(world.balls) == 2, "Decoy should be created"

    decoy = world.balls[1]
    assert decoy.is_decoy == True
    assert decoy.kind == "vengeful_decoy"
    assert decoy.half_reflect_shield_active == True, "Decoy must have 50% damage reflect"
    assert decoy.hp == 100.0
    assert decoy.owner_id == 1

def test_vengeful_decoy_path_replay():
    mode = GAME_MODES["vengeful_decoys"]
    world = MockWorld()

    player1 = MockBall(1, 0.0, 0.0)
    world.balls.append(player1)

    mode.setup(world, world.balls)

    # Move player for 10.1 seconds (just over decoy interval)
    for i in range(101):
        player1.x = i * 2.0
        mode.tick(world, world.balls, 0.1)

    # Find decoy
    decoy = next((b for b in world.balls if getattr(b, "is_decoy", False)), None)
    assert decoy is not None

    # Simulate time for decoy
    decoy.update(0.5)
    assert decoy.x > 0.0 # Decoy should be following path
