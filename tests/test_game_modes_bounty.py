import unittest
from ai.game_modes import GameMode, BountyHuntMode, ZombieInfectionMode, VampireRoyaleMode, VIPDefenseMode

class MockPM:
    def __init__(self):
        self.points = 0
    def add_skill_points(self, points):
        self.points += points

class MockWorld:
    def __init__(self):
        self.profile_manager = MockPM()
    def add_event(self, t, d):
        pass

class MockBall:
    def __init__(self, id, kill_bounty):
        self.id = id
        self.kill_bounty = kill_bounty

class TestGameModesBounty(unittest.TestCase):
    def test_bounty_hunt_mode_reward(self):
        gm = BountyHuntMode()
        world = MockWorld()
        ball = MockBall("b1", 2)
        killer = MockBall("k1", 0)
        gm.on_ball_died(world, ball, killer)
        self.assertEqual(world.profile_manager.points, 120)  # 30 * 2 * 2.0 = 120

    def test_zombie_infection_mode_reward(self):
        gm = ZombieInfectionMode()
        world = MockWorld()
        ball = MockBall("b1", 2)
        killer = MockBall("k1", 0)
        gm.on_ball_died(world, ball, killer)
        self.assertEqual(world.profile_manager.points, 10)  # 5 * 2 * 1.0 = 10

    def test_vampire_royale_mode_reward(self):
        gm = VampireRoyaleMode()
        world = MockWorld()
        ball = MockBall("b1", 2)
        killer = MockBall("k1", 0)
        gm.on_ball_died(world, ball, killer)
        self.assertEqual(world.profile_manager.points, 45)  # 15 * 2 * 1.5 = 45

    def test_vip_defense_mode_reward(self):
        gm = VIPDefenseMode()
        world = MockWorld()
        ball = MockBall("b1", 2)
        killer = MockBall("k1", 0)
        gm.on_ball_died(world, ball, killer)
        self.assertEqual(world.profile_manager.points, 50)  # 25 * 2 * 1.0 = 50
