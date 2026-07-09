import pytest
from ai.action import Action

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.events = []

class MockBall:
    def __init__(self, id, x, y, team=""):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.stun_timer = 0
        self.radius = 10.0
        self.inventory = []
        self.speed = 10.0

def test_trickster_decoys_swap():
    owner = MockBall(1, 100, 100)
    owner.id = 1
    owner.team = "teamA"
    owner.ball_type = "trickster"
    owner.decoy_swap_timer = 0.0  # trigger immediately

    decoy1 = MockBall(98, 150, 150)
    decoy1.owner_id = 1
    decoy1.is_decoy = True
    decoy1.decoy_timer = 5.0
    decoy1.is_orbiting = True
    decoy1.orbit_angle = 1.0

    decoy2 = MockBall(99, 50, 50)
    decoy2.owner_id = 1
    decoy2.is_decoy = True
    decoy2.decoy_timer = 5.0
    decoy2.is_mirroring = True

    arena = MockArena()
    world = MockWorld(arena, [owner, decoy1, decoy2])

    action = Action(owner, world)

    # Tick to trigger swap
    action.execute("idle", 0.1)

    # Positions should have swapped
    assert (decoy1.x, decoy1.y) == (50, 50)
    assert (decoy2.x, decoy2.y) == (150, 150)

    # Attributes should have swapped
    assert getattr(decoy1, "is_mirroring", False) is True
    assert getattr(decoy1, "is_orbiting", False) is False

    assert getattr(decoy2, "is_orbiting", False) is True
    assert getattr(decoy2, "is_mirroring", False) is False
    assert getattr(decoy2, "orbit_angle", 0.0) == 1.0

    # Events should have been generated
    teleports = [e for e in world.events if e.get("type") == "teleport"]
    assert len(teleports) == 2
