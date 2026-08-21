from ai.ball_types_necromancer import Necromancer
from ai.action import Action
import math

class DummyWorld:
    def __init__(self):
        self.balls = []

def test_bone_splinters():
    world = DummyWorld()
    necro = Necromancer(1, 0.0, 0.0)
    necro.team = 'team_necro'
    world.balls.append(necro)
    necro.world = world

    enemy = type('Enemy', (), {})()
    enemy.id = 2
    enemy.x = 10.0
    enemy.y = 10.0
    enemy.hp = 100.0
    enemy.alive = True
    enemy.team = 'team_enemy'
    enemy.ball_type = 'enemy'
    def take_damage(amount):
        enemy.hp -= amount
        if enemy.hp <= 0: enemy.alive = False
    enemy.take_damage = take_damage
    world.balls.append(enemy)

    necro.bone_armor_stacks = 1
    # 50 damage -> 10 negated, 40 taken
    necro.take_damage(50.0)

    assert necro.bone_armor_stacks == 0
    assert necro.bone_splinters_damage == 10.0
    assert necro.hp == 90.0 - 40.0

    action = Action(necro, world)
    action.execute("idle", 0.1)

    assert enemy.hp == 90.0
    assert getattr(necro, 'bone_splinters_damage', 0.0) == 0.0
