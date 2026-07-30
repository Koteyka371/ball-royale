import pytest
from ai.game_modes import DecoySwapMode

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "blue"
        self.is_decoy = False
        self.ball_type = "player"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 100

    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})

def test_decoy_swap_spawn():
    mode = DecoySwapMode()
    world = MockWorld()

    player1 = MockBall(1, 100.0, 100.0)
    world.balls = [player1]

    # Tick to pre_spawn_time
    mode.tick(world, world.balls, delta=11.5)

    # Should have spawned a decoy
    assert len(world.balls) == 2
    decoy = world.balls[1]
    assert decoy.is_decoy is True
    assert decoy.owner_id == 1
    assert decoy.x == 100.0
    assert decoy.y == 100.0

def test_decoy_swap_execute():
    mode = DecoySwapMode()
    world = MockWorld()

    player1 = MockBall(1, 100.0, 100.0)
    player2 = MockBall(2, -100.0, -100.0)

    # Provide a decoy for player 1, but player 2 lacks one
    decoy1 = MockBall(101, 50.0, 50.0)
    decoy1.is_decoy = True
    decoy1.owner_id = 1

    world.balls = [player1, player2, decoy1]

    # Tick to pre_spawn_time to spawn decoy for player2
    mode.tick(world, world.balls, delta=11.5)

    assert len(world.balls) == 4
    decoy2 = world.balls[-1]
    assert decoy2.owner_id == 2
    assert decoy2.x == -100.0
    assert decoy2.y == -100.0

    # Tick to swap time (12.0 total, we already did 11.5)
    mode.tick(world, world.balls, delta=0.5)

    # Player 1 should swap with decoy1
    assert player1.x == 50.0
    assert player1.y == 50.0
    assert decoy1.x == 100.0
    assert decoy1.y == 100.0

    # Player 2 should swap with decoy2
    assert player2.x == -100.0
    assert player2.y == -100.0

    # Verify events
    swap_events = [e for e in world.events if e.get('type') == 'visual_effect' and e.get('data', {}).get('type') == 'teleport_swap']
    assert len(swap_events) == 2
