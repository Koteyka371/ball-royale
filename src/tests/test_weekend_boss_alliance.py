import pytest
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.entities = self.balls
        self.events = []

    def add_event(self, name, data):
        self.events.append((name, data))

class MockBall:
    def __init__(self, id_val, team):
        self.id = id_val
        self.team = team
        self.ball_type = "player"
        self.alive = True
        self.x = 100.0
        self.y = 100.0
        self.hp = 100.0
        self.max_hp = 100.0

def test_weekend_boss_alliance():
    mode = BattleRoyaleMode()
    world = MockWorld()

    player1 = MockBall(1, "Red")
    player2 = MockBall(2, "Blue")
    world.balls.extend([player1, player2])

    # Mock datetime to force weekend and rng to force spawn
    import datetime
    class MockDatetime:
        @classmethod
        def now(cls):
            class Date:
                def weekday(self):
                    return 5 # Saturday
            return Date()

    class MockRandom:
        def random(self):
            return 0.1 # < 0.2 to trigger spawn
        def randint(self, a, b):
            return a
        def choice(self, seq):
            return seq[0]
        def uniform(self, a, b):
            return (a+b)/2.0

    import sys
    sys.modules['datetime'].datetime = MockDatetime
    mode.random = MockRandom()

    # Tick to spawn boss
    mode.tick(world, world.balls, 0.016)

    # Verify boss spawned
    assert mode._weekend_boss_spawned
    boss = next((b for b in world.balls if getattr(b, "is_weekend_boss", False)), None)
    assert boss is not None

    # Verify alliance logic
    assert player1.team == "BossHunters"
    assert player2.team == "BossHunters"

    # Kill boss
    boss.alive = False

    # Tick again
    mode.tick(world, world.balls, 0.016)


    # Verify teams restored
    assert player1.team == "Red"
    assert player2.team == "Blue"

    # Cleanup
    import datetime as real_datetime
    sys.modules['datetime'].datetime = real_datetime.datetime
