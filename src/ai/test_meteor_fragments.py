import unittest
from ai.game_modes import GlowingMeteorFragmentsMode
from ai.action import Action
import math

class MockBall:
    def __init__(self, id=1, x=100.0, y=100.0, hp=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = True
        self.radius = 10.0
        self.damage_booster_timer = 0.0
        self.team = "team1"
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 100.0
        self.intangible = False
        self.intangible_timer = 0.0
        self.is_ghost = False

    def take_damage(self, amount):
        self.hp -= amount

    def get(self, prop, default=None):
        return getattr(self, prop, default)

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []
        self.items = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []
        self.balls = []

    def _collect_booster(self, ball, b):
        pass

class TestMeteorFragments(unittest.TestCase):
    def test_meteor_fragments_mode(self):
        mode = GlowingMeteorFragmentsMode()
        world = MockWorld()
        balls = [MockBall()]
        world.balls = balls

        mode.setup(world, balls)

        # Advance time to trigger meteor spawn
        mode.tick(world, balls, 3.1)

        # Check meteor was spawned
        self.assertGreaterEqual(len(mode.active_meteors), 1)
        meteor = mode.active_meteors[0]

        # Move ball directly to the meteor impact point
        balls[0].x = meteor["x"]
        balls[0].y = meteor["y"]

        # Advance time to trigger meteor impact
        mode.tick(world, balls, 5.1)

        # Check meteor impact damage
        self.assertLess(balls[0].hp, 100.0)

        # Check fragment was spawned
        self.assertGreaterEqual(len(world.boosters), 1)

        # Find the specific fragment that dropped from the first meteor
        fragment = next((b for b in world.boosters if b.x == meteor["x"] and b.y == meteor["y"]), None)
        self.assertIsNotNone(fragment)
        self.assertEqual(fragment.kind, "meteor_fragment")

        # Check fragment collection
        action = Action(balls[0], world)
        # Action is instantiated with (ball, world) incorrectly? Let's check init signature
        # In this project action is often `Action(world, self.ball)` inside other functions but standard is Action(ball, world) or Action(world) where world is self
        # Actually it's Action(ball, world) in many tests but let's do action._collect_booster

        # Set Action instance manually to avoid init errors
        action.world = world
        action.ball = balls[0]
        action._collect_booster(0.016)

        # Booster should be collected
        self.assertNotIn(fragment, world.boosters)
        # Damage booster timer should be updated
        self.assertGreater(balls[0].damage_booster_timer, 0.0)

if __name__ == '__main__':
    unittest.main()
