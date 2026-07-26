import unittest
from ai.action import Action

class MockBall:
    def __init__(self, x, y, alive=True, team="team_A"):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.alive = alive
        self.is_decoy = False
        self.inventory = []
        self.ball_type = team
        self.team = team
        self.id = id(self)

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500
        self.weather = "clear"
        self.is_eclipse = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball and b.alive]

class TestPositionSwapRandom(unittest.TestCase):
    def test_position_swap_prioritizes_nearest_enemy(self):
        world = MockWorld()
        ball1 = MockBall(0, 0, team="team_A")
        ball1.inventory.append("position_swap")

        # Ally, shouldn't be swapped with if there are enemies
        ball2 = MockBall(10, 10, team="team_A")

        # Enemies
        ball3 = MockBall(100, 100, team="team_B") # Distance 141
        ball4 = MockBall(200, 200, team="team_C") # Distance 282

        world.balls = [ball1, ball2, ball3, ball4]

        action = Action(ball1, world)
        action.execute("flee", 0.0) # Delta 0 so it doesn't move further

        # Should never swap with an ally when enemies are present
        self.assertFalse(ball2.x == 0 and ball2.y == 0)

        # Should swap with the nearest enemy (ball3)
        self.assertTrue(ball3.x == 0 and ball3.y == 0)
        self.assertFalse(ball4.x == 0 and ball4.y == 0)

if __name__ == '__main__':
    unittest.main()
