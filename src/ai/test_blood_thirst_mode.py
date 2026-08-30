from ai.game_modes import GameMode, BloodThirstMode

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, hp, max_hp, lifesteal):
        self.id = id
        self.hp = hp
        self.max_hp = max_hp
        self.lifesteal = lifesteal
        self.alive = True
        self.hp_regen_timer = 5.0

def test_blood_thirst_setup():
    mode = BloodThirstMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100, 0.0), MockBall(2, 100, 100, 0.5)]
    mode.setup(world, balls)

    # Check that lifesteal is applied correctly
    assert abs(balls[0].lifesteal - 1.0) < 0.1
    assert abs(balls[1].lifesteal - 1.5) < 0.1

def test_blood_thirst_tick():
    mode = BloodThirstMode()
    world = MockWorld()
    balls = [MockBall(1, 10, 100, 2.0), MockBall(2, 1, 100, 2.0)]

    # After 1 sec (delta=1.0), drain should be 5.0
    mode.tick(world, balls, delta=1.0)

    # Ball 1 takes 5 damage -> hp = 5.0
    assert abs(balls[0].hp - 5.0) < 0.1
    assert balls[0].alive == True
    # natural regen timer should be forced to 0
    assert abs(balls[0].hp_regen_timer - 0.0) < 0.1

    # Ball 2 had 1 hp, drain of 5.0 -> dead
    assert abs(balls[1].hp - 0.0) < 0.1
    assert balls[1].alive == False
    assert abs(balls[1].hp_regen_timer - 0.0) < 0.1

    # Check if event was added
    assert len(world.events) == 1
    assert world.events[0][0] == "death"
    assert world.events[0][1]["id"] == 2
    assert world.events[0][1]["reason"] == "blood_thirst_drain"
