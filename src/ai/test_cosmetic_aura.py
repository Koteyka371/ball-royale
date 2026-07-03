from ai.action import Action

class MockBall:
    def __init__(self):
        self.alive = True
        self.ball_type = "warrior"
        self.level = 1
        self.experience = 0

class MockWorld:
    def add_event(self, event_name, data):
        pass

def test_cosmetic_aura_on_level_up():
    ball = MockBall()
    world = MockWorld()
    action = Action(ball, world)

    # Give enough XP to reach level 3
    action._award_xp(ball, 200, world)

    assert ball.level == 2
    assert hasattr(ball, "cosmetic_aura_scale")
    assert ball.cosmetic_aura_scale > 1.0

    assert hasattr(ball, "cosmetic_aura_color")
    assert isinstance(ball.cosmetic_aura_color, tuple)
    assert len(ball.cosmetic_aura_color) == 4

if __name__ == "__main__":
    test_cosmetic_aura_on_level_up()
    print("All tests passed!")
