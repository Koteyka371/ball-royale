import pytest
from ai.action import Action
from ai.ball_types_decoy_master import DecoyMaster

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
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball and getattr(b, "team", "") != getattr(ball, "team", "")],
                "allies": [b for b in self.balls if b != ball and getattr(b, "team", "") == getattr(ball, "team", "")]}

def test_decoy_master_skill():
    world = MockWorld()
    master = DecoyMaster(1, 100.0, 100.0)
    master.team = "teamA"

    world.balls.append(master)

    action = Action(master, world)
    master.skill_timer = 0
    action.execute("use_skill", 0.1)

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) == 3

    decoy_types = [getattr(d, "decoy_type", "") for d in decoys]
    assert "explosive" in decoy_types
    assert "stun_trap" in decoy_types
    assert "healing" in decoy_types

def test_healing_decoy_explosion():
    from ai.test_action_advanced import MockBall

    world = MockWorld()

    decoy = MockBall(x=100, y=100)
    decoy.is_decoy = True
    decoy.alive = True
    decoy.hp = 0
    decoy.decoy_type = "healing"
    decoy.team = "teamA"
    decoy.decoy_timer = 5.0
    decoy.id = 999

    ally = MockBall(x=120, y=100)
    ally.team = "teamA"
    ally.hp = 50.0
    ally.max_hp = 100.0
    ally.id = 2

    enemy = MockBall(x=90, y=100)
    enemy.team = "teamB"
    enemy.hp = 100.0
    enemy.id = 3

    world.balls = [decoy, ally, enemy]

    action = Action(ally, world)
    action.execute("idle", 0.1)

    assert getattr(decoy, "_decoy_exploded", False) is True
    assert ally.hp == 80.0 # Healed by 30
    assert enemy.hp == 100.0 # Enemies are not affected by healing decoys
