import pytest
from ai.action import Action
from ai.ball_types_necromancer import Necromancer

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'safe_zone_center': [0,0], 'safe_zone_radius': 1000, 'hazards': []})()

class MockBall:
    def __init__(self, bid, btype, team, x, y):
        self.id = bid
        self.ball_type = btype
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.bone_armor_stacks = 0
        self.bone_armor_accumulator = 0.0
        self.speed = 2.0
        self.stun_timer = 0.0

def test_necromancer_aura():
    world = MockWorld()
    necro = MockBall(1, "necromancer", "A", 0, 0)
    necro.hp = 50.0
    enemy = MockBall(2, "warrior", "B", 10, 0)
    world.balls = [necro, enemy]

    action = Action(necro, world)

    # Delta of 2.0 -> damage = 5.0 * 2.0 = 10.0
    action._update_skill_timer(2.0)

    # Enemy takes 10 damage -> hp=90
    assert enemy.hp == 90.0

    # Damage dealt = 10 -> heal amount = 5
    # Necro hp = 50 + 5 = 55
    assert necro.hp == 55.0

    # Accumulator goes to 10
    assert necro.bone_armor_accumulator == 10.0
    assert necro.bone_armor_stacks == 0

    # Delta of 2.0 -> damage = 10.0 again
    action._update_skill_timer(2.0)

    assert enemy.hp == 80.0
    assert necro.hp == 60.0
    # Accumulator reaches 20, resets to 0 and gives 1 stack
    assert necro.bone_armor_accumulator == 0.0
    assert necro.bone_armor_stacks == 1
