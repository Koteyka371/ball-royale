import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from ai.game_modes import (
    BattleRoyaleMode, TeamDeathmatchMode, ZombieInfectionMode,
    BossFightMode, VIPDefenseMode, SurvivalMode, MemoryTrapsMode
)

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.id = id
        self.ball_type = ball_type
        self.alive = alive
        self.max_hp = 100
        self.hp = 100
        self.damage = 10

class MockWorld:
    pass


def test_memory_traps_mode():
    mode = MemoryTrapsMode()
    world = MockWorld()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000})())

    # Place a trap exactly at (500, 500)
    mode.setup(world, [])
    mode.traps = [{"x": 500.0, "y": 500.0, "radius": 40.0, "cooldowns": {}}]

    b1 = MockBall("b1", "warrior")
    b1.x = 500.0
    b1.y = 500.0
    b1.hp = 100.0

    b2 = MockBall("b2", "scout")
    b2.x = 100.0
    b2.y = 100.0
    b2.hp = 100.0

    balls = [b1, b2]

    mode.tick(world, balls, 0.016)

    # b1 should take 20 damage, b2 should take 0
    assert b1.hp == 80.0
    assert b2.hp == 100.0

    # Tick again immediately, b1 should not take damage due to cooldown
    mode.tick(world, balls, 0.016)
    assert b1.hp == 80.0

    # Simulate time passing > 1.0s
    mode.tick(world, balls, 1.1)

    # The tick itself processes cooldown first, removing the ID.
    # But since it processes the cooldown AND does distance check in the same loop,
    # the exact behavior depends on order. In our logic, cooldown reduces, then if deleted, it damages.
    assert b1.hp == 60.0

def test_battle_royale_mode():

    mode = BattleRoyaleMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)
    for b in balls:
        assert b.team == b.ball_type

    assert mode.check_winner(world, balls) is None

    balls[1].alive = False
    assert mode.check_winner(world, balls) == "warrior"

def test_team_deathmatch_mode():
    mode = TeamDeathmatchMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3), MockBall(4)]

    mode.setup(world, balls)
    teams = [b.team for b in balls]
    assert teams.count("Red") == 2
    assert teams.count("Blue") == 2

    assert mode.check_winner(world, balls) is None

    balls[0].alive = False
    balls[1].alive = False
    assert mode.check_winner(world, balls) == "Blue"

def test_zombie_infection_mode():
    mode = ZombieInfectionMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)
    teams = [b.team for b in balls]
    assert teams.count("Zombie") == 1
    assert teams.count("Survivor") == 2

    # Identify who is who
    _ = next(b for b in balls if b.team == "Zombie")
    survivors = [b for b in balls if b.team == "Survivor"]

    assert mode.check_winner(world, balls) is None

    survivors[0].alive = False
    survivors[1].alive = False
    assert mode.check_winner(world, balls) == "Zombies"

def test_zombie_infection_mode_resurrection():
    mode = ZombieInfectionMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)
    survivors = [b for b in balls if b.team == "Survivor"]

    # Kill one survivor
    survivors[0].alive = False

    # Tick should resurrect it as a zombie
    if hasattr(mode, 'tick'):
        mode.tick(world, balls)

    assert survivors[0].alive is True
    assert survivors[0].team == "Zombie"
    assert survivors[0].ball_type == "berserker"

    # One survivor left
    assert mode.check_winner(world, balls) is None

    # Kill the last survivor
    survivors[1].alive = False
    if hasattr(mode, 'tick'):
        mode.tick(world, balls)

    assert survivors[1].alive is True
    assert survivors[1].team == "Zombie"
    assert survivors[1].ball_type == "berserker"

    # Now everyone is a zombie, so zombies win?
    # check_winner actually checks if survivors == 0 among ALIVE balls.
    # Since we resurrected them, they are alive and team=Zombie, so survivors=0 -> Zombies win
    assert mode.check_winner(world, balls) == "Zombies"

def test_boss_fight_mode():
    mode = BossFightMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)
    assert balls[0].team == "Boss"
    assert balls[0].max_hp == 1000 # 100 * 10
    assert balls[0].damage == 20 # 10 * 2
    assert balls[1].team == "Hunters"
    assert balls[2].team == "Hunters"

    assert mode.check_winner(world, balls) is None

    balls[0].alive = False
    assert mode.check_winner(world, balls) == "Hunters"

def test_vip_defense_mode():
    mode = VIPDefenseMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3), MockBall(4)]

    mode.setup(world, balls)
    assert balls[0].team == "VIP"
    assert balls[0].ball_type == "king"
    assert balls[1].team == "Defenders"
    assert balls[2].team == "Attackers"
    assert balls[3].team == "Attackers"

    assert mode.check_winner(world, balls) is None

    balls[0].alive = False # VIP dies
    assert mode.check_winner(world, balls) == "Attackers"

def test_survival_mode():
    mode = SurvivalMode()
    world = MockWorld()
    balls = [MockBall(1), MockBall(2), MockBall(3), MockBall(4), MockBall(5), MockBall(6)]

    mode.setup(world, balls)
    teams = [b.team for b in balls]
    assert teams.count("Players") == 4
    assert teams.count("Enemies") == 2

    assert mode.check_winner(world, balls) is None

    balls[0].alive = False
    balls[1].alive = False
    balls[2].alive = False
    balls[3].alive = False
    assert mode.check_winner(world, balls) == "Enemies"


