import math
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': [], 'items': []})()
        self.balls = []
        self.boosters = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id, x, y, hp=100.0, team="A"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.alive = True
        self.skill = "chain_bounce_attack"
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0
        self.damage = 10.0

    def use_skill(self):
        pass

def test_chain_bounce_skill():
    world = MockWorld()

    # Attacker
    attacker = MockBall(1, 100, 100, team="A")

    # Enemies
    enemy1 = MockBall(2, 200, 100, team="B", hp=100) # distance 100 from attacker
    enemy2 = MockBall(3, 300, 100, team="B", hp=100) # distance 100 from enemy1
    enemy3 = MockBall(4, 400, 100, team="B", hp=100) # distance 100 from enemy2
    enemy4 = MockBall(5, 500, 100, team="B", hp=100) # distance 100 from enemy3
    enemy5 = MockBall(6, 600, 100, team="B", hp=100) # distance 100 from enemy4

    world.balls = [attacker, enemy1, enemy2, enemy3, enemy4, enemy5]

    action = Action(attacker, world)
    action._get_enemies = lambda: [b for b in world.balls if b.team != attacker.team]

    action._use_skill()

    # Verify initial target took 30 damage (100 - 30 = 70)
    assert math.isclose(enemy1.hp, 70.0)

    # 1st bounce (22.5 damage, 100 - 22.5 = 77.5)
    assert math.isclose(enemy2.hp, 77.5)

    # 2nd bounce (16.875 damage, 100 - 16.875 = 83.125)
    assert math.isclose(enemy3.hp, 83.125)

    # 3rd bounce (12.65625 damage, 100 - 12.65625 = 87.34375)
    assert math.isclose(enemy4.hp, 87.34375)

    # Should not bounce to 4th enemy
    assert math.isclose(enemy5.hp, 100.0)

    # Verify skill timer was reset
    assert attacker.skill_timer == 5.0
