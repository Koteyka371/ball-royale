from ai.action import Action

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.damage = 10.0
        self.speed = 10.0
        self.reflect_shield_active = False
        self.reflect_shield_capacity = 0.0
        self.reflect_shield_layers = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.leaderboard_manager = None

    def _deal_damage(self, attacker, target):
        pass

def test_unlayered_shield():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "A")
    attacker.damage = 40.0

    target = MockBall(2, 50, 0, "B")
    target.reflect_shield_active = True
    target.reflect_shield_capacity = 75.0
    target.reflect_shield_layers = False

    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    # It absorbs all 40 damage.
    assert target.reflect_shield_capacity == 35.0

def test_unlayered_shield_breaks():
    world = MockWorld()
    attacker = MockBall(1, 0, 0, "A")
    attacker.damage = 80.0

    target = MockBall(2, 50, 0, "B")
    target.reflect_shield_active = True
    target.reflect_shield_capacity = 75.0
    target.reflect_shield_layers = False

    world.balls = [attacker, target]

    action = Action(target, world)
    action._attempt_damage(attacker, target)

    # Breaks the shield and capacity drops to 0 (and the excess damage should be processed but capacity resets to 0.0 inside the block)
    assert target.reflect_shield_active == False
    assert target.reflect_shield_capacity == 0.0

test_unlayered_shield()
test_unlayered_shield_breaks()
print("Success")
