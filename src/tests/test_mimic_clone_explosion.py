import pytest
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, id=1, team="red", ball_type="fighter", hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.hp = hp
        self.alive = alive
        self.is_mimic_clone = False
        self.is_mimic_charging = False
        self.mimic_timer = 10.0
        self.mimic_charge_timer = 3.0
        self.vx = 0.0
        self.vy = 0.0
        self.max_hp = hp
        self.illusion_timer = 10.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = type('MockArena', (), {'hazards': []})()

def test_mimic_clone_explosion_event():
    world = MockWorld()
    clone = MockBall(0, 0, id=1, team="red")
    clone.is_mimic_charging = True
    clone.mimic_charge_timer = 0.1 # Will detonate on next tick
    world.balls.append(clone)

    enemy = MockBall(50, 0, id=2, team="blue")
    world.balls.append(enemy)

    action = Action(clone, world)
    action.execute("idle", 0.2)

    # Check that the explosion event was added
    assert len(world.events) > 0
    explosion_event = world.events[-1]

    # Python code was modified to use 'visual_effect', 'data': {'type': 'mimic_clone_explosion'}
    if 'type' in explosion_event and explosion_event['type'] == 'visual_effect':
        assert explosion_event['data']['type'] == 'mimic_clone_explosion'
        assert explosion_event['data']['radius'] == 60.0
    else:
        assert False, f"Expected visual_effect mimic_clone_explosion event, got: {explosion_event}"
