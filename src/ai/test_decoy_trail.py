import pytest
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x=100, y=100, vx=0, vy=0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 15.0
        self.alive = True
        self.is_decoy = False
        self.team = "red"
        self.cosmetic = "hat"
        self.color = "blue"
        self.hp = 100
        self.max_hp = 100
        self.mass = 1.0
        self.charge_timer = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

def test_decoy_trail_mode():
    world = MockWorld()
    b1 = MockBall(1, 100, 100, 5, 0)
    world.balls.append(b1)

    mode = GAME_MODES["decoy_trail"]

    # Tick past 5 seconds to trigger trail timer
    mode.tick(world, world.balls, delta=5.1)

    assert getattr(b1, "decoy_trail_timer", 0.0) == 2.0
    assert getattr(b1, "decoy_trail_duration", 0.0) == 1.0

    action = Action(b1, world)

    # Tick action to spawn decoy
    action.execute("attack", delta=0.016)

    assert len(world.arena.hazards) > 0
    decoy = world.arena.hazards[0]
    assert decoy.kind == "mirage_decoy"
    assert decoy.team == "red"
    assert decoy.cosmetic == "hat"
    assert decoy.color == "blue"
    assert decoy.vx == 5
    assert decoy.vy == 0
    assert decoy.owner_id == 1

if __name__ == "__main__":
    test_decoy_trail_mode()
    print("Tests passed!")
