import pytest
from ai.game_modes import GAME_MODES, WanderingDecoysMode, WanderingDecoy

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.alive = True
        self.is_decoy = False
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.team = "A"
        self.ball_type = "basic"
        self.speed = 2.0
        self.base_speed = 100.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000

def test_wandering_decoys_spawning():
    mode = GAME_MODES["wandering_decoys"]
    world = MockWorld()

    player1 = MockBall(1, 100.0, 100.0)
    world.balls.append(player1)

    mode.setup(world, world.balls)

    # Tick for just over 10 seconds to trigger spawn
    for _ in range(int(10.1 / 0.016) + 1):
        mode.tick(world, world.balls, 0.016)

    # There should be 1 real ball and 1-3 decoys
    assert len(world.balls) >= 2, "Decoy should be created"

    # Find the decoy
    decoy = next((b for b in world.balls if getattr(b, "is_decoy", False)), None)
    assert decoy is not None
    assert decoy.kind == "wandering_decoy"
    assert decoy.alive == True
    assert decoy.team == "A"
    assert decoy.ball_type == "basic"

def test_wandering_decoys_one_hit_kill():
    player1 = MockBall(1, 100.0, 100.0)
    decoy = WanderingDecoy(1000, 50.0, 50.0, player1)

    assert decoy.alive == True
    assert decoy.hp == 1.0

    decoy.take_damage(0.1)

    assert decoy.alive == False
    assert decoy.hp == 0.0

def test_wandering_decoys_movement():
    player1 = MockBall(1, 100.0, 100.0)
    decoy = WanderingDecoy(1000, 50.0, 50.0, player1)

    initial_x = decoy.x
    initial_y = decoy.y

    # Tick to update movement
    for _ in range(10):
        decoy.update(0.1)

    # Should have moved towards its target_x/target_y, or chosen a new one
    assert decoy.x != initial_x or decoy.y != initial_y
