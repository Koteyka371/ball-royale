import pytest
from ai.action import Action
from ai.game_modes import GameMode

class DummyBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0

        self.radius = 15.0
        self.hp = 100.0
        self.alive = True
        self.homing_missile_booster_timer = 0.0
        self.inventory = []
        self.owner_id = id
        self.ball_type = "basic"
        self.team = "A"

class DummyBooster:
    def __init__(self, x, y):
        self.kind = "homing_missile_booster"
        self.x = x
        self.y = y
        self.radius = 15.0


class DummyArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.safe_zone_x = 500
        self.safe_zone_y = 500
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.boosters = []
        self.balls = []
        self.dead_balls = []

    def _collect_booster(self, ball, booster):
        if booster in self.boosters:
            self.boosters.remove(booster)

def test_homing_missile_booster_pickup_and_fire():
    ball = DummyBall("player_1", 100, 100)
    world = DummyWorld()
    world.balls = [ball]

    booster = DummyBooster(100.1, 100.1)
    world.boosters.append(booster)
    world.arena.hazards.append(booster)


    action = Action(ball, world)

    # Pickup booster
    ball.homing_missile_booster_timer = 5.0
    action.execute("idle", 0.016)
    assert getattr(ball, "homing_missile_booster_timer", 0.0) > 0.0

    # Wait for 1 second to fire missile
    for _ in range(65):
        action.execute("idle", 0.016)
    action.execute("idle", 0.016)


    assert len(world.arena.hazards) > 0
    missile = world.arena.hazards[-1]
    assert getattr(missile, "kind", "") == "homing_missile"
    assert missile.owner_id == ball.id

def test_homing_missile_movement_and_damage():
    ball = DummyBall("player_1", 100, 100)
    enemy = DummyBall("player_2", 500, 500)
    world = DummyWorld()
    world.balls = [ball, enemy]

    # Add a missile near the enemy
    class Hazard:
        def __init__(self, id, x, y, radius, kind, damage):
            self.id = id
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.damage = damage
            self.active = True
            self.owner_id = "player_1"

    m = Hazard("m1", 490, 490, 10.0, "homing_missile", 25.0)
    world.arena.hazards.append(m)

    mode = GameMode()
    mode.tick(world, world.balls, 0.016)

    # Enemy should take damage
    assert enemy.hp < 100.0
    # Missile should be removed
    assert m not in world.arena.hazards

if __name__ == "__main__":
    pytest.main(["-v", "test_homing_missile_booster.py"])

def test_dummy_1():
    pass

def test_dummy_2():
    pass
