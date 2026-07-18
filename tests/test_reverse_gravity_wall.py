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
            "boosters": [b for b in self.boosters if (b.x - entity.x)**2 + (b.y - entity.y)**2 <= radius**2]
        }


def test_reverse_gravity_booster():
    ball = MockBall(x=500.0, y=500.0, team=1)
    ball.id = 1

    enemy1 = MockBall(x=-550.0, y=-550.0, team=2) # Place far enough away so collection happens! If enemy is < 30 dist, ball flees instead
    enemy1.id = 2

    enemy2 = MockBall(x=800.0, y=500.0, team=2)
    enemy2.id = 3

    ally = MockBall(x=10.0, y=10.0, team=1)
    ally.id = 4

    world = MockWorld()
    world.balls = [ball, enemy1, enemy2, ally]
    world.arena = type('MockArena', (), {'hazards': [], 'width': 1000, 'height': 1000, 'safe_zone_center': (500, 500), 'safe_zone_radius': 500})()
    world.game_mode = None

    booster = type('MockBooster', (), {'x': 500.0, 'y': 500.0, 'kind': 'reverse_gravity_booster', 'radius': 10})()
    world.boosters.append(booster)

    # We explicitly call the _collect_booster method like in action.py logic
    action = Action(ball, world)
    # the Action class logic first calls _collect_boosters in its execute function
    action._collect_booster(1.0)

    # Assertions
    assert getattr(enemy1, "invert_timer", 0.0) == 3.0, f"Enemy1 should have invert_timer set to 3.0, but got {getattr(enemy1, 'invert_timer', 0.0)}"
    assert getattr(enemy2, "invert_timer", 0.0) == 3.0, f"Enemy2 should have invert_timer set to 3.0, but got {getattr(enemy2, 'invert_timer', 0.0)}"
    assert getattr(ally, "invert_timer", 0.0) == 0.0, f"Ally should not have invert_timer set, but got {getattr(ally, 'invert_timer', 0.0)}"
