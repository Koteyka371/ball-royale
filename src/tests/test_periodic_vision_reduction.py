import math
from ai.game_modes import PeriodicVisionReductionEventMode

class MockBall:
    def __init__(self, id, team, ball_type):
        self.id = id
        self.team = team
        self.ball_type = ball_type
        self.base_perception_radius = 500.0
        self.perception_radius = 500.0
        self.periodic_vision_reduction_applied = False

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, type, data):
        self.events.append({"type": type, "data": data})

def test():
    mode = PeriodicVisionReductionEventMode()
    world = MockWorld()
    b1 = MockBall(1, "team1", "player")
    balls = [b1]

    mode.setup(world, balls)

    # 15 seconds cooldown
    assert not mode.is_active
    mode.tick(world, balls, 10.0)
    assert not mode.is_active

    # After another 5 seconds, should activate
    mode.tick(world, balls, 6.0)
    assert mode.is_active
    assert b1.perception_radius == 250.0

    # It lasts 5 seconds
    mode.tick(world, balls, 3.0)
    assert mode.is_active
    assert b1.perception_radius == 250.0

    mode.tick(world, balls, 3.0)
    assert not mode.is_active
    assert b1.perception_radius == 500.0

    print("Test passed!")

if __name__ == "__main__":
    test()
