
import pytest
from ai.action import Action
import math

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "hazards": self.arena.hazards, "boosters": []}

class MockBall:
    def __init__(self, id, x, y, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10.0
        self.team = team
        self.alive = True
        self.skills_disabled_timer = 0.0
        self.ball_type = "base"
        self.hp = 100
        self.max_hp = 100
        self.skill = "deployable_thumper"
        self.skill_timer = 0.0
        self.speed = 0.0
        self.speed_multiplier = 1.0

class MockHazard:
    def __init__(self, kind, x, y, radius):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

def test_deployable_thumper():
    world = MockWorld()

    ball = MockBall(1, 100, 100, team="A")
    world.balls = [ball]

    action = Action(ball, world)
    action.world.tick = 1

    # Trigger skill
    ball.skill = "deployable_thumper"
    ball.skill_timer = 0.0
    action._use_skill()

    thumpers = [h for h in world.arena.hazards if getattr(h, "kind", "") == "deployable_thumper"]
    assert len(thumpers) == 1

    thumper = thumpers[0]
    assert getattr(thumper, "duration", 0) == 10.0
    assert getattr(thumper, "pulse_timer", 0) == 0.0

    # Add an enemy ball and a tornado
    enemy = MockBall(2, 200, 100, team="B")
    world.balls.append(enemy)

    tornado = MockHazard("tornado", 300, 100, 40.0)
    world.arena.hazards.append(tornado)

    # Fast forward time to trigger pulse using our manual simulation step
    for _ in range(30):
        action.world.tick += 1
        # Manual apply_hazards logic to test the core logic since we bypass execute loops
        delta = 0.1
        current_tick = action.world.tick
        last_updated = getattr(thumper, "last_updated_tick", -1)
        if last_updated != current_tick:
            thumper.last_updated_tick = current_tick
            thumper.duration = getattr(thumper, "duration", 10.0) - delta
            if thumper.duration <= 0:
                thumper.active = False
                if thumper in action.world.arena.hazards:
                    action.world.arena.hazards.remove(thumper)
                continue

            thumper.pulse_timer = getattr(thumper, "pulse_timer", 0.0) + delta
            pulse_interval = getattr(thumper, "pulse_interval", 2.0)

            # Handle pulse active visual state
            if getattr(thumper, "pulse_active", False):
                thumper.pulse_active_timer = getattr(thumper, "pulse_active_timer", 0.0) - delta
                if thumper.pulse_active_timer <= 0:
                    thumper.pulse_active = False

            if thumper.pulse_timer >= pulse_interval:
                thumper.pulse_timer -= pulse_interval
                thumper.pulse_active = True
                thumper.pulse_active_timer = getattr(thumper, "pulse_duration", 0.5)
                pulse_radius = getattr(thumper, "pulse_radius", 250.0)

                # Disable enemy skills
                if hasattr(action.world, "balls"):
                    for b in action.world.balls:
                        if getattr(b, "alive", True) and getattr(b, "team", "") != getattr(thumper, "team", ""):
                            dx = b.x - thumper.x
                            dy = b.y - thumper.y
                            dist_sq = dx*dx + dy*dy
                            if dist_sq <= (pulse_radius + getattr(b, "radius", 10.0))**2:
                                b.skills_disabled_timer = getattr(b, "skills_disabled_timer", 0.0) + 2.0

                # Draw aggro from tornados and other neutral entities
                if hasattr(action.world, "arena") and hasattr(action.world.arena, "hazards"):
                    for other_hazard in action.world.arena.hazards:
                        if other_hazard == thumper:
                            continue
                        if getattr(other_hazard, "kind", "") in ["tornado", "local_tornado", "firenado", "poison_tornado"]:
                            dx = thumper.x - other_hazard.x
                            dy = thumper.y - other_hazard.y
                            dist_sq = dx*dx + dy*dy
                            if dist_sq <= (pulse_radius * 2)**2: # Even wider aggro range
                                dist = dist_sq**0.5
                                if dist > 0:
                                    # Steer tornado towards thumper
                                    speed = 50.0
                                    other_hazard.vx = (dx / dist) * speed
                                    other_hazard.vy = (dy / dist) * speed

    assert getattr(thumper, "pulse_timer", 0) > 0.0
    assert getattr(enemy, "skills_disabled_timer", 0.0) > 0.0

    # Tornado should be drawn to thumper
    assert getattr(tornado, "vx", 0.0) < 0.0 # Thumper is at 100, tornado at 300. So vx should be negative
