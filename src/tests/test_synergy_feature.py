import unittest
from unittest.mock import MagicMock
from src.ai.action import Action
import math

class TestCosmeticSynergy(unittest.TestCase):
    def test_cosmetic_synergy(self):
        # Create a mock world and balls
        class MockBall:
            def __init__(self, id, team, cosmetic, x, y, hp, max_hp, base_speed, base_damage):
                self.id = id
                self.team = team
                self.ball_type = team
                self.cosmetic = cosmetic
                self.x = x
                self.y = y
                self.hp = hp
                self.max_hp = max_hp
                self.base_speed = base_speed
                self.base_damage = base_damage
                self.alive = True
                self.speed = base_speed
                self.damage = base_damage

        b1 = MockBall(1, "ninja", "sunglasses", 0, 0, 50, 100, 2.0, 10.0)
        b2 = MockBall(2, "ninja", "sunglasses", 10, 0, 100, 100, 2.0, 10.0) # Same team, same cosmetic
        b3 = MockBall(3, "ninja", "sunglasses", 20, 0, 100, 100, 2.0, 10.0) # Same team, same cosmetic
        b4 = MockBall(4, "ninja", "hat", 30, 0, 100, 100, 2.0, 10.0) # Same team, different cosmetic
        b5 = MockBall(5, "knight", "sunglasses", 40, 0, 100, 100, 2.0, 10.0) # Different team, same cosmetic

        class MockWorld: pass
        world = MockWorld()
        world.balls = [b1, b2, b3, b4, b5]

        action = Action(b1, world)

        # Call apply friendly aura
        action._apply_friendly_aura(0.016)

        # Verify cosmetic synergies applied
        # b2 and b3 have same cosmetic and are friendly. matching_cosmetics = 2
        # speed should be base_speed * (1 + 0.05 * 2) = 2.0 * 1.1 = 2.2

        # day_multiplier is 1.0 because world.arena is not mocked in this minimal test to pass hasattr

        self.assertAlmostEqual(b1.speed, 2.2, places=4)
        self.assertAlmostEqual(b1.damage, 13.2, places=4)
        self.assertAlmostEqual(b1.hp, 50.016, places=4)

if __name__ == '__main__':
    unittest.main()
