from ai.action import Action
import pytest
import math

class MockBall:
    def __init__(self, id=1, x=0.0, y=0.0, team="team1"):
        self.id = id
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.ball_type = "basic"
        self.speed = 100.0
        self.base_speed = 100.0
        self.radius = 15.0
        self.skill = None
        self.active_skill = None
        self.damage = 10.0
        self.minimap_ping_timer = 0.0
        self.state_history = []
        self.last_teleport_tick = -100

class MockHazard:
    def __init__(self, owner_id):
        self.id = 100
        self.kind = "trap"
        self.trap_variant = "decoy"
        self.owner_id = owner_id
        self.x = 50.0
        self.y = 50.0
        self.radius = 15.0
        self.damage = 0.0
        self.duration = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 0
        self.next_id = 9999
        self.events = []
    def _deal_damage(self, attacker, target, dmg=None):
        pass # mock damage

def test_hologram_trap_spawns_3_clones():
    # Setup owner and triggering ball
    owner = MockBall(id=2, x=200, y=200, team="team2")
    triggering_ball = MockBall(id=1, x=45, y=45, team="team1") # Close to hazard at (50, 50)

    world = MockWorld()
    hazard = MockHazard(owner_id=owner.id)
    world.arena.hazards.append(hazard)
    world.balls = [triggering_ball, owner]

    action = Action(triggering_ball.id, world)
    action.ball = triggering_ball

    # Execute action to process hazards
    action.execute("idle", 0.1)

    # Post-condition: hazard is destroyed (duration=0), 3 clones are spawned
    assert hazard.duration == 0.0

    # 5 balls: triggering_ball, owner, +3 clones
    assert len(world.balls) == 5

    clones = [b for b in world.balls if getattr(b, "is_trap_hologram", False)]
    assert len(clones) == 3

    for clone in clones:
        assert clone.is_hologram is True
        assert clone.clone_owner == triggering_ball.id
        assert clone.hp == 100.0
        assert clone.damage == 0.0
        assert clone.id != owner.id
        assert clone.id != triggering_ball.id

def test_hologram_feedback_damage():
    world = MockWorld()
    enemy = MockBall(id=3, x=100.0, y=100.0, team="team2")
    enemy.hp = 100.0

    hologram = MockBall(id=4, x=110.0, y=100.0, team="team1")
    hologram.is_trap_hologram = True
    hologram.damage = 0.0

    world.balls.extend([enemy, hologram])

    action = Action(enemy.id, world)
    action.ball = enemy

    # Manually attempt damage
    action._attempt_damage_internal(enemy, hologram)

    assert enemy.minimap_ping_timer == 3.0
    assert enemy.hp == 95.0 # Feedback damage
    assert hologram.hp == 100.0 # Hologram shouldn't take damage in the damage handler logic we added
