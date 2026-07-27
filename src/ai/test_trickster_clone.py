import pytest
from ai.action import Action
from ai.ball_types_trickster import Trickster

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []

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
        self.stutter_timer = 0.0
        self.radius = 10.0
        self.inventory = []
        self.speed = 10.0
        self.damage = 10.0
        self.illusion_timer = 1.0

    def take_damage(self, dmg):
        self.hp -= dmg

def test_trickster_clone_spawns_three_decoys():
    arena = MockArena()
    owner = Trickster(1, 100, 100)
    owner.team = "teamA"
    owner.skill = "trickster_clone"

    world = MockWorld(arena, [owner])
    action = Action(owner, world)

    action._use_skill()

    # Verify 3 decoys were created
    decoys = [b for b in world.balls if getattr(b, "is_confetti_clone", False)]
    assert len(decoys) == 3

    for d in decoys:
        assert getattr(d, "is_illusion", False)
        assert getattr(d, "mimic_owner", None) == 1
        assert getattr(d, "damage", 0.0) == 0.0
        assert getattr(d, "hp", 0.0) == owner.max_hp * 0.5

def test_trickster_clone_explosion_minor_slow():
    # Target enemy
    target = MockBall(2, 100.0, 100.0, team="teamB")

    # Decoy owned by trickster
    decoy = MockBall(3, 100.0, 100.0, team="teamA")
    decoy.is_illusion = True
    decoy.is_confetti_clone = True
    decoy.hp = 0  # Trigger explosion

    arena = MockArena()
    world = MockWorld(arena, [target, decoy])
    action = Action(decoy, world)

    action.execute("idle", 0.1)

    # Decoy should be dead
    assert not decoy.alive
    assert getattr(decoy, "_illusion_exploded", False)

    # Target should NOT take damage, but SHOULD get stutter
    assert target.hp == 100.0
    assert getattr(target, "stutter_timer", 0.0) == 1.5
