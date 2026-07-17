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
    def test_position_swap_is_random_and_prioritizes_enemies(self):
        swapped_with_2 = False
        swapped_with_3 = False
        swapped_with_4 = False

        for _ in range(30):
            world = MockWorld()
            ball1 = MockBall(0, 0, team="team_A")
            ball1.inventory.append("position_swap")

            # Ally, shouldn't be swapped with if there are enemies
            ball2 = MockBall(10, 10, team="team_A")

            # Enemies
            ball3 = MockBall(100, 100, team="team_B")
            ball4 = MockBall(200, 200, team="team_C")

            world.balls = [ball1, ball2, ball3, ball4]

            action = Action(ball1, world)
            action.execute("flee", 0.0) # Delta 0 so it doesn't move further

            # The swap sets ball1 coordinates, but then action logic might slightly adjust it.
            # We can just check if ball3 or ball4 got moved to (0,0) which was ball1's original pos!
            if ball2.x == 0 and ball2.y == 0:
                swapped_with_2 = True
            elif ball3.x == 0 and ball3.y == 0:
                swapped_with_3 = True
            elif ball4.x == 0 and ball4.y == 0:
                swapped_with_4 = True

        # Should never swap with an ally when enemies are present
        self.assertFalse(swapped_with_2)

        # Should swap with both enemies randomly over 30 runs
        self.assertTrue(swapped_with_3)
        self.assertTrue(swapped_with_4)

if __name__ == '__main__':
    unittest.main()
