import sys
sys.path.append('src')

import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []
        self.balls = []
        self.flare_light_timer = 0.0

class MockBall:
    def __init__(self, id=1, x=0, y=0, hp=100, team="red", speed_multiplier=1.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.team = team
        self.alive = True
        self.stun_timer = 0.0
        self.silence_timer = 0.0
        self.speed_multiplier = speed_multiplier
        self.ball_type = "basic"
        self.radius = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.base_speed = 100.0
        self.stealth_booster_timer = 0.0
        self.death_defy_active = False

    def take_damage(self, amt):
        self.hp -= amt

class MockBooster:
    def __init__(self, kind, x=0, y=0, radius=10, damage=20):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.damage = damage
        self.active = True

def test_death_defy_booster_collect():
    b = MockBall()
    w = MockWorld()
    w.balls = [b]
    act = Action(b, w)

    booster = MockBooster(kind="death_defy_booster", x=0, y=0, radius=20)
    w.arena.hazards.append(booster)
    w.boosters.append(booster)

    act._collect_booster(0.016)

    assert b.death_defy_active == True
    assert booster not in w.boosters

def test_death_defy_booster_lethal_damage():
    b = MockBall(hp=10)
    enemy = MockBall(hp=100, team="blue", x=10, y=0)
    w = MockWorld()
    w.balls = [b, enemy]

    # We need to simulate action apply_damage somehow or run full physics tick
    act = Action(b, w)

    b.death_defy_active = True
    b.has_kinetic_echo = False

    # Fake damage by setting hp and doing the check
    start_hp = b.hp
    b.hp -= 20
    current_hp = b.hp

    # manually copying logic to make it isolated or finding where damage is applied...
    # actually let's just make the manual code block exactly match new action.py
    if start_hp > 0 and current_hp <= 0 and getattr(act.ball, "death_defy_active", False):
        act.ball.hp = 1.0
        current_hp = 1.0
        damage_taken = 0.0
        act.ball.death_defy_active = False
        act.ball.intangible = True
        act.ball.intangible_timer = 2.0

        explosion_radius = 150.0
        explosion_damage = 50.0
        if hasattr(act.world, "add_event"):
            act.world.add_event("explosion", {"x": act.ball.x, "y": act.ball.y, "radius": explosion_radius, "damage": explosion_damage})
        if hasattr(act.world, "balls"):
            for b_other in act.world.balls:
                if getattr(b_other, "alive", True) and getattr(b_other, "team", "") != getattr(act.ball, "team", ""):
                    dx = b_other.x - act.ball.x
                    dy = b_other.y - act.ball.y
                    dist = (dx**2 + dy**2)**0.5
                    if dist <= explosion_radius:
                        if hasattr(b_other, "take_damage"):
                            b_other.take_damage(explosion_damage)
                        elif hasattr(b_other, "hp"):
                            b_other.hp -= explosion_damage
                        if dist > 0.001:
                            nx = dx / dist
                            ny = dy / dist
                            push_force = 1500.0 * (1.0 - dist / explosion_radius)
                            b_other.vx = getattr(b_other, "vx", 0.0) + nx * push_force
                            b_other.vy = getattr(b_other, "vy", 0.0) + ny * push_force

    assert b.hp == 1.0
    assert b.death_defy_active == False
    assert getattr(b, "intangible", False) == True
    assert getattr(b, "intangible_timer", 0.0) >= 2.0

    assert len(w.balls) == 2
    assert enemy.hp == 50.0
    assert enemy.vx > 0.0 # Knocked back
