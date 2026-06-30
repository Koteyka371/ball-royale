import math
from ai.action import Action

class MockBall:
    def __init__(self, id=0, ball_type="necromancer", team="team_necro", x=0, y=0, hp=100, max_hp=100, damage=10):
        self.id = id
        self.ball_type = ball_type
        self.team = team
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
        self.damage = damage
        self.speed = 100
        self.base_speed = 100
        self.base_damage = 10
        self.alive = True
        self.attack_timer = 0
        self.attack_range = 100

class MockWorld:
    def __init__(self, balls=None):
        self.balls = balls or []
        self.current_mode_name = "Normal"

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_necromancer_speed_buff_with_minion():
    necro = MockBall(id=1, ball_type="necromancer", team="necro_team", x=0, y=0)
    minion = MockBall(id=2, ball_type="minion", team="necro_team", x=50, y=50) # Within 150 aura
    world = MockWorld([necro, minion])

    action = Action(necro, world)
    action._apply_friendly_aura(1.0)

    # Base speed is 100, necro buff gives 1.5x -> 150
    assert necro.speed == 150

def test_necromancer_heal_on_attack():
    necro = MockBall(id=1, ball_type="necromancer", team="necro_team", x=0, y=0, hp=50, max_hp=100, damage=10)
    minion = MockBall(id=2, ball_type="minion", team="necro_team", x=50, y=50) # within 200 range
    enemy = MockBall(id=3, ball_type="enemy", team="enemy_team", x=10, y=0, hp=100)

    world = MockWorld([necro, minion, enemy])
    action = Action(necro, world)
    action._attempt_damage(necro, enemy)

    # 50 + 10 * 0.3 = 53
    assert necro.hp == 53

def test_necromancer_no_buff_without_minion():
    necro = MockBall(id=1, ball_type="necromancer", team="necro_team", x=0, y=0)
    world = MockWorld([necro])

    action = Action(necro, world)
    action._apply_friendly_aura(1.0)

    assert necro.speed == 100

def test_necromancer_no_heal_without_minion():
    necro = MockBall(id=1, ball_type="necromancer", team="necro_team", x=0, y=0, hp=50, max_hp=100, damage=10)
    enemy = MockBall(id=3, ball_type="enemy", team="enemy_team", x=10, y=0, hp=100)

    world = MockWorld([necro, enemy])
    action = Action(necro, world)
    action._attempt_damage(necro, enemy)

    assert necro.hp == 50
