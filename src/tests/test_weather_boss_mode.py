import pytest
from ai.game_modes import GAME_MODES, WeatherBossMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.weather = "clear"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []
        self.next_id = 100

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self):
        self.id = 1
        self.hp = 100
        self.max_hp = 100
        self.alive = True

def test_weather_boss_mode_spawn():
    mode = GAME_MODES["weather_boss"]
    world = MockWorld()
    balls = [MockBall()]

    # Not intense weather -> boss shouldn't spawn
    world.arena.weather = "clear"
    for _ in range(60): # 1 second tick
        mode.tick(world, balls, 0.1)

    assert not any(getattr(b, "ball_type", "") == "neutral_boss" for b in world.balls)

    # Intense weather -> boss should spawn after 5s
    world.arena.weather = "blizzard"
    for _ in range(60): # 6 seconds tick
        mode.tick(world, balls, 0.1)

    bosses = [b for b in world.balls if getattr(b, "ball_type", "") == "neutral_boss"]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.name == "Storm Elemental"
    assert boss.team == "neutral"
    # Intensity builds up: 0.5 per sec * 6s = 3.0
    # Expected damage = 20 + 3.0 * 5 = 35.0
    assert 30 <= boss.damage <= 40

def test_weather_boss_mode_defeat():
    mode = WeatherBossMode()
    world = MockWorld()
    balls = []

    world.arena.weather = "hurricane"
    for _ in range(60):
        mode.tick(world, balls, 0.1)

    boss = [b for b in world.balls if getattr(b, "ball_type", "") == "neutral_boss"][0]

    # Kill boss
    boss.hp = 0
    mode.tick(world, balls, 0.1)

    assert not boss.alive
    assert len(world.boosters) == 1
    assert world.boosters[0].kind.startswith("legendary_")
    assert any(e[0] == "boss_defeated" for e in world.events)
