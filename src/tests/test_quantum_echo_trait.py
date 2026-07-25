import pytest

class DummyWorld:
    def __init__(self):
        self.events = []
        self.balls = []

class DummyBall:
    def __init__(self, bid):
        self.id = bid
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.traits = ["quantum_echo"]
        self.speed = 100.0
        self.skill = "dummy_skill"
        self.skill_timer = 0.0
        self.x = 0.0
        self.y = 0.0

def test_quantum_echo():
    from ai.game_modes import GameMode
    from ai.action import Action
    world = DummyWorld()
    b = DummyBall(1)
    b.x = 10.0
    b.y = 10.0
    b.hp = 100.0
    world.balls = [b]

    mode = GameMode()
    mode.setup(world, [b])

    assert getattr(b, "is_quantum_echo", False)

    # Tick Action.execute for 3 seconds to spawn the ghost
    action = Action(b, world)
    action.execute("idle", 3.0)

    assert getattr(b, "quantum_echo_ghost", None) is not None
    assert b.quantum_echo_ghost["x"] == 10.0
    assert b.quantum_echo_ghost["y"] == 10.0
    assert b.quantum_echo_ghost["hp"] == 100.0

    # Move ball and change hp
    b.x = 50.0
    b.y = 50.0
    b.hp = 20.0

    # Use skill
    b.skill_timer = 0.0
    action._use_skill()

    assert b.x == 10.0
    assert b.y == 10.0
    assert b.hp == 100.0
