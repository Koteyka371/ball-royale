import unittest
from ai.action import Action
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.ball_type = "necromancer"
        self.skill = "bone_wall"
        self.skill_timer = 0
        self.vx = 0
        self.vy = 0
        self.damage = 10
        self.state_history = []
        self.suspended_projectiles = []
        self.last_teleport_tick = -100

class MockArena:
    def __init__(self):
        self.hazards = []

    def clamp_position(self, x, y, r):
        return x, y, False

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.next_id = 1000

    def get_nearby_entities(self, ball, radius):
        return {'enemies': [], 'boosters': []}

class TestBoneWall(unittest.TestCase):
    def test_bone_wall(self):
        ball = MockBall(1, 0, 0, "team1")
        ball.skill_timer = 0
        world = MockWorld()
        world.balls.append(ball)

        enemy = MockBall(2, 50, 0, "team2")
        enemy.ball_type = "basic"
        world.balls.append(enemy)

        action = Action(ball, world)

        # Call use skill to spawn bone_wall
        action.execute("idle", 0.1)

        # Check if bone_wall hazard was spawned
        bone_walls = [h for h in world.arena.hazards if getattr(h, "kind", "") == "bone_wall"]
        self.assertEqual(len(bone_walls), 1)

if __name__ == '__main__':
    unittest.main()
