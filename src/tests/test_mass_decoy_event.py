import pytest
from ai.game_modes import GAME_MODES

def test_mass_decoy_event():
    assert "mass_decoy_event" in GAME_MODES
    mode = GAME_MODES["mass_decoy_event"]

    class MockArena:
        width = 1000
        height = 1000

    class MockWorld:
        def __init__(self):
            self.events = []
            self.balls = []
            self.next_id = 100
            self.arena = MockArena()

        def add_event(self, event_type, data):
            self.events.append((event_type, data))

    class MockBall:
        def __init__(self, id):
            self.id = id
            self.alive = True
            self.ball_type = "normal"
            self.is_decoy = False
            self.team = "red"
            self.x = 100
            self.y = 100
            self.radius = 15
            self.hp = 100
            self.max_hp = 100

    world = MockWorld()
    b1 = MockBall(1)
    b2 = MockBall(2)
    world.balls = [b1, b2]

    import random
    random.seed(42)

    # Tick to spawn decoys
    mode.tick(world, world.balls, delta=100.0) # force trigger

    assert len(world.balls) == 4

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) == 2
    assert decoys[0].decoy_type == "stationary"
    assert decoys[0].team == "red"
    assert decoys[1].team == "red"

    assert any(e[0] == "mass_decoy_spawn" for e in world.events)

    # Tick to end event
    mode.tick(world, world.balls, delta=11.0)

    # Decoys should be dead
    for d in decoys:
        assert d.hp == 0.0
        assert not d.alive
