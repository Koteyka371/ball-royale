import pytest
from ai.action import Action
from ai.ball_types_illusionist import Illusionist

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.safe_zone_x = 500
        self.safe_zone_y = 500
        self.safe_zone_radius = 5000

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls if balls is not None else []
        self.next_id = 1000
        self.arena = MockArena()
        self.time = 0
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball and getattr(b, "team", "") != getattr(ball, "team", "")]}

def test_illusionist_mass_illusion():
    world = MockWorld()
    illusionist = Illusionist(1, 100.0, 100.0)
    illusionist.team = "teamA"

    world.balls.append(illusionist)

    action = Action(illusionist, world)

    # Test use skill
    illusionist.skill_timer = 0
    action.execute("use_skill", 0.1)

    # Verify 3 clones are created
    clones = [b for b in world.balls if getattr(b, "is_active_clone", False)]
    assert len(clones) == 3

    # Verify clones have reduced hp and damage
    for clone in clones:
        assert clone.hp == 45.0  # 90 * 0.5
        assert clone.damage == getattr(illusionist, "damage", 10) * 0.5
        assert clone.is_illusion == True
        assert clone.mimic_owner == 1
        assert clone.mimic_timer == 10.0

def test_active_clone_mimics_owner():
    world = MockWorld()

    owner = Illusionist(1, 100.0, 100.0)
    owner.team = "teamA"
    owner.current_action = "attack"

    clone = Illusionist(2, 100.0, 100.0)
    clone.team = "teamA"
    clone.speed = 6.0
    clone.base_speed = 6.0
    clone._base_speed_set = True
    clone.is_active_clone = True
    clone.mimic_owner = 1
    clone.mimic_timer = 10.0
    clone.current_action = "idle"  # Will be overridden

    target = Illusionist(3, 100.0, 150.0)  # Close enemy
    target.team = "teamB"

    world.balls.extend([owner, clone, target])

    action = Action(clone, world)
    action.execute("idle", 1.0)  # Even if clone tries to idle, it should mimic owner and attack

    # Since clone copied "attack" from owner, and enemy is at (100, 150),
    # clone should move towards (100, 150), so y should increase
    assert clone.y > 100.0
    assert clone.mimic_timer < 10.0
