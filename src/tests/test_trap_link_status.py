import pytest

from unittest.mock import MagicMock
from ai.action import Action

class FakeBall:
    def __init__(self, x=0.0, y=0.0, hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.alive = alive
        self.id = id(self)
        self.team = "solo"
        self.ball_type = "basic"
        self.radius = 10.0
        self.stun_timer = 0.0
        self.poison_timer = 0.0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_trap_link_status():
    ball = FakeBall(0.0, 0.0)
    enemy = FakeBall(50.0, 0.0)
    enemy.team = "enemy"

    world = MagicMock()
    world.balls = [ball, enemy]
    world.arena.hazards = []
    world.arena.safe_zone_center = (500, 500)
    world.arena.safe_zone_radius = 2000
    world.arena.is_in_safe_zone.return_value = True
    world.arena.clamp_position.return_value = (0, 0, False)
    world.arena.danger_grid = {}

    action = Action(ball, world)
    ball.trap_link_target = enemy
    ball.trap_link_timer = 5.0

    # Run once to initialize prev variables
    action.execute("idle", 1.0)

    # Simulate stun
    ball.stun_timer = 5.0

    action.execute("idle", 1.0)

    # Check enemy status
    print("Enemy stun:", enemy.stun_timer)
    print("Ball stun:", ball.stun_timer)
    assert enemy.stun_timer == 5.0

if __name__ == '__main__':
    test_trap_link_status()

def test_trap_link_damage():
    ball = FakeBall(0.0, 0.0)
    enemy = FakeBall(50.0, 0.0)
    enemy.team = "enemy"

    world = MagicMock()
    world.balls = [ball, enemy]
    world.arena.hazards = []
    world.arena.safe_zone_center = (500, 500)
    world.arena.safe_zone_radius = 2000
    world.arena.is_in_safe_zone.return_value = True
    world.arena.clamp_position.return_value = (0, 0, False)
    world.arena.danger_grid = {}

    action = Action(ball, world)
    ball.trap_link_target = enemy
    ball.trap_link_timer = 5.0

    # Simulate damage
    ball.prev_hp = 100.0
    ball.hp = 80.0

    action.execute("idle", 1.0)
    assert enemy.hp == 80.0
