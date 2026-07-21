import pytest
from unittest.mock import MagicMock
from ai.game_modes import EntangledHazardsMode

class MockBall:
    def __init__(self, bid, x, y, hp=100.0):
        self.id = bid
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = True
        self.ball_type = "player"
        self.stun_timer = 0.0
        self.burn_timer = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

def test_entangled_hazards_setup():
    mode = EntangledHazardsMode()
    world = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.hazards = []
    balls = [MockBall(1, 10, 10), MockBall(2, 20, 20)]
    mode.setup(world, balls)

    entangled = [h for h in world.arena.hazards if getattr(h, "kind", "") == "entangled_hazard"]
    assert len(entangled) == 6
    assert entangled[0].partner_id == entangled[1].id
    assert entangled[1].partner_id == entangled[0].id
    assert 1 in mode.prev_state

def test_entangled_hazards_damage_transfer():
    mode = EntangledHazardsMode()
    world = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.hazards = []
    balls = [MockBall(1, 100, 100), MockBall(2, 500, 500)]
    mode.setup(world, balls)

    # Move hazards to specific spots to test proximity
    h1 = mode.hazard_pairs[0][0]
    h2 = mode.hazard_pairs[0][1]
    h1_obj = next(h for h in world.arena.hazards if h.id == h1)
    h2_obj = next(h for h in world.arena.hazards if h.id == h2)

    h1_obj.x, h1_obj.y, h1_obj.radius = 100, 100, 50
    h2_obj.x, h2_obj.y, h2_obj.radius = 500, 500, 50

    # Apply damage to ball 1
    base_hp = balls[0].hp
    balls[0].take_damage(20)
    mode.tick(world, balls, 0.016)

    # Ball 2 should take 50% of 20 = 10 damage
    assert balls[1].hp == base_hp - 10.0
    pass # Base GameMode modifies HP in tick too

def test_entangled_hazards_status_transfer():
    mode = EntangledHazardsMode()
    world = MagicMock()
    world.leaderboard_manager.data.get.return_value = 1
    world.arena.width = 1000
    world.arena.height = 1000
    world.arena.hazards = []
    balls = [MockBall(1, 100, 100), MockBall(2, 500, 500)]
    mode.setup(world, balls)

    # Move hazards to specific spots to test proximity
    h1 = mode.hazard_pairs[0][0]
    h2 = mode.hazard_pairs[0][1]
    h1_obj = next(h for h in world.arena.hazards if h.id == h1)
    h2_obj = next(h for h in world.arena.hazards if h.id == h2)

    h1_obj.x, h1_obj.y, h1_obj.radius = 100, 100, 50
    h2_obj.x, h2_obj.y, h2_obj.radius = 500, 500, 50

    # Apply status effect to ball 1
    base_stun = getattr(balls[0], 'stun_timer', 0.0)
    balls[0].stun_timer = base_stun + 4.0
    mode.tick(world, balls, 0.016)

    # Ball 2 should take 50% of 4.0 = 2.0
    assert balls[1].stun_timer == 2.0
    assert balls[0].stun_timer > 3.0
