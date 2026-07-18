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
        return {'enemies': [b for b in self.balls if b.team != ball.team], 'boosters': []}

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

        # Mock _get_enemies since it checks get_nearby_entities
        def mock_get_enemies():
            return [enemy]
        action._get_enemies = mock_get_enemies

        # Call use skill to spawn bone_wall
        action.execute("use_skill", 0.1)

        # Check if bone_wall hazard was spawned
        bone_walls = [h for h in world.arena.hazards if getattr(h, "kind", "") == "bone_wall"]
        self.assertEqual(len(bone_walls), 1)

        wall = bone_walls[0]
        # Distance between ball and enemy is 50. Wall should spawn 60 units towards enemy, meaning x=60, y=0.
        # Check if wall hp is 300
        self.assertEqual(wall.hp, 300.0)

        # Now create a projectile
        proj = MockBall(3, wall.x - 5, wall.y, "team2")
        proj.ball_type = "projectile"
        proj.damage = 50
        world.balls.append(proj)
        action2 = Action(proj, world)
        action2.execute("idle", 0.1)

        # Projectile should be dead, wall HP should be 250
        self.assertFalse(proj.alive)
        self.assertEqual(wall.hp, 250.0)

if __name__ == '__main__':
    unittest.main()
