import pytest
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, hp=100.0, speed=100.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100.0
        self.speed = speed
        self.alive = True
        self.entanglement_target = None
        self.entanglement_timer = 0.0
        self.radius = 10.0
        self.ball_type = "normal"

class MockBooster:
    def __init__(self, x, y, kind, radius=10.0):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = MockArena()

    def _collect_booster(self, ball, booster):
        if booster.kind == "health_pack":
            ball.hp = min(ball.max_hp, ball.hp + 20)
        elif booster.kind == "speed_booster":
            ball.speed += 15

        if booster in getattr(self, "boosters", []):
            self.boosters.remove(booster)
        elif booster in getattr(self.arena, "hazards", []):
            self.arena.hazards.remove(booster)

def test_entanglement_booster_pickup_and_buff_sharing():
    b1 = MockEntity(1, 0, 0)
    b2 = MockEntity(2, 50, 50)
    b3 = MockEntity(3, 1000, 1000) # Far away, shouldn't be picked

    world = MockWorld()
    world.balls = [b1, b2, b3]

    # Booster to link b1 and b2
    ent_booster = MockBooster(5, 5, "entanglement_booster")
    world.boosters.append(ent_booster)

    action = Action(b1, world)
    action._get_enemies = lambda: [b2, b3]
    action._get_boosters = lambda: world.boosters

    # 1. Pick up the entanglement booster
    b1.x = 4
    b1.y = 4
    action._collect_booster(0.1)

    assert b1.entanglement_target == b2
    assert b2.entanglement_target == b1
    assert b1.entanglement_timer == 10.0
    assert b2.entanglement_timer == 10.0

    # 2. b1 picks up a health pack
    b1.hp = 50.0
    b2.hp = 50.0
    hp_booster = MockBooster(4, 4, "health_pack")
    world.boosters.append(hp_booster)
    action._collect_booster(0.1)

    # b1 heals 20 (hp goes to 70), b2 should heal 10 (hp goes to 60)
    assert b1.hp == 70.0
    assert b2.hp == 60.0

    # 3. b1 picks up a speed booster
    speed_booster = MockBooster(4, 4, "speed_booster")
    world.boosters.append(speed_booster)
    action._collect_booster(0.1)

    # b1 gains 15 speed (100 -> 115), b2 gains 7.5 speed (100 -> 107.5)
    assert b1.speed == 115.0
    assert b2.speed == 107.5

    # 4. Timer expires
    action.execute("idle", 10.1)
    assert getattr(b1, "entanglement_timer", 0.0) <= 0.0
    assert getattr(b1, "entanglement_target", None) is None
