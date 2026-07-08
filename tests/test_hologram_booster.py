import unittest
import math
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.next_id = 50000
        self.events = []
        self.dead_balls = []

    def get_nearby_entities(self, entity, radius):
        return {"allies": [], "enemies": [], "hazards": [], "boosters": []}

    def _deal_damage(self, attacker, target, damage=None):
        dmg = damage if damage is not None else getattr(attacker, 'damage', 10.0)
        if hasattr(target, 'take_damage'):
            target.take_damage(dmg)
        else:
            target.hp -= dmg
            if target.hp <= 0:
                target.alive = False

class MockBall:
    def __init__(self, id, ball_type):
        self.id = id
        self.ball_type = ball_type
        self.team = ball_type
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.speed = 5.0
        self.base_speed = 5.0
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.alive = True
        self.inventory = []
        self.strategy = "none"

class MockBooster:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 15.0

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, radius):
        return x, y, False

class TestHologramBooster(unittest.TestCase):
    def setUp(self):
        self.world = MockWorld()
        self.world.arena = MockArena()
        self.ball = MockBall(1, "test_ball")
        self.world.balls.append(self.ball)
        self.action = Action(self.ball, self.world)
        self.booster = MockBooster("hologram_booster", 10.0, 0.0)
        self.world.boosters.append(self.booster)
        self.world.get_nearby_entities = lambda e, r: {"boosters": [self.booster], "enemies": [], "allies": [], "hazards": []}
        self.action._get_perception_radius = lambda: 1000.0

    def test_hologram_booster_collection(self):
        initial_balls_count = len(self.world.balls)

        # Set distance very close so it collects it immediately
        self.ball.x = 10.0
        self.ball.y = 0.0

        # Collect booster strategy
        self.action.execute("collect booster", 1.0)

        # 3 Holograms should have been spawned
        self.assertEqual(len(self.world.balls), initial_balls_count + 3)
        self.assertNotIn(self.booster, self.world.boosters)

        holograms = [b for b in self.world.balls if getattr(b, "is_hologram", False)]
        self.assertEqual(len(holograms), 3)

        for holo in holograms:
            self.assertEqual(holo.hp, 1.0)
            self.assertEqual(holo.max_hp, 1.0)
            self.assertTrue(holo.is_hologram)
            self.assertGreater(holo.hologram_timer, 0.0)

            speed = math.hypot(holo.vx, holo.vy)
            self.assertTrue(math.isclose(speed, self.ball.speed * 1.5, rel_tol=1e-1))

    def test_hologram_takes_damage(self):
        self.ball.x = 10.0
        self.ball.y = 0.0
        self.action.execute("collect booster", 1.0)
        holograms = [b for b in self.world.balls if getattr(b, "is_hologram", False)]
        holo = holograms[0]

        attacker = MockBall(2, "attacker")
        attacker.damage = 10.0

        self.action._attempt_damage(attacker, holo)

        self.assertFalse(holo.alive)
        self.assertEqual(holo.hp, 0.0)

if __name__ == '__main__':
    unittest.main()
