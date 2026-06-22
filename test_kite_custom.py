import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, speed=10, radius=10, attack_range=150.0):
        self.current_action = None
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.attack_range = attack_range
        self.perception_radius = 1000
        self.skill_timer = 0.0
        self.attack_timer = 0.0
        self.ball_type = "sniper"
        self.alive = True

    def use_skill(self):
        pass

class MockEnemy:
    def __init__(self, x=10, y=0, radius=10, ball_type="enemy_ball", alive=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.ball_type = ball_type
        self.alive = alive

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.enemies = []
        self.allies = []
        self.damage_dealt = False

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": self.enemies,
            "allies": self.allies,
            "boosters": [],
            "traps": []
        }

    def _deal_damage(self, attacker, target):
        self.damage_dealt = True

def test_kite_move_away():
    ball = MockBall(x=500, y=500, speed=10, attack_range=150.0)
    world = MockWorld()
    world.enemies = [MockEnemy(x=550, y=500)] # distance 50
    action_layer = Action(ball, world)
    action_layer.execute("kite", 0.1)

    assert ball.x < 500 # moved away from 550

def test_kite_move_closer():
    ball = MockBall(x=500, y=500, speed=10, attack_range=150.0)
    world = MockWorld()
    world.enemies = [MockEnemy(x=700, y=500)] # distance 200 > 150
    action_layer = Action(ball, world)
    action_layer.execute("kite", 0.1)

    assert ball.x > 500 # moved closer to 700

def test_kite_hold_position():
    ball = MockBall(x=500, y=500, speed=10, attack_range=150.0)
    world = MockWorld()
    world.enemies = [MockEnemy(x=630, y=500)] # distance 130 (between 120 and 150)
    action_layer = Action(ball, world)

    orig_x, orig_y = ball.x, ball.y
    action_layer.execute("kite", 0.1)

    assert math.isclose(ball.x, orig_x, rel_tol=1e-5)
    assert world.damage_dealt == True

if __name__ == '__main__':
    test_kite_move_away()
    test_kite_move_closer()
    test_kite_hold_position()
    print("Tests passed.")
