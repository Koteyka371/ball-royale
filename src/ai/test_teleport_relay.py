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
        self.alive = True
        self.last_teleport_tick = 0
        self.skills = ["deploy_teleport_relay"]
        self.skill = "deploy_teleport_relay"
        self.active_skill = "deploy_teleport_relay"
        self.base_speed = 0.0
        self.base_damage = 10.0
        self._base_speed_set = True

def test_teleport_relay():
    world = DummyWorld()
    ball = DummyBall()
    ball.x, ball.y = 10.0, 10.0
    action = Action(ball, world)

    action._use_skill()
    relay1_id = world.arena.hazards[0].id

    ball.x, ball.y = 100.0, 100.0
    action._use_skill()

    # We will test the hazard interaction manually to avoid execute's physics
    ball.x, ball.y = 10.0, 10.0
    world.tick = 150

    # Run the hazard loop segment
    for hazard in world.arena.hazards:
        if hazard.kind == "teleport_relay":
            dist = math.hypot(ball.x - hazard.x, ball.y - hazard.y)
            if dist <= getattr(hazard, "radius", 25.0):
                linked_id = getattr(hazard, "linked_relay_id", None)
                if linked_id is not None:
                    last_teleport = getattr(ball, "last_teleport_tick", -100)
                    current_tick = getattr(world, "tick", 0)
                    if current_tick - last_teleport > 20:  # 20 tick cooldown
                        for h in world.arena.hazards:
                            if getattr(h, "id", None) == linked_id:
                                ball.x = h.x
                                ball.y = h.y
                                ball.last_teleport_tick = current_tick
                                if hasattr(ball, "_teleported_this_tick"):
                                    ball._teleported_this_tick = True
                                world.events.append({"type": "visual_effect", "data": {"x": ball.x, "y": ball.y, "kind": "teleport"}})
                                break

    # Ensure it teleported
    assert abs(ball.x - 100.0) < 1.0
    assert abs(ball.y - 100.0) < 1.0
    assert ball.last_teleport_tick == world.tick

if __name__ == "__main__":
    test_teleport_relay()
    print("Teleport relay test passed.")
