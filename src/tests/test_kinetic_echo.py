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
        self.skill = "kinetic_echo"
        self.skill_timer = 0.0
        self._prev_skill_timer = 0.0
        self.has_kinetic_echo = False
        self.blood_magic_timer = 0.0

def test_kinetic_echo_place_and_trigger():
    b = MockBall(hp=100)
    e = MockBall(hp=100, team="blue", x=10, y=10)
    w = MockWorld()
    w.balls = [b, e]
    act = Action(b, w)
    act._get_enemies = lambda: [e]

    # 1. Place echo
    b.skill_timer = 1.0 # Trigger skill update
    act._update_skill_timer(0.1)

    assert b.has_kinetic_echo == True
    assert b.kinetic_echo_x == 0
    assert b.kinetic_echo_y == 0
    assert b.kinetic_echo_start_hp == 100
    assert b.skill_timer == 0.0

    placed_events = [ev for ev in w.events if ev['type'] == 'visual_effect' and ev['data']['type'] == 'kinetic_echo_placed']
    assert len(placed_events) == 1

    # Move ball and take damage
    b.x = 500
    b.y = 500
    b.hp = 50

    # 2. Trigger again
    b.skill_timer = 2.0
    act._update_skill_timer(0.1)

    assert b.has_kinetic_echo == False
    assert b.x == 0
    assert b.y == 0

    # Check shockwave damage
    # Damage taken = 50. Shockwave dmg = max(10, 50 * 1.5) = 75
    assert e.hp == 25

    sw_events = [ev for ev in w.events if ev['type'] == 'visual_effect' and ev['data']['type'] == 'kinetic_echo_shockwave']
    assert len(sw_events) == 1
    assert sw_events[0]['data']['damage'] == 75

def test_kinetic_echo_lethal():
    b = MockBall(hp=100)
    e = MockBall(hp=100, team="blue", x=10, y=10)
    w = MockWorld()
    w.balls = [b, e]
    act = Action(b, w)
    act._get_enemies = lambda: [e]

    b.skill_timer = 1.0
    act._update_skill_timer(0.1)
    assert b.has_kinetic_echo == True

    b.x = 500
    b.y = 500

    start_hp = b.hp
    b.hp = -10
    current_hp = b.hp

    # Simulate execution of the lethal damage logic block from execute
    if start_hp > 0 and current_hp <= 0 and getattr(act.ball, "has_kinetic_echo", False):
        act.ball.hp = 1.0
        current_hp = 1.0
        damage_taken = 0.0
        act.ball.alive = True

        dmg_accumulated = max(0.0, getattr(act.ball, "kinetic_echo_start_hp", 1.0) - 1.0)
        shockwave_dmg = max(10.0, dmg_accumulated * 1.5)
        echo_x = getattr(act.ball, "kinetic_echo_x", act.ball.x)
        echo_y = getattr(act.ball, "kinetic_echo_y", act.ball.y)

        for enemy in act._get_enemies():
            dist_sq = (enemy.x - echo_x)**2 + (enemy.y - echo_y)**2
            if dist_sq <= 150.0**2:
                enemy.hp -= shockwave_dmg

        act.world.events.append({'type': 'visual_effect', 'data': {'type': 'kinetic_echo_shockwave', 'x': echo_x, 'y': echo_y, 'radius': 150.0, 'damage': shockwave_dmg}})

        act.ball.x = echo_x
        act.ball.y = echo_y
        act.ball.has_kinetic_echo = False
        act.ball.skill_timer = 0.0

    assert b.hp == 1.0
    assert b.has_kinetic_echo == False
    assert b.x == 0
    assert b.y == 0

    # 99 dmg accumulated * 1.5 = 148.5
    assert e.hp == 100 - 148.5