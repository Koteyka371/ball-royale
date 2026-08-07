from ai.game_modes import GAME_MODES, SwapLowestHPMutator

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, kind, data):
        self.events.append((kind, data))

class MockBall:
    def __init__(self, id, team, hp, max_hp, x, y):
        self.id = id
        self.team = team
        self.hp = hp
        self.max_hp = max_hp
        self.x = x
        self.y = y
        self.alive = True
        self.ball_type = "player"
        self.low_hp_swap_triggered = False
        self.name = f"Ball_{id}"

def test_low_hp_swap_mutator_exists():
    assert "low_hp_swap_mutator" in GAME_MODES
    assert isinstance(GAME_MODES["low_hp_swap_mutator"], SwapLowestHPMutator)

def test_low_hp_swap_triggers():
    world = MockWorld()
    mode = GAME_MODES["low_hp_swap_mutator"]

    b1 = MockBall(1, "team1", 20.0, 100.0, 100, 100) # 20%, should swap
    b2 = MockBall(2, "team2", 80.0, 100.0, 200, 200)
    b3 = MockBall(3, "team2", 90.0, 100.0, 300, 300) # Highest HP enemy

    balls = [b1, b2, b3]
    mode.tick(world, balls, 0.1)

    assert b1.low_hp_swap_triggered == True
    assert b1.x == 300 and b1.y == 300
    assert b3.x == 100 and b3.y == 100
    assert b2.x == 200 and b2.y == 200 # Unchanged

def test_low_hp_swap_ignores_teammates():
    world = MockWorld()
    mode = GAME_MODES["low_hp_swap_mutator"]

    b1 = MockBall(1, "team1", 20.0, 100.0, 100, 100) # 20%, should swap
    b2 = MockBall(2, "team1", 90.0, 100.0, 200, 200) # Highest HP, but teammate
    b3 = MockBall(3, "team2", 50.0, 100.0, 300, 300) # Only enemy

    balls = [b1, b2, b3]
    mode.tick(world, balls, 0.1)

    assert b1.low_hp_swap_triggered == True
    assert b1.x == 300 and b1.y == 300
    assert b3.x == 100 and b3.y == 100
    assert b2.x == 200 and b2.y == 200 # Unchanged

def test_low_hp_swap_triggers_only_once():
    world = MockWorld()
    mode = GAME_MODES["low_hp_swap_mutator"]

    b1 = MockBall(1, "team1", 20.0, 100.0, 100, 100)
    b2 = MockBall(2, "team2", 90.0, 100.0, 200, 200)

    balls = [b1, b2]
    mode.tick(world, balls, 0.1)

    assert b1.x == 200 and b1.y == 200
    assert b2.x == 100 and b2.y == 100
    assert b1.low_hp_swap_triggered == True

    # Move them again to test if it swaps again
    b1.x, b1.y = 500, 500
    b2.x, b2.y = 600, 600

    mode.tick(world, balls, 0.1)
    # Should not swap because triggered flag is True and HP is still low
    assert b1.x == 500 and b1.y == 500
    assert b2.x == 600 and b2.y == 600

    # Heal above 30%
    b1.hp = 40.0
    mode.tick(world, balls, 0.1)
    assert b1.low_hp_swap_triggered == False

    # Damage below 30% again
    b1.hp = 10.0
    mode.tick(world, balls, 0.1)
    assert b1.x == 600 and b1.y == 600
    assert b2.x == 500 and b2.y == 500
    assert b1.low_hp_swap_triggered == True
