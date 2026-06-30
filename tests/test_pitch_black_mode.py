import math
from ai.game_modes import PitchBlackMode
from ai.perception import Perception

class MockBall:
    def __init__(self, ball_id, ball_type, team, x, y, vx=0.0, vy=0.0):
        self.id = ball_id
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.alive = True
        self.perception_radius = 250.0

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.game_mode = None
        self.entities = {"enemies": [], "allies": [], "boosters": [], "traps": []}

    def get_nearby_entities(self, ball, radius):
        return self.entities

def test_pitch_black_setup():
    mode = PitchBlackMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior", "warrior", 0, 0)]
    mode.setup(world, balls)

    assert getattr(balls[0], "is_pitch_black", False) == True
    assert balls[0].base_perception_radius == 250.0
    assert balls[0].perception_radius == 250.0

def test_pitch_black_perception():
    mode = PitchBlackMode()
    world = MockWorld()
    world.game_mode = mode

    # Ball facing right (vx=1, vy=0)
    # Cone is 90 degrees: -45 to +45 degrees relative to facing direction
    b1 = MockBall(1, "warrior", "warrior", 0, 0, vx=1.0, vy=0.0)
    b1.is_pitch_black = True

    # Enemy straight ahead (0 degrees) - inside cone
    e1 = MockBall(2, "warrior", "enemy", 50, 0)
    # Enemy above (90 degrees) - outside cone
    e2 = MockBall(3, "warrior", "enemy", 0, 50)
    # Enemy behind (180 degrees) - outside cone
    e3 = MockBall(4, "warrior", "enemy", -50, 0)
    # Enemy slightly up-right (approx 45 degrees) - should be inside if exact or slightly less
    e4 = MockBall(5, "warrior", "enemy", 50, 40)

    world.entities["enemies"] = [e1, e2, e3, e4]

    p = Perception(b1, world)
    data = p.scan()

    # Only e1 and e4 should be detected
    detected_ids = [e.id for e in data["enemies"]]
    assert 2 in detected_ids
    assert 5 in detected_ids
    assert 3 not in detected_ids
    assert 4 not in detected_ids
