import pytest
from ai.action import Action
from ai.game_modes import GameMode
from ai.test_action_advanced import MockWorld, MockBall

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class DummyHazard:
    pass

def test_frost_minion_fires_bolt():
    world = MockWorld()
    world.arena = MockArena()
    world.next_id = 1000

    fm = MockBall()
    fm.x = 100
    fm.y = 100
    fm.ball_type = "frost_minion"
    fm.hp = 15
    fm.team = "undead"
    fm.attack_timer = 0.0
    fm.speed = 2.5
    fm.id = 1

    enemy = MockBall()
    enemy.x = 200
    enemy.y = 100
    enemy.team = "hero"
    enemy.hp = 100
    enemy.id = 2

    world.balls = [fm, enemy]

    action = Action(fm, world)
    action.execute("idle", 1.0)

    assert len(world.arena.hazards) == 1
    bolt = world.arena.hazards[0]
    assert getattr(bolt, "kind", "") == "frost_bolt"
    assert getattr(bolt, "damage", 0) == 10.0
    assert getattr(bolt, "owner_id", None) == fm.id

def test_frost_bolt_hit():
    world = MockWorld()
    world.arena = MockArena()

    fm = MockBall()
    fm.id = 1

    enemy = MockBall()
    enemy.id = 2
    enemy.x = 250
    enemy.y = 100
    enemy.radius = 15.0
    enemy.hp = 100.0
    enemy.alive = True
    enemy.slow_timer = 0.0

    def take_damage(dmg):
        enemy.hp -= dmg
    enemy.take_damage = take_damage

    world._deal_damage = lambda attacker, target, dmg=None: target.take_damage(dmg if dmg else attacker.damage)

    world.balls = [fm, enemy]

    bolt = DummyHazard()
    bolt.x = 200
    bolt.y = 100
    bolt.radius = 8.0
    bolt.vx = 300.0
    bolt.vy = 0.0
    bolt.kind = "frost_bolt"
    bolt.owner_id = fm.id
    bolt.damage = 10.0
    bolt.duration = 5.0
    world.arena.hazards.append(bolt)

    mode = GameMode()
    mode.tick(world, world.balls, 0.2)

    assert bolt.duration == 0.0
    assert enemy.hp == 90.0
    assert enemy.slow_timer >= 2.0
