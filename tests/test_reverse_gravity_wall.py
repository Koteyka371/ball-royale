from ai.action import Action
from ai.action import Action

class MockBall:
    def __init__(self, x=0, y=0, team=1):
        self.id = 1
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.speed = 10
        self.base_speed = 10
        self.stamina = 100
        self.ball_type = "brawler"
        self.radius = 20
        self._base_speed_set = True
        self.vx = 0
        self.vy = 0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = None
        self.game_mode = None
        self.boosters = []
        self.events = []

    def get_nearby_entities(self, entity, radius):
        return {
            "enemies": [b for b in self.balls if b != entity and getattr(b, "team", -1) != getattr(entity, "team", -1)],
            "allies": [b for b in self.balls if b != entity and getattr(b, "team", -1) == getattr(entity, "team", -1)],
            "boosters": self.boosters
        }


def test_reverse_gravity_booster_wall():
    ball = MockBall(x=500.0, y=500.0, team=1)
    ball.id = 1
    ball.reverse_gravity_booster_timer = 5.0

    enemy1 = MockBall(x=550.0, y=550.0, team=2) # close enough to ball
    enemy1.id = 2

    enemy2 = MockBall(x=800.0, y=500.0, team=2) # far from ball
    enemy2.id = 3

    ally = MockBall(x=10.0, y=10.0, team=1) # close ally
    ally.id = 4

    world = MockWorld()
    world.balls = [ball, enemy1, enemy2, ally]
    world.arena = type('MockArena', (), {'hazards': [], 'width': 1000, 'height': 1000})()
    world.game_mode = None

    action = Action(ball, world)
    action.execute("none", 1.0)

    # Assertions
    assert enemy1.x > 550.0 or enemy1.x < 550.0 or enemy1.y > 550.0 or enemy1.y < 550.0, "Enemy1 should have moved"
    assert enemy2.x == 800.0 and enemy2.y == 500.0, "Enemy2 should not have moved"
    assert ally.x == 10.0 and ally.y == 10.0, "Ally should not have moved"
