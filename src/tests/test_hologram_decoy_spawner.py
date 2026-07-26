import pytest
from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = []
        self.events = []

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius

class MockBall:
    def __init__(self, id, x, y, ball_type="warrior", alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.ball_type = ball_type
        self.alive = alive
        self.is_decoy = False

def test_decoy_spawner():
    mode = GAME_MODES["battle_royale"]
    world = MockWorld()
    hazard = MockHazard("decoy_spawner", 500, 500, 100)
    world.arena.hazards.append(hazard)

    player1 = MockBall(1, 510, 510, "warrior")
    player2 = MockBall(2, 900, 900, "mage")
    world.balls.extend([player1, player2])

    # Reset internal state to avoid flaky test issues
    mode.weather = "clear"
    mode.time_survived = 0.0

    # Tick to spawn decoy
    mode.tick(world, world.balls, 3.1)

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) == 1, "Should spawn one decoy"
    decoy = decoys[0]

    assert getattr(decoy, "is_hologram_decoy", False) is True, "Should be a hologram"
    assert getattr(decoy, "ball_type", "") == "warrior", "Should mimic nearby player1's type"
    assert getattr(decoy, "owner_id", None) == 1, "Should be owned by player1"
    assert decoy.x == hazard.x and decoy.y == hazard.y, "Should spawn at hazard position"
