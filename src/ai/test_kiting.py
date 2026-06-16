import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from ai.action import Action
from ai.ball_types_sniper import Sniper
from ai.ball_types_warrior import Warrior

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.entities = []

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [e for e in self.entities if getattr(e, "ball_type", getattr(e.__class__, "BALL_TYPE", "")) != getattr(ball, "ball_type", getattr(ball.__class__, "BALL_TYPE", "")) and e != ball],
            "allies": [e for e in self.entities if getattr(e, "ball_type", getattr(e.__class__, "BALL_TYPE", "")) == getattr(ball, "ball_type", getattr(ball.__class__, "BALL_TYPE", "")) and e != ball],
            "boosters": []
        }

    def _deal_damage(self, ball, target):
        pass


def test_sniper_kites_enemy():
    world = MockWorld()
    sniper = Sniper(1, x=500, y=500)
    enemy1 = Warrior(2, x=550, y=500)
    world.entities = [enemy1]

    action = Action(sniper, world)
    orig_x = sniper.x
    action.execute("attack", 0.1)

    assert sniper.x < orig_x, f"Expected sniper to move left, but x moved from {orig_x} to {sniper.x}"


def test_sniper_maintains_distance():
    world = MockWorld()
    sniper = Sniper(1, x=500, y=500)
    enemy1 = Warrior(2, x=635, y=500)
    world.entities = [enemy1]

    action = Action(sniper, world)
    orig_x = sniper.x
    orig_y = sniper.y
    action.execute("attack", 0.1)

    assert math.isclose(sniper.x, orig_x), f"Expected sniper to stay, but moved to {sniper.x}"
    assert math.isclose(sniper.y, orig_y), f"Expected sniper to stay, but moved to {sniper.y}"

def test_sniper_chases_far_enemy():
    world = MockWorld()
    sniper = Sniper(1, x=500, y=500)
    enemy1 = Warrior(2, x=700, y=500)
    world.entities = [enemy1]

    action = Action(sniper, world)
    orig_x = sniper.x
    action.execute("attack", 0.1)

    assert sniper.x > orig_x, f"Expected sniper to move right, but x moved from {orig_x} to {sniper.x}"


if __name__ == "__main__":
    test_sniper_kites_enemy()
    test_sniper_maintains_distance()
    test_sniper_chases_far_enemy()
    print("All kiting tests passed.")
