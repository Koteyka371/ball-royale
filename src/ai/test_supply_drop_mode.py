from game_modes import GAME_MODES

class MockEntity:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.alive = True

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.events = []
        self.next_id = 100

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_supply_drop_mode():
    mode = GAME_MODES["supply_drop"]
    world = MockWorld()

    ball = MockEntity(id=1, x=500.0, y=500.0, radius=20.0, ball_type="warrior", speed=100.0, damage=10.0, hp=100.0)
    ball.base_speed = 100.0
    ball.base_damage = 10.0
    world.balls = [ball]

    mode.setup(world, world.balls)

    # Tick to spawn booster
    mode.tick(world, world.balls, 10.1)

    assert len(world.boosters) == 1
    assert world.boosters[0]["supply_drop_type"] in ["invincibility", "speed", "damage"]
    assert world.boosters[0]["active"] is True

    # Force booster onto player
    booster = world.boosters[0]
    booster["x"] = ball.x
    booster["y"] = ball.y
    b_type = booster["supply_drop_type"]

    mode.tick(world, world.balls, 0.1)

    assert len(world.boosters) == 0
    if b_type == "invincibility":
        assert getattr(ball, "immunity_timer", 0) > 0
    elif b_type == "speed":
        assert getattr(ball, "speed_booster_timer", 0) > 0
        assert ball.speed > 100.0
    elif b_type == "damage":
        assert getattr(ball, "damage_booster_timer", 0) > 0
        assert ball.damage > 10.0

    print("Test passed!")

if __name__ == "__main__":
    test_supply_drop_mode()
