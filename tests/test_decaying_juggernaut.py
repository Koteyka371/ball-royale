import pytest
from ai.decaying_juggernaut import DecayingJuggernautMode

class MockWorld:
    def __init__(self):
        self.tick_timer = 0
        self.dead_balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, btype):
        self.id = id
        self.ball_type = btype
        self.alive = True
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.radius = 10.0
        self.speed = 100.0
        self.mass = 1.0

def get_jug(balls):
    for b in balls:
        if getattr(b, "team", "") == "Juggernaut":
            return b
    return None

def test_decaying_juggernaut_decay():
    world = MockWorld()
    # Just 1 ball so there's no alive hunters to swap to!
    balls = [MockBall(1, "normal")]

    mode = DecayingJuggernautMode()
    mode.setup(world, balls)

    jug = get_jug(balls)
    assert jug is not None
    assert jug.max_hp == 1000.0
    assert getattr(jug, "juggernaut_decay", None) == 1.0

    # Tick for 10 seconds (1000 ticks of 0.01)
    for _ in range(1000):
        mode.tick(world, balls, 0.01)

    jug = get_jug(balls)
    # Should decay by 0.02 per second -> 0.2 over 10 seconds
    assert jug.juggernaut_decay == pytest.approx(0.8, abs=0.01)
    assert jug.max_hp == pytest.approx(820.0, abs=5.0)

    # Tick for another 50 seconds to hit the cap of 0.2
    for _ in range(5000):
        mode.tick(world, balls, 0.01)

    jug = get_jug(balls)
    assert jug.juggernaut_decay == pytest.approx(0.2, abs=0.01)
    assert jug.max_hp == pytest.approx(280.0, abs=5.0)
