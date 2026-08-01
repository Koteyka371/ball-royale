import unittest
from ai.action import Action
from ai.test_action_advanced import MockBall, MockWorld
import math

class MockArena:
    def __init__(self):
        self.hazards = []

class MockHazard:
    def __init__(self, x, y, radius, kind):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.id = 12345
        self.active = True
        self.owner_team = "evil"

class TestBoneWallShrapnel(unittest.TestCase):
    def test_bone_wall_shrapnel(self):
        world = MockWorld()
        world.arena = MockArena()
        world.balls = []

        # Add bone wall with 5 HP
        bone_wall = MockHazard(100.0, 100.0, 40.0, "bone_wall")
        bone_wall.hp = 5.0
        world.arena.hazards.append(bone_wall)

        attacker = MockBall()
        attacker.x = 20.0
        attacker.y = 100.0
        attacker.damage = 10.0
        attacker.team = "good"
        attacker.id = 1
        world.balls.append(attacker)

        target = MockBall()
        target.x = 200.0
        target.y = 100.0
        target.id = 2
        world.balls.append(target)

        action = Action(attacker, world)

        # Fire attack through the wall
        action._attempt_damage(attacker, target)

        # Check if bone wall is destroyed
        self.assertFalse(bone_wall.active)

        # Now, simulate game tick to ensure shrapnels are spawned (in game_modes.py we will implement this for bone_walls)
        from ai.game_modes import GameMode
        mode = GameMode()
        mode.tick(world, world.balls, 0.1)

        shrapnels = [h for h in world.arena.hazards if getattr(h, 'kind', '') == 'bone_fragment']
        self.assertEqual(len(shrapnels), 6)
