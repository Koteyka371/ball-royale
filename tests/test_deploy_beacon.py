import math
from ai.action import Action
from arena.procedural_arena import Hazard

class DummyArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, radius):
        return x, y, False

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []
        self.tick = 100
        self.next_id = 1000
        self.time = 0.0
        self.boosters = []
        self.balls = []

    def add_combat_log(self, *args, **kwargs): pass
    def add_event(self, *args, **kwargs): pass

class DummyBall:
    def __init__(self):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.skills = ["deploy_beacon"]
        self.skill = "deploy_beacon"
        self.active_skill = "deploy_beacon"
        self.SKILL_COOLDOWN = 15.0
        self.skill_timer = 0.0
        self.base_speed = 0.0
        self.base_damage = 10.0
        self._base_speed_set = True

        # Test shield states
        self.kinetic_shield_active = True
        self.kinetic_shield_stored_damage = 50.0

def test_deploy_beacon():
    world = DummyWorld()
    ball = DummyBall()
    ball.x, ball.y = 10.0, 10.0
    world.balls.append(ball)
    action = Action(ball, world)

    # First cast: deploy beacon
    action._use_skill()
    assert getattr(ball, "active_beacon_id", None) is not None
    assert len(world.arena.hazards) == 1
    beacon = world.arena.hazards[0]
    assert getattr(beacon, "kind", "") == "recall_beacon"
    assert beacon.saved_hp == 100.0
    assert beacon.saved_shields["kinetic_shield_active"] == True
    assert beacon.saved_shields["kinetic_shield_stored_damage"] == 50.0
    assert ball.skill_timer == 0.5

    # Simulate movement, damage, and shield loss
    ball.x, ball.y = 50.0, 50.0
    ball.hp = 20.0
    ball.kinetic_shield_active = False
    ball.kinetic_shield_stored_damage = 0.0

    # Second cast: trigger recall early
    ball.skill_timer = 0.0
    action._use_skill()
    assert ball.active_beacon_id is None
    # Now the hazard duration is 0, let's run the hazard loop in execute
    action.execute("idle", 0.1)

    # Hazard should be removed and player state restored
    assert len(world.arena.hazards) == 0
    assert ball.x == 10.0
    assert ball.y == 10.0
    assert ball.hp == 100.0
    assert ball.kinetic_shield_active == True
    assert ball.kinetic_shield_stored_damage == 50.0
    assert ball.skill_timer == 15.0 - 0.1

if __name__ == "__main__":
    test_deploy_beacon()
    print("test_deploy_beacon passed.")
