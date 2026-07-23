import pytest
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': [], 'items': [], 'width': 1000, 'height': 1000})()
        self.events = []
        self.balls = []

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500
        self.y = 500
        self.speed = 100
        self.hp = 90
        self.max_hp = 100
        self.alive = True
        self.ball_type = "player"
        self.base_speed = 100
        self.pet = None

def test_pet_system_auto_loot():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    wild_pet = type('Hazard', (), {'kind': 'wild_pet', 'pet_type': 'auto_loot', 'x': 510, 'y': 510, 'radius': 20, 'active': True})()
    world.arena.hazards.append(wild_pet)

    item = type('Item', (), {'kind': 'coin', 'x': 550, 'y': 550})()
    world.arena.items.append(item)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Check if pet was tamed
    assert ball.pet == "auto_loot"
    assert wild_pet.active == False

    # Check if auto loot magnetizes the item
    assert item.x < 550
    assert item.y < 550

def test_pet_system_healer():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    wild_pet = type('Hazard', (), {'kind': 'wild_pet', 'pet_type': 'healer', 'x': 510, 'y': 510, 'radius': 20, 'active': True})()
    world.arena.hazards.append(wild_pet)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.pet == "healer"

    # Fast forward pet heal timer
    ball.pet_heal_timer = 0
    action.execute("idle", 0.1)

    assert ball.hp == 95

def test_pet_system_speed_boost():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    wild_pet = type('Hazard', (), {'kind': 'wild_pet', 'pet_type': 'speed_boost', 'x': 510, 'y': 510, 'radius': 20, 'active': True})()
    world.arena.hazards.append(wild_pet)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    assert ball.pet == "speed_boost"
    assert round(ball.speed) == 110
