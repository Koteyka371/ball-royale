import pytest
from ai.action import Action
import math

class MockEntity:
    def __init__(self, x=0, y=0, kind="", id=1):
        self.x = x
        self.y = y
        self.kind = kind
        self.id = id
        self.hp = 10
        self.max_hp = 10
        self.damage = 5
        self.team = "blue"

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards else []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, balls=None, boosters=None):
        self.balls = balls if balls else []
        self.boosters = boosters if boosters else []
        self.arena = MockArena()

def test_clone_booster_spawns_clones():
    ball = MockEntity(50, 50, id=99)
    booster = MockEntity(50, 50, kind="clone_booster")
    world = MockWorld([ball], [booster])

    action = Action(ball, world)
    action._get_boosters = lambda: [booster]

    # Trigger collect booster logic
    action._collect_booster(0.1)

    assert len(world.balls) == 3 # Original + 2 clones
    clones = [b for b in world.balls if b != ball]

    assert len(clones) == 2
    for clone in clones:
        assert clone.hp == 1.0
        assert clone.max_hp == 1.0
        assert clone.damage == 0
        assert getattr(clone, "is_decoy", False) is True
        assert getattr(clone, "intangible", False) is True
        assert getattr(clone, "is_mirroring", False) is True
        assert getattr(clone, "owner_id", None) == 99

def test_clone_booster_mirroring():
    ball = MockEntity(50, 50, id=99)
    clone1 = MockEntity(40, 40, id=100)
    clone1.alive = True
    clone1.is_mirroring = True
    clone1.is_decoy = True
    clone1.decoy_timer = 5.0
    clone1.owner_id = 99
    ball.alive = True
    world = MockWorld([ball, clone1])

    action = Action(clone1, world)

    # Should establish mirror center
    action.execute("idle", 0.1)

    assert hasattr(clone1, "mirror_center_x")
    assert math.isclose(clone1.mirror_center_x, 45.0, rel_tol=0.1)

    # Move ball
    ball.x = 60
    ball.y = 60
    action.execute("idle", 0.1)

    # Clone should mirror
    assert math.isclose(clone1.x, 30.0, rel_tol=0.1) # 45 - (60 - 45)

def test_clone_booster_decoy_timer_decrement():
    ball = MockEntity(50, 50, id=99)
    clone1 = MockEntity(40, 40, id=100)
    clone1.alive = True
    clone1.is_mirroring = True
    clone1.is_decoy = True
    clone1.decoy_timer = 5.0
    clone1.owner_id = 99
    world = MockWorld([ball, clone1])

    action = Action(clone1, world)

    action.execute("idle", 0.1)

    assert round(clone1.decoy_timer, 2) == 4.9


def test_clone_booster_takes_damage():
    ball = MockEntity(50, 50, id=99)
    clone1 = MockEntity(40, 40, id=100)
    clone1.alive = True
    clone1.is_mirroring = True
    clone1.is_decoy = True
    clone1.intangible = True
    clone1.decoy_timer = 5.0
    clone1.owner_id = 99
    world = MockWorld([ball, clone1])

    action = Action(clone1, world)

    # Take damage should make it disappear (decoy_timer = 0)
    dmg = action._attempt_damage_internal(ball, clone1)

    assert dmg == 0
    assert clone1.decoy_timer == 0
