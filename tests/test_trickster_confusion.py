import pytest
from ai.action import Action
import random

class MockBall:
    def __init__(self, x=50, y=50, team="red", ball_type="generic"):
        self.id = 1
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.is_decoy = False
        self.decoy_timer = 0
        self.is_confused = False
        self.confusion_timer = 0.0
        self.perception_radius = 200

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 100
    def get_nearby_entities(self, ball, radius):
        enemies = [b for b in self.balls if b != ball and b.team != ball.team]
        allies = [b for b in self.balls if b != ball and b.team == ball.team]
        return {"enemies": enemies, "allies": allies}

def test_trickster_confusion_explosion():
    # Force random to always trigger our < 0.3 condition for the test
    original_random = random.random
    random.random = lambda: 0.1

    try:
        world = MockWorld()

        # Setup trickster decoy
        decoy = MockBall(50, 50, "red", "trickster")
        decoy.is_decoy = True
        decoy.decoy_timer = 3.0
        decoy.hp = 10.0

        # Setup nearby enemy
        enemy = MockBall(60, 50, "blue", "generic")
        enemy.id = 2

        world.balls.extend([decoy, enemy])

        action = Action(decoy, world)

        # Kill decoy to trigger explosion
        decoy.hp = 0.0
        action.execute("idle", 0.1)

        assert getattr(decoy, "_decoy_exploded", False) == True
        # Enemy should take damage and become confused
        assert enemy.hp <= 70.0
        assert getattr(enemy, "is_confused", False) == True
        assert getattr(enemy, "confusion_timer", 0.0) == 3.0

    finally:
        random.random = original_random

def test_confusion_targeting_swap():
    world = MockWorld()
    confused_ball = MockBall(50, 50, "red", "generic")
    confused_ball.is_confused = True

    ally = MockBall(60, 50, "red", "generic")
    ally.id = 2

    enemy = MockBall(40, 50, "blue", "generic")
    enemy.id = 3

    world.balls.extend([confused_ball, ally, enemy])

    action = Action(confused_ball, world)

    # Normally get_enemies would return [enemy], but confused should return [ally]
    enemies_list = action._get_enemies()
    assert len(enemies_list) == 1
    assert enemies_list[0].id == ally.id

    # Normally get_allies would return [ally], but confused should return [enemy]
    allies_list = action._get_allies()
    assert len(allies_list) == 1
    assert allies_list[0].id == enemy.id
