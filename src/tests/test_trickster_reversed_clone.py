import pytest
from ai.action import Action
from ai.ball_types_trickster import Trickster

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.clamp_position = lambda x,y,r: (x,y,False)

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.entities = balls
        self.boosters = arena.hazards
        self.next_id = 1000

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

def test_trickster_reversed_clone_spawns():
    arena = MockArena()
    owner = Trickster(1, 100, 100)
    owner.team = "teamA"
    owner.skill = "reversed_trickster_clone"

    world = MockWorld(arena, [owner])
    action = Action(owner, world)

    action._use_skill()

    # Verify taunt decoy was created
    decoys = [b for b in world.balls if getattr(b, "is_decoy_clone", False) and getattr(b, "decoy_type", "") == "taunt"]
    assert len(decoys) == 1

    decoy = decoys[0]
    assert getattr(decoy, "is_illusion", False)
    assert getattr(decoy, "mimic_owner", None) == 1
    assert getattr(decoy, "damage", 0.0) == 0.0
    assert getattr(decoy, "hp", 0.0) == owner.max_hp * 0.5
    assert getattr(decoy, "is_mirroring", False) == True

def test_taunt_targeting():
    enemy = MockBall(1, 0, 0, team="teamA")
    target = MockBall(2, 50, 0, team="teamB")
    taunt = MockBall(3, 100, 0, team="teamB")
    taunt.is_decoy = True
    taunt.decoy_type = "taunt"

    world = MockWorld(MockArena(), [enemy, target, taunt])
    action = Action(enemy, world)

    selected_target = action._get_target([target, taunt])
    assert selected_target.id == 3
