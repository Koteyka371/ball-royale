import pytest
from ai.game_modes import GameMode, GAME_MODES
from unittest.mock import MagicMock

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.stun_timer = 0.0

class MockHazard:
    def __init__(self, kind, x=0, y=0, radius=50):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius
        self.active = True
        self.duration = 10.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 800

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.leaderboard_manager = MagicMock()
        self.leaderboard_manager.data.get.return_value = 1

def test_shockwave():
    mode = GAME_MODES['magnetic_shockwave']
    world = MockWorld()
    b1 = MockBall(x=10, y=10)
    b2 = MockBall(x=400, y=400) # center, touches anchor
    balls = [b1, b2]

    # Fast forward to spawn anchor
    mode.tick(world, balls, delta=5.1)

    assert mode.anchor is not None
    assert len(world.arena.hazards) == 1

    # Check stun
    mode.tick(world, balls, delta=0.1)
    assert b2.stun_timer >= 2.0
    assert b1.stun_timer == 0.0

    # Fast forward to shockwave
    mode.tick(world, balls, delta=3.9) # Total timer = 0.1 + 3.9 = 4.0
    mode.tick(world, balls, delta=0.1) # Exceeds 4.0 -> turns on

    # Shockwave should be active now
    assert mode.active_shockwave == True

    prev_hp = b1.hp
    prev_vx = b1.vx
    prev_vy = b1.vy

    # Apply shockwave
    mode.tick(world, balls, delta=0.1)

    # Check damage and pull
    # (distance from 10,10 to 400,400 is approx 551, which is > 400, so b1 is not pulled)
    # Let's test with a ball closer to the anchor
    b3 = MockBall(x=350, y=350)
    balls.append(b3)
    prev_hp_3 = b3.hp
    prev_vx_3 = b3.vx

    mode.tick(world, balls, delta=0.1)
    assert b3.hp < prev_hp_3
    assert b3.vx > prev_vx_3
