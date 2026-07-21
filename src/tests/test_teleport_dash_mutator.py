import unittest
import math
from ai.game_modes import TeleportDashMutatorMode
from ai.action import Action

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return [max(0, min(1000, x)), max(0, min(1000, y))]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.game_mode = TeleportDashMutatorMode()
        self.balls = []
        self.width = 1000
        self.height = 1000

class MockBall:
    def __init__(self, id, x=500, y=500, team=1):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 10
        self.team = team
        self.hp = 100
        self.alive = True
        self.dash_range_mult = 1.0
        self.SKILL_COOLDOWN = 5.0
        self.skill_timer = 0.0
        self.skill = "dash"
        self.active_skill = "dash"
        self.mutators = ["teleport_dash"]
        self.intangible = False
        self.invulnerable = False
        self.is_dashing = False
        self.silence_timer = 0.0
        self.alliance = str(team)

class TestTeleportDashMutator(unittest.TestCase):
    def test_teleport_dash_action(self):
        world = MockWorld()
        ball = MockBall(1, 500, 500, "1")
        enemy = MockBall(2, 800, 800, "2")
        world.balls = [ball, enemy]

        action = Action(ball, world)

        def fake_get_enemies():
            return [enemy]
        action._get_enemies = fake_get_enemies

        action._use_skill()

        # Original dash has range 100 * mult, teleport dash has 200 * mult.
        # Should teleport towards the enemy
        dx = 800 - 500
        dy = 800 - 500
        dist = math.sqrt(dx*dx + dy*dy)
        dir_x = dx / dist
        dir_y = dy / dist

        expected_x = 500 + dir_x * 200.0
        expected_y = 500 + dir_y * 200.0

        self.assertAlmostEqual(ball.x, expected_x, places=1)
        self.assertAlmostEqual(ball.y, expected_y, places=1)

        # Cooldown should be 5.0 * 1.5 = 7.5
        self.assertAlmostEqual(ball.skill_timer, 7.5, places=1)

if __name__ == '__main__':
    unittest.main()
