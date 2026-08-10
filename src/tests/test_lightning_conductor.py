import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 800
        self.height = 600
        self.weather = "clear"
    def update_zone(self, tick, delta=None): pass
    def clamp_position(self, x, y, radius=0): return x, y, False

class MockBall:
    def __init__(self, id=1, hp=100.0, speed=2.0, damage=10.0, x=0.0, y=0.0, traits=None, team="test_team"):
        self.ball_type = "basic"
        self.hp = hp
        self.speed = speed
        self.damage = damage
        self.x = x
        self.y = y
        self.id = id
        self.team = team
        self.alive = True
        self.radius = 10.0
        self.traits = traits or []
        self.base_speed = speed
        self.base_damage = damage

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.game_mode = None
    def add_event(self, t, d):
        self.events.append((t, d))
    def _deal_damage(self, attacker, target):
        target.take_damage(attacker.damage)

class MockHazard:
    def __init__(self, kind, damage, radius, x, y, hit_targets=False):
        self.id = 1
        self.kind = kind
        self.damage = damage
        self.radius = radius
        self.x = x
        self.y = y
        self.hit_targets = hit_targets

def test_lightning_conductor_trait():
    # A defensive skill where being hit by any form of lightning gives the player a brief burst of incredible speed and makes their next attack bounce to up to 2 nearby enemies.
    ball = MockBall(id=1, traits=["lightning_conductor"])
    world = MockWorld()
    world.balls.append(ball)

    enemy1 = MockBall(id=2, x=50, y=50, team="enemy")
    enemy2 = MockBall(id=3, x=100, y=100, team="enemy")
    enemy3 = MockBall(id=4, x=150, y=150, team="enemy")

    world.balls.extend([enemy1, enemy2, enemy3])

    action = Action(ball, world)

    # Hit by lightning
    lightning = MockHazard(kind="lightning_strike", damage=50.0, radius=30.0, x=0.0, y=0.0)
    world.arena.hazards.append(lightning)

    delta = 0.1
    action.execute("idle", delta)

    # Ensure it gets the speed buff timer and charges
    assert getattr(ball, "speed_buff_timer", 0.0) >= 2.9
    assert getattr(ball, "lightning_conductor_charges", 0) == 1

    # Now attack an enemy (simulate action internally doing deal damage or attempt damage)
    world.arena.hazards = []

    ball.damage = 20.0
    action._attempt_damage(ball, enemy1)

    assert enemy1.hp == 100.0 - 20.0
    # Chain lightning should bounce to enemy2 and enemy3
    assert enemy2.hp == 100.0 - 10.0
    assert enemy3.hp == 100.0 - 10.0

    assert ball.lightning_conductor_charges == 0
