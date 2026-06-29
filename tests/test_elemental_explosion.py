import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
from arena.procedural_arena import Hazard

class MockEnemy:
    id = 2
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.damage_taken = 0
        self.burn_timer = 0
        self.poison_timer = 0
        self.alive = True
        self.ball_type = "test_enemy"

    def take_damage(self, dmg):
        self.damage_taken += dmg

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.team = 1
        self.id = 1
        self.ball_type = "test"
        self.skill_timer = 0
        self.skill_cooldown = 10

class MockArena:
    def __init__(self):
        self.hazards = []
        self.rooms = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

    def get_nearby_entities(self, entity, radius):
        return [b for b in self.balls if b != entity]

def test_elemental_explosion_lava():
    world = MockWorld()
    ball = MockBall(0, 0)
    enemy = MockEnemy(150, 0)  # Outside normal explosion radius (100) but inside secondary (200)
    world.balls = [ball, enemy]

    # Create a lava hazard near the ball
    hazard = Hazard(id=1, x=50, y=0, radius=50, kind='lava', damage=10)








    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    # Need to simulate skill cast
    ball.active_skill = "explosion"
    action._use_skill()

    # The enemy should take damage and get a burn timer because explosion radius grew
    assert enemy.damage_taken == 50.0
    assert enemy.burn_timer == 5.0

def test_elemental_explosion_poison():
    world = MockWorld()
    ball = MockBall(0, 0)
    enemy = MockEnemy(150, 0)
    world.balls = [ball, enemy]

    hazard = Hazard(id=1, x=50, y=0, radius=50, kind='lava', damage=10)

    hazard.id = 2



    hazard.kind = "poison_cloud"


    world.arena.hazards.append(hazard)

    action = Action(ball, world)

    ball.active_skill = "explosion"
    action._use_skill()

    assert enemy.damage_taken == 50.0
    assert enemy.poison_timer == 5.0

def test_no_elemental_explosion():
    world = MockWorld()
    ball = MockBall(0, 0)
    enemy = MockEnemy(150, 0)
    world.balls = [ball, enemy]

    # No hazards
    action = Action(ball, world)

    ball.active_skill = "explosion"
    action._use_skill()

    # Outside normal radius (100), shouldn't get hit
    assert enemy.damage_taken == 0.0
