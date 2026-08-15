import pytest
from system.crowd_system import CrowdSystem

class DummyWorld:
    def __init__(self):
        self.events = []
        self.game_mode = DummyGameMode()
        self.tick = 0

    def add_event(self, kind, data):
        self.events.append((kind, data))

class DummyGameMode:
    def _make_juggernaut(self, world, b):
        b.team = "Juggernaut"

class DummyBall:
    def __init__(self, id):
        self.id = id
        self.alive = True
        self.ball_type = "basic"
        self.kills = 0

def test_spawnboss_juggernaut():
    world = DummyWorld()
    cs = CrowdSystem(world)

    b1 = DummyBall(1)
    b2 = DummyBall(2)
    balls = [b1, b2]

    cs.process_external_command("user1", "!spawnboss juggernaut", balls)
    assert any(getattr(b, "team", "") == "Juggernaut" for b in balls)
    assert world.events[-1][0] == "juggernaut_change"

def test_spawnboss_phantom_juggernaut():
    world = DummyWorld()
    cs = CrowdSystem(world)

    b1 = DummyBall(1)
    balls = [b1]

    cs.process_external_command("user2", "!spawnboss phantom juggernaut", balls)
    assert any(getattr(b, "team", "") == "Phantom Juggernaut" for b in balls)
    assert world.events[-1][0] == "juggernaut_change"

def test_spawnboss_elementalist():
    world = DummyWorld()
    cs = CrowdSystem(world)

    b1 = DummyBall(1)
    balls = [b1]

    cs.process_external_command("user3", "!spawnboss elementalist", balls)
    assert any(b.ball_type == "elementalist" for b in balls)
    assert any(getattr(b, "team", "") == "Boss" for b in balls)
    assert world.events[-1][0] == "boss_change"
