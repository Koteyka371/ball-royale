import pytest
import math

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.boosters = []
        self.events = []
        self.balls = []

class DummyArena:
    def __init__(self):
        self.hazards = []

class DummyHazard:
    def __init__(self, kind):
        self.kind = kind
        self.x = 0
        self.y = 0

class DummyBall:
    def __init__(self, x=0, y=0, team="red", ball_type="basic"):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.radius = 10
        self.damage = 20
        self.inventory = []
        self.stun_timer = 0
        self.id = id(self)

    def take_damage(self, dmg):
        self.hp -= dmg

from ai.action import Action

def test_directional_shield_pickup_and_use():
    world = DummyWorld()
    ball = DummyBall()
    world.balls = [ball]
    action = Action(ball, world)

    # Add to arena
    h = DummyHazard("directional_shield_item")
    world.arena.hazards.append(h)

    # Pickup (via finding nearest) - we mock this or just add to inventory directly to test use
    ball.inventory.append("directional_shield_item")

    enemy = DummyBall(100, 0, team="blue")
    world.balls.append(enemy)

    action.execute("attack", 1.0)

    assert "directional_shield_item" not in ball.inventory
    assert ball.directional_shield_active == True
    assert ball.directional_shield_timer == 4.0

    # Since enemy is at (100, 0), angle should be 0
    assert abs(ball.directional_shield_angle) < 0.01

def test_directional_shield_damage_reflect():
    world = DummyWorld()
    ball = DummyBall() # target
    world.balls = [ball]
    action = Action(ball, world)

    ball.directional_shield_active = True
    ball.directional_shield_timer = 5.0
    ball.directional_shield_angle = 0.0 # Facing right

    attacker = DummyBall(100, 0, team="blue") # Right side
    attacker.damage = 10.0
    # Simulate ranged attack from attacker

    action._attempt_damage(attacker, ball)

    # It should reflect damage to attacker (1.5x) using suspended_projectiles
    assert ball.hp == 100 # No damage taken
    assert attacker.hp == 100 # Attacker HP not modified yet, projectile is suspended
    assert len(ball.suspended_projectiles) == 1
    assert ball.suspended_projectiles[0]["damage"] == 15.0

    assert ball.directional_shield_active == True # Not shattered

def test_directional_shield_melee_shatter():
    world = DummyWorld()
    ball = DummyBall() # target
    world.balls = [ball]
    action = Action(ball, world)

    ball.directional_shield_active = True
    ball.directional_shield_timer = 5.0
    ball.directional_shield_angle = 0.0 # Facing right

    attacker = DummyBall(15, 0, team="blue") # Close (melee)
    attacker.damage = 10.0

    action._attempt_damage(attacker, ball)

    # Melee hit from front: shatters, stuns user
    assert ball.hp == 100 # No damage taken from the hit? The prompt says "taking a direct melee hit shatters the shield and stuns the user." It doesn't explicitly say the user takes damage, but usually blocking a melee attack completely might mitigate damage, or it might take damage. The prompt doesn't say "takes no damage". If we returned early, they take no damage. Let's assume they take no damage but get stunned.
    assert ball.directional_shield_active == False
    assert ball.directional_shield_timer == 0.0
    assert ball.stun_timer >= 2.0

    assert attacker.hp == 100 # Attacker takes no damage
