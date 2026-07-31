import pytest

class MockBall:
    def __init__(self, id, team, x=0, y=0, radius=10.0):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = 100
        self.alive = True
        self.blindness_timer = 0.0
        self.is_blinded = False
        self.perception_radius = 100.0
        self.stun_timer = 0.0
        self.is_stunned = False

class MockBooster:
    def __init__(self, x, y, kind, radius=15.0):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.active = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.events = []
        self.next_id = 100
        self.arena = type("Arena", (), {"hazards": []})()

def test_flashbang_booster_blinds_and_stuns_enemies():
    from ai.action import Action
    world = MockWorld()

    player = MockBall(1, "A", x=5, y=5)
    enemy1 = MockBall(2, "B", x=25, y=25)
    enemy2 = MockBall(3, "C", x=600, y=600) # Out of 500 range

    world.balls.extend([player, enemy1, enemy2])

    flashbang = MockBooster(5, 5, "flashbang_booster")
    world.boosters.append(flashbang)

    action = Action(player, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: [enemy1, enemy2]

    action._collect_booster(0.1)

    # Check if enemy1 is blinded (in range)
    assert enemy1.is_blinded == True
    assert enemy1.blindness_timer > 0
    assert enemy1.stun_timer > 0
    assert enemy1.is_stunned == True
    assert enemy1.perception_radius == 0.0
    assert getattr(enemy1, "base_perception_radius", 0.0) == 100.0

    # Check if enemy2 is NOT blinded (out of range)
    assert enemy2.is_blinded == False
    assert enemy2.blindness_timer == 0.0
    assert getattr(enemy2, "stun_timer", 0.0) == 0.0
    assert getattr(enemy2, "is_stunned", False) == False
    assert enemy2.perception_radius == 100.0
