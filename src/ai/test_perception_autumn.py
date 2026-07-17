import math
from ai.perception import Perception

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True, team="red"):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.team = team
        self.max_hp = 100
        self.hp = 100
        self.damage = 10.0
        self.speed = 100.0
        self.x = 0.0
        self.y = 0.0
        self.perception_radius = 300.0

class MockArena:
    def __init__(self):
        self.is_windy = False
        self.is_night = False
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []

    def get_nearby_entities(self, ball, radius):
        enemies = []
        for b in self.balls:
            if b.team != ball.team:
                dist = math.sqrt((b.x - ball.x)**2 + (b.y - ball.y)**2)
                if dist <= radius:
                    enemies.append(b)
        return {"enemies": enemies, "allies": [], "boosters": [], "traps": []}

def test_autumn_vision_reduced():
    ball = MockBall(1)

    # Normal perception
    world_normal = MockWorld()
    p_normal = Perception(ball, world_normal)

    # Windy perception
    world_windy = MockWorld()
    world_windy.arena.is_windy = True
    p_windy = Perception(ball, world_windy)

    # Base radius without flares/night is 2000.0 due to default max(perception_radius, 2000.0)
    radius_normal = 2000.0
    radius_windy = 2000.0 * 0.7

    # Ensure enemies outside the reduced radius but inside the normal radius are not seen
    enemy = MockBall(2, team="blue")
    enemy.x = radius_windy + 100.0 # Outside windy radius, inside normal
    enemy.y = 0.0
    world_windy.balls.append(enemy)
    world_normal.balls.append(enemy)

    scan_normal = p_normal.scan()
    scan_windy = p_windy.scan()

    assert len(scan_normal["enemies"]) == 1
    assert len(scan_windy["enemies"]) == 0

def test_thermal_vision_ignores_weather():
    ball = MockBall(1)
    ball.has_thermal_vision = True

    # Normal perception
    world_normal = MockWorld()
    p_normal = Perception(ball, world_normal)

    # Windy perception
    world_windy = MockWorld()
    world_windy.arena.is_windy = True
    p_windy = Perception(ball, world_windy)

    radius_normal = 2000.0
    radius_windy = 2000.0  # Should NOT be reduced because of thermal vision

    enemy = MockBall(2, team="blue")
    enemy.x = 2000.0 * 0.7 + 100.0
    enemy.y = 0.0
    world_windy.balls.append(enemy)
    world_normal.balls.append(enemy)

    scan_normal = p_normal.scan()
    scan_windy = p_windy.scan()

    assert len(scan_normal["enemies"]) == 1
    assert len(scan_windy["enemies"]) == 1
