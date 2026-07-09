import pytest
from game_modes import GAME_MODES
from action import Action
import math

class MockBall:
    def __init__(self, x, y, team="red", ball_type="warrior", personality="aggressive"):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.perception_radius = 250
        self.radius = 10
        self.personality = personality
        self.attack_accuracy = 1.0
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.perception_radius = 250
        self.radius = 10
        self.personality = personality

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"allies": [], "enemies": [], "boosters": []}

def test_sniper_nest_mechanics():
    mode = GAME_MODES["sniper_nests"]
    world = MockWorld()

    # 200, 200 is center of a nest (radius 120)
    # 500, 500 is another nest (radius 150)
    b1 = MockBall(200, 200) # In nest
    b2 = MockBall(10, 10)   # Not in nest

    balls = [b1, b2]
    mode.setup(world, balls)
    mode.tick(world, balls, 0.016)

    # Check perception
    assert b1.perception_radius == 250.0 * 1.25
    assert getattr(b1, "in_sniper_nest", False) == True
    assert getattr(b1, "cosmetic", "none") == "ancient_aura"

    assert b2.perception_radius == 250.0
    assert getattr(b2, "in_sniper_nest", False) == False

    # Exit nest
    b1.x = 10
    b1.y = 10
    mode.tick(world, balls, 0.016)

    assert b1.perception_radius == 250.0
    assert getattr(b1, "in_sniper_nest", False) == False
    assert getattr(b1, "cosmetic", "none") == "none"

def test_sniper_nest_damage_bonus():
    class WorldWithDamage(MockWorld):
        def _deal_damage(self, att, tar):
            tar.hp -= att.damage

    world = WorldWithDamage()
    act = Action(1, world)

    attacker = MockBall(0, 0)
    attacker.damage = 10.0
    attacker.in_sniper_nest = True

    target = MockBall(200, 200) # Ranged distance
    act.world = world
    act._attempt_damage(attacker, target)

    # Expect 1.25x damage
    assert target.hp == 100 - (10.0 * 1.25)

    # Close range
    target2 = MockBall(15, 0) # Close range
    act._attempt_damage(attacker, target2)
    assert target2.hp == 100 - 10.0

def test_sniper_nest_targeting():
    world = MockWorld()
    act = Action(1, world)
    act.ball = MockBall(500, 500, personality="warrior") # Aggro bot

    e1 = MockBall(400, 500) # Closer, not in nest
    e2 = MockBall(100, 100) # Farther, in nest
    e2.in_sniper_nest = True

    enemies = [e1, e2]

    target = act._get_target(enemies)
    assert target == e2 # Prioritizes e2 in nest

    # Non aggro bot
    act.ball.personality = "healer"
    target = act._get_target(enemies)
    assert target == e1 # Prioritizes closer
