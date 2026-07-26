import unittest
from ai.action import Action
import random

class DummyArena:
    def __init__(self):
        self.hazards = []
        self.friction = 0.5
        self.bounds = (100, 100)
        self.width = 100
        self.height = 100
        self.is_snowing = False
        self.is_heatwave = False
        self.is_windy = False
        self.storm_intensity = 0.0

class DummyBall:
    def __init__(self, x, y, team, id):
        self.x = x
        self.y = y
        self.team = team
        self.id = id
        self.hp = 50.0
        self.max_hp = 100.0
        self.stamina = 50.0
        self.max_stamina = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.speed_multiplier = 1.0
        self.vx = 0.0
        self.vy = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.is_intangible = False
        self.bounces_left = 0
        self.stun_timer = 0.0
        self.rooted_timer = 0.0
        self.alive = True
        self.shadow_booster_timer = 15.0
        self.shadow_speed_applied = False
        self.ball_type = "default"
        self.radius = 10.0
        self.invulnerable_timer = 0.0
        self.charge_level = 0.0
        self.defense_multiplier = 1.0

class DummyWorld:
    def __init__(self, balls):
        self.balls = balls
        self.arena = DummyArena()
        self.events = []
        self.boosters = []
        self.time = 0.0
        self.game_mode = "default"

class TestShadowBooster(unittest.TestCase):
    def test_shadow_booster_mechanics(self):
        ball = DummyBall(0, 0, "A", 1)
        enemy = DummyBall(10, 0, "B", 2)
        enemy.hp = 100.0

        world = DummyWorld([ball, enemy])
        action = Action(ball, world)
        action.random = random

        try:
            action.execute("idle", 1.0)
        except Exception:
            pass

        self.assertEqual(ball.shadow_booster_timer, 14.0)
        self.assertEqual(ball.speed_multiplier, 1.5)
        self.assertEqual(ball.shadow_speed_applied, True)
        self.assertEqual(ball.max_stamina, 95.0)
        self.assertEqual(ball.hp, 60.0)
        self.assertEqual(enemy.hp, 90.0)

        # Now fast forward to expiration
        try:
            action.execute("idle", 15.0)
        except Exception:
            pass

        self.assertEqual(ball.shadow_booster_timer, 0.0)
        self.assertEqual(ball.speed_multiplier, 1.0)
        self.assertEqual(ball.shadow_speed_applied, False)
        self.assertEqual(ball.max_stamina, 20.0)

if __name__ == '__main__':
    unittest.main()