def test_vampire_royale_mode():
    from ai.game_modes import VampireRoyaleMode
    mode = VampireRoyaleMode()
    class MBall:
        def __init__(self, id, hp, btype):
            self.id = id
            self.hp = hp
            self.max_hp = 100
            self.ball_type = btype
            self.alive = True
            self.team = btype

    b1 = MBall(1, 100, "warrior")
    b2 = MBall(2, 100, "tank")
    b3 = MBall(3, 100, "sniper")

    balls = [b1, b2, b3]
    world = MockWorld()

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0) # lose 5 HP

    assert b1.hp == 95
    assert b2.hp == 95
    assert b3.hp == 95

    # 20 ticks = 100 HP loss
    for _ in range(19):
        mode.tick(world, balls, delta=1.0)

    assert b1.hp == 0
    assert not b1.alive
    assert b2.hp == 0
    assert not b2.alive
    assert b3.hp == 0
    assert not b3.alive

    # One survives
    b4 = MBall(4, 100, "warrior")
    balls = [b4]
    mode.setup(world, balls)

    winner = mode.check_winner(world, balls)
    assert winner == "warrior"

def test_domination_mode():
    from ai.game_modes import DominationMode
    mode = DominationMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout"), MockBall(3, "mage"), MockBall(4, "tank")]

    # Initialize some required stats to test the buff
    for b in balls:
        b.damage = 10.0
        b.max_hp = 100.0
        b.hp = 100.0

    mode.setup(world, balls)

    # Check teams
    assert balls[0].team == "Red"
    assert balls[1].team == "Red"
    assert balls[2].team == "Blue"
    assert balls[3].team == "Blue"

    # Check points are initialized
    assert len(mode.points) == 3
    pt = mode.points[0]

    # Move Red balls to point A
    balls[0].x, balls[0].y = pt.x, pt.y
    balls[1].x, balls[1].y = pt.x, pt.y
    # Move Blue ball away
    balls[2].x, balls[2].y = 0, 0
    balls[3].x, balls[3].y = 0, 0

    # Tick should capture the point over time
    # 10.0 per tick * 10 ticks = 100
    for _ in range(10):
        mode.tick(world, balls, delta=1.0)

    assert pt.owner == "Red"

    # Red should receive buff: +5 damage, +20 max hp
    assert balls[0].damage == 15.0
    assert balls[0].max_hp == 120.0
    assert balls[0].hp == 120.0

    # Blue should not
    assert balls[2].damage == 10.0
    assert balls[2].max_hp == 100.0
    assert balls[2].hp == 100.0


def test_bumper_balls_mode():
    from ai.game_modes import BumperBallsMode
    mode = BumperBallsMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    # Give them some initial damage
    balls[0].damage = 10.0
    balls[1].damage = 10.0

    mode.setup(world, balls)

    # Should deal 0 damage
    assert balls[0].damage == 0.0
    assert balls[1].damage == 0.0

    assert mode.check_winner(world, balls) is None

    balls[1].alive = False
    assert mode.check_winner(world, balls) == "warrior"

    # Test tick eliminates balls outside arena
    balls[0].x, balls[0].y = 500, 500 # Inside
    mode.tick(world, [balls[0]])
    assert balls[0].alive is True

    balls[0].x, balls[0].y = 1500, 1500 # Outside
    mode.tick(world, [balls[0]])
    assert balls[0].alive is False

def test_random_reroll_mutator():
    from ai.game_modes import CustomMatchMode
    mode = CustomMatchMode()
    mode.mutators = ["random_reroll"]
    world = MockWorld()
    setattr(world, "profile_manager", type("MockProfile", (), {"are_mutators_unlocked": lambda self=None: True})())

    b1 = MockBall("b1", "warrior")
    b1.base_speed = 100.0
    b1.speed = 100.0
    b1.base_damage = 10.0
    b1.damage = 10.0
    balls = [b1]

    mode.setup(world, balls)

    # Tick for 9.9 seconds, should not trigger reroll
    mode.tick(world, balls, delta=9.9)
    assert b1.ball_type == "warrior"
    assert b1.max_hp == 100.0

    # Tick 0.2 more seconds, should trigger reroll
    mode.tick(world, balls, delta=0.2)

    # Now it should be rerolled
    # The chance of both matching exactly the original is extremely low
    if b1.ball_type == "warrior" and b1.max_hp == 100.0:
        assert False, "Stats not rerolled"


def test_escort_mode():
    from ai.game_modes import EscortMode
    mode = EscortMode()
    world = MockWorld()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)

    assert len(balls) == 2
    payload = mode.payload
    assert getattr(payload, "ball_type") == "payload"
    assert balls[0].team == "Defenders"
    assert balls[1].team == "Attackers"

    # Tick payload towards goal
    mode.tick(world, balls)
    assert getattr(payload, "x") > 100.0 # Moved right

    assert mode.check_winner(world, balls) is None

    # Goal reached
    payload.x = mode.goal_x
    payload.y = mode.goal_y
    assert mode.check_winner(world, balls) == "Defenders"

    # Payload destroyed
    payload.x = 100.0
    payload.y = 500.0
    payload.hp = 0
    assert mode.check_winner(world, balls) == "Attackers"


def test_pitch_black_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["pitch_black"]

    world = MockWorld()
    ball1 = MockBall("b1", 100, 100)
    ball1.ball_type = "runner"
    ball1.perception_radius = 250.0

    mode.setup(world, [ball1])
    assert getattr(world, "is_pitch_black", False) == True
    assert getattr(ball1, "cone_of_light_active", False) == True

    mode.tick(world, [ball1], 0.1)
    assert getattr(ball1, "perception_radius", 0) == 250.0
