import pytest
from src.ai.action import Action
from src.ai.ball_types_elementalist import Elementalist
from src.ai.ball_types_warrior import Warrior
from src.ai.ball_types_bomber import Bomber

class DummyBall:
    def __init__(self, id, x, y, skill):
        self.id = id
        self.x = x
        self.y = y
        self.skill = skill
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.team_message = None

    def take_damage(self, amount):
        self.hp -= amount

class DummyWorld:
    def __init__(self, balls):
        self.balls = balls

def test_synergy_steam_explosion():
    elementalist = DummyBall(1, 0, 0, "elemental_burst")
    warrior = DummyBall(2, 50, 0, "wave_attack") # ally
    enemy = DummyBall(3, 100, 0, "none") # enemy

    world = DummyWorld([elementalist, warrior, enemy])
    action = Action(elementalist, world)

    # Mock methods
    action._get_allies = lambda: [warrior]
    action._get_enemies = lambda: [enemy]

    action._check_synergy("elemental_burst", elementalist.x, elementalist.y, 150.0)

    assert enemy.hp == 50 # took 50 damage
    assert enemy.x > 100 # pushed back

def test_synergy_meteor_strike():
    dasher = DummyBall(1, 0, 0, "dash")
    berserker = DummyBall(2, 50, 0, "rage_burst")
    enemy = DummyBall(3, 50, 0, "none")

    world = DummyWorld([dasher, berserker, enemy])
    action = Action(dasher, world)

    action._get_allies = lambda: [berserker]
    action._get_enemies = lambda: [enemy]

    action._check_synergy("dash", dasher.x, dasher.y, 150.0)

    assert enemy.hp == 20
    assert getattr(enemy, "stutter_timer", 0.0) == 1.0

def test_synergy_hellfire():
    mage = DummyBall(1, 0, 0, "fireball")
    bomber = DummyBall(2, 50, 0, "explosion")
    enemy = DummyBall(3, 50, 0, "none")

    world = DummyWorld([mage, bomber, enemy])
    action = Action(mage, world)

    action._get_allies = lambda: [bomber]
    action._get_enemies = lambda: [enemy]

    action._check_synergy("fireball", mage.x, mage.y, 150.0)

    assert getattr(enemy, "dot_duration", 0.0) == 5.0
    assert getattr(enemy, "dot_damage_per_tick", 0.0) == 10.0

def test_synergy_sanctuary():
    paladin = DummyBall(1, 0, 0, "holy_shield")
    healer = DummyBall(2, 50, 0, "heal_ally")
    healer.hp = 10 # injured

    world = DummyWorld([paladin, healer])
    action = Action(paladin, world)

    action._get_allies = lambda: [healer]
    action._get_enemies = lambda: []

    action._check_synergy("holy_shield", paladin.x, paladin.y, 150.0)

    assert healer.hp == 100
