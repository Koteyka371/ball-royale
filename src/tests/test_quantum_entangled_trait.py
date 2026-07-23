import pytest

class DummyBall:
    def __init__(self, id):
        self.id = id
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.traits = ["quantum_entangled"]
        self.speed = 100.0
        self.base_speed = 100.0
        self.damage = 10.0
        self.base_damage = 10.0

class DummyLobby:
    def get_traits(self, bid):
        return ["quantum_entangled"]

class DummyWorld:
    def __init__(self):
        self.dead_balls = []

def test_quantum_entanglement():
    from ai.game_modes import GameMode
    mode = GameMode()
    world = DummyWorld()
    b1 = DummyBall(1)
    b2 = DummyBall(2)
    balls = [b1, b2]

    # Mock the lobby via global import modification or directly setting traits.
    # In GameMode.setup, if lobby import fails, it uses b.traits directly.
    mode.setup(world, balls)

    assert getattr(b1, "is_quantum_entangled", False)
    assert getattr(b2, "is_quantum_entangled", False)

    # Tick to initialize HP trackers
    mode.tick(world, balls)
    assert b1.last_entangled_hp == 100.0
    assert b2.last_entangled_hp == 100.0

    # Damage b1
    b1.hp = 80.0
    mode.tick(world, balls)

    # b2 should lose 50% of 20 = 10 HP
    assert b2.hp == 90.0

    # Heal b2
    b2.hp = 94.0
    mode.tick(world, balls)

    # b1 should gain 50% of 4 = 2 HP
    assert b1.hp == 82.0

    # Kill b2
    b2.alive = False
    mode.tick(world, balls)

    # b1 should become enraged
    assert b1.quantum_enraged == True
    assert b1.speed >= 200.0
    assert b1.damage >= 20.0
