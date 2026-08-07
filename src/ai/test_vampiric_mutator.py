from ai.game_modes import GameMode, VampiricMutatorMode

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

def test_vampiric_mutator_setup():
    mode = VampiricMutatorMode()
    world = MockWorld()
    balls = [MockBall(1, 100, 100, 0.0), MockBall(2, 100, 100, 0.5)]
    mode.setup(world, balls)

    # Check that lifesteal is applied correctly
    assert balls[0].lifesteal == 2.5
    assert balls[1].lifesteal == 3.0

def test_vampiric_mutator_tick():
    mode = VampiricMutatorMode()
    world = MockWorld()
    balls = [MockBall(1, 10, 100, 2.0), MockBall(2, 1, 100, 2.0)]

    # After 1 sec (delta=1.0), drain should be 5.0
    mode.tick(world, balls, delta=1.0)

    assert balls[0].hp == 5.0
    assert balls[0].alive == True

    # Ball 2 had 1 hp, drain of 5.0 -> dead
    assert balls[1].hp == 0.0
    assert balls[1].alive == False

    # Check if event was added
    assert len(world.events) == 1
    assert world.events[0][0] == "death"
    assert world.events[0][1]["id"] == 2
