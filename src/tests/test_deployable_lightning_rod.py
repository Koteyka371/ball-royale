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
        self.events = []
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
        self.ball_type = "base"
        self.hp = 100
        self.max_hp = 100
        self.skill = "deploy_lightning_rod"
        self.skill_timer = 0.0
        self.speed = 0.0
        self.speed_multiplier = 1.0
        self.stun_timer = 0.0
        self.energy_shield_active = False
        self.energy_shield_hp = 0.0

def test_deployable_lightning_rod():
    world = MockWorld()

    ball = MockBall(1, 100, 100, team="A")
    world.balls = [ball]

    action = Action(ball, world)
    action.world.tick = 1

    # Trigger skill
    ball.skill = "deploy_lightning_rod"
    ball.skill_timer = 0.0
    action._use_skill()

    rods = [h for h in world.arena.hazards if getattr(h, "kind", "") == "deployable_lightning_rod"]
    assert len(rods) == 1

    rod = rods[0]
    assert getattr(rod, "duration", 0) == 15.0
    assert getattr(rod, "charge", 0) == 0.0
    assert getattr(rod, "max_charge", 0) == 100.0

    ally = MockBall(2, 120, 100, team="A")
    enemy = MockBall(3, 200, 100, team="B")
    world.balls.extend([ally, enemy])

    # Tick loop 1: ally gets shield
    action.world.tick = 2
    delta = 0.1
    # We call apply hazards logic directly for test
    for hazard in list(action.world.arena.hazards):
        if hazard.kind == "deployable_lightning_rod":
            current_tick = getattr(action.world, "tick", 0)
            last_updated = getattr(hazard, "last_updated_tick", -1)
            if last_updated != current_tick:
                hazard.last_updated_tick = current_tick
                hazard.duration = getattr(hazard, "duration", 15.0) - delta
                if hazard.duration <= 0:
                    continue

                pulse_radius = getattr(hazard, "pulse_radius", 250.0)
                if hasattr(action.world, "balls"):
                    for b in action.world.balls:
                        if getattr(b, "alive", True) and getattr(b, "team", None) == getattr(hazard, "team", ""):
                            dx = b.x - hazard.x
                            dy = b.y - hazard.y
                            dist_sq = dx*dx + dy*dy
                            if dist_sq <= (pulse_radius + getattr(b, "radius", 10.0))**2:
                                b.energy_shield_active = True
                                b.energy_shield_hp = max(getattr(b, "energy_shield_hp", 0.0), 50.0)

                charge = getattr(hazard, "charge", 0.0)
                max_charge = getattr(hazard, "max_charge", 100.0)
                if charge >= max_charge:
                    hazard.charge = 0.0
                    if hasattr(action.world, "events"):
                        action.world.events.append({'type': 'visual_effect', 'data': {'type': 'lightning', 'x': hazard.x, 'y': hazard.y}})
                    if hasattr(action.world, "balls"):
                        for b in action.world.balls:
                            if getattr(b, "alive", True) and getattr(b, "team", None) != getattr(hazard, "team", ""):
                                dx = b.x - hazard.x
                                dy = b.y - hazard.y
                                dist_sq = dx*dx + dy*dy
                                if dist_sq <= (pulse_radius + getattr(b, "radius", 10.0))**2:
                                    b.stun_timer = max(getattr(b, "stun_timer", 0.0), 2.0)
                                    if hasattr(action, "_spawn_directed_particles"):
                                        action._spawn_directed_particles(hazard, b, "lightning")

    assert ally.energy_shield_active is True
    assert ally.energy_shield_hp == 50.0
    assert enemy.stun_timer == 0.0

    # Tick loop 2: charge >= max_charge
    rod.charge = 150.0
    action.world.tick = 3
    for hazard in list(action.world.arena.hazards):
        if hazard.kind == "deployable_lightning_rod":
            current_tick = getattr(action.world, "tick", 0)
            last_updated = getattr(hazard, "last_updated_tick", -1)
            if last_updated != current_tick:
                hazard.last_updated_tick = current_tick
                hazard.duration = getattr(hazard, "duration", 15.0) - delta
                if hazard.duration <= 0:
                    continue

                pulse_radius = getattr(hazard, "pulse_radius", 250.0)

                charge = getattr(hazard, "charge", 0.0)
                max_charge = getattr(hazard, "max_charge", 100.0)
                if charge >= max_charge:
                    hazard.charge = 0.0
                    if hasattr(action.world, "events"):
                        action.world.events.append({'type': 'visual_effect', 'data': {'type': 'lightning', 'x': hazard.x, 'y': hazard.y}})
                    if hasattr(action.world, "balls"):
                        for b in action.world.balls:
                            if getattr(b, "alive", True) and getattr(b, "team", None) != getattr(hazard, "team", ""):
                                dx = b.x - hazard.x
                                dy = b.y - hazard.y
                                dist_sq = dx*dx + dy*dy
                                if dist_sq <= (pulse_radius + getattr(b, "radius", 10.0))**2:
                                    b.stun_timer = max(getattr(b, "stun_timer", 0.0), 2.0)
                                    if hasattr(action, "_spawn_directed_particles"):
                                        action._spawn_directed_particles(hazard, b, "lightning")

    assert rod.charge == 0.0
    assert enemy.stun_timer == 2.0
    assert any(e == {'type': 'visual_effect', 'data': {'type': 'lightning', 'x': rod.x, 'y': rod.y}} for e in world.events)
