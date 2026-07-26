from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
    def is_point_inside(self, x, y):
        return True

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.entities = balls
        self.arena = MockArena()
        self.events = []

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = team
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.is_decoy = False
        self.inventory = ["position_swap"]
        self.ball_type = "mock"

def test_position_swap_low_hp():
    ball1 = MockBall(1, 10, 10, "team1")
    ball1.hp = 20.0 # 20%

    ball2 = MockBall(2, 100, 100, "team2")
    ball2.hp = 100.0

    ball3 = MockBall(3, 50, 50, "team2") # Closer enemy
    ball3.hp = 100.0

    world = MockWorld([ball1, ball2, ball3])
    action = Action(ball1, world)

    # Try to execute idle strategy, when low HP it should trigger swap
    action.execute("idle", 0.1)

    # ball1 should be at ball3's original position, and ball1's inventory should be empty
    assert abs(ball1.x - 50) < 5
    assert abs(ball1.y - 50) < 5
    assert len(ball1.inventory) == 0
