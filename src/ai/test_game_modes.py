import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from ai.game_modes import (
    BattleRoyaleMode, TeamDeathmatchMode, ZombieInfectionMode,
    BossFightMode, VIPDefenseMode, SurvivalMode, MemoryTrapsMode
)

class MockBall:
    def __init__(self, id, ball_type="warrior", alive=True):
        self.x = 0.0
        self.y = 0.0
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    balls = [MockBall(1), MockBall(2), MockBall(3)]

    mode.setup(world, balls)
    assert balls[0].team == "Boss"
    assert balls[0].max_hp == 1000 # 100 * 10
    assert balls[0].damage in (20, 30.0) # 10 * 2 or updated scaling
    assert balls[1].team == "Hunters"
    assert balls[2].team == "Hunters"

    assert mode.check_winner(world, balls) is None

    balls[0].alive = False
    assert mode.check_winner(world, balls) == "Hunters"

def test_vip_defense_mode():
    mode = VIPDefenseMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()

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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
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
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)

    assert len(balls) == 2
    payload = mode.payload
    assert getattr(payload, "ball_type") == "payload"
    assert getattr(payload, "is_invulnerable", False) is True
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

    # Time runs out
    payload.x = 100.0
    payload.y = 500.0
    mode.timer = 0.0
    assert mode.check_winner(world, balls) == "Attackers"

def test_pitch_black_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["pitch_black"]

    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    # Mock arena to check if is_night gets set
    world.arena = type('MockArena', (), {'is_night': False})()

    b1 = MockBall(1, "warrior")
    b1.perception_radius = 250.0
    b2 = MockBall(2, "scout")
    b2.perception_radius = 350.0

    balls = [b1, b2]

    mode.setup(world, balls)

    assert getattr(world.arena, "is_night", False) == True
    assert b1.perception_radius == 250.0
    assert b2.perception_radius == 350.0

    # Tick should keep it at base
    b1.perception_radius = 100.0  # Try changing it
    mode.tick(world, balls, delta=0.016)
    assert b1.perception_radius == 250.0
    assert b2.perception_radius == 350.0


def test_shifting_maze_setup():
    from ai.game_modes import ShiftingMazeMode
    mode = ShiftingMazeMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000})())

    balls = [MockBall(1), MockBall(2)]
    mode.setup(world, balls)

    assert len(mode.walls) > 0
    assert mode.maze_scale == 1.0

def test_shifting_maze_tick_damage():
    from ai.game_modes import ShiftingMazeMode
    mode = ShiftingMazeMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000})())

    # We will need to set up the ball so its take_damage works
    ball = MockBall(1)
    ball.x = 50.0
    ball.y = 50.0
    ball.radius = 20.0
    # Override take_damage for mock
    def take_damage(amt, src):
        ball.hp -= amt
        if ball.hp <= 0: ball.alive = False
    ball.take_damage = take_damage

    balls = [ball]
    mode.setup(world, balls)

    # Override walls to explicitly be on the ball
    mode.walls = [{
        "x": 40.0,
        "y": 40.0,
        "width": 100.0,
        "height": 100.0,
        "dx": 0.0,
        "dy": 0.0
    }]

    initial_hp = balls[0].hp
    mode.tick(world, balls, 1.0) # Tick 1 second

    assert balls[0].hp < initial_hp
    assert balls[0].hp == initial_hp - mode.wall_damage_per_second


def test_gravity_well_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["gravity_well"]
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    world.arena = type('MockArena', (), {'width': 2000.0, 'height': 2000.0, 'hazards': []})()
    balls = [MockBall("teamA")]

    mode.setup(world, balls)

    assert hasattr(world.arena, "hazards")
    assert len(world.arena.hazards) == 0

    mode.tick(world, balls, delta=5.1)

    assert len(world.arena.hazards) == 1
    assert world.arena.hazards[0].kind == "gravity_well"
    assert world.arena.hazards[0].damage > 0.0


def test_supernova_mode():
    from ai.game_modes import SupernovaMode

    class MockBall:
        def __init__(self, x, y, hp=100):
            self.x = x
            self.y = y
            self.hp = hp
            self.alive = True
            self.ball_type = "player"
            self.team = "team1"
            self.vx = 0.0
            self.vy = 0.0
            self.speed = 100
            self.damage = 10

    class MockArena:
        def __init__(self):
            self.width = 1000.0
            self.height = 1000.0

    class MockWorld:
        def __init__(self):
            self.dead_balls = []
            self.arena = MockArena()

    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()

    # Ball close to center (500, 500)
    b1 = MockBall(500.0, 510.0, 100)
    # Ball far from center
    b2 = MockBall(100.0, 100.0, 100)

    balls = [b1, b2]

    mode = SupernovaMode()

    # Tick before explosion
    mode.tick(world, balls, delta=1.0)

    # b1 should have taken more damage than b2
    assert b1.hp < b2.hp, f"b1 hp ({b1.hp}) should be lower than b2 hp ({b2.hp}) due to heat damage"

    # Trigger explosion
    mode.explosion_timer = 20.0
    mode.tick(world, balls, delta=1.0)

    assert mode.supernova_exploded == True

    # Check knockback on survivor
    assert b1.vy != 0 or b1.vx != 0, "b1 should have received knockback velocity"
    assert b2.vx < 0 or b2.vy < 0, "b2 should have received knockback velocity towards top-left"

def test_day_night_mode():
    from ai.game_modes import DayNightMode
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'is_night': False})()

    mode = DayNightMode()
    mode.setup(world, [])
    assert world.arena.is_night == False

    # Tick past phase duration
    mode.tick(world, [], delta=11.0)
    assert world.arena.is_night == True

    # Tick again past phase duration
    mode.tick(world, [], delta=11.0)
    assert world.arena.is_night == False

def test_zero_gravity_mode():
    from ai.game_modes import ZeroGravityMode
    mode = ZeroGravityMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)

    assert mode.name == "Zero Gravity"

def test_zero_gravity_mode():
    from ai.game_modes import ZeroGravityMode
    mode = ZeroGravityMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    balls = [MockBall(1, "warrior"), MockBall(2, "scout")]

    mode.setup(world, balls)

    assert mode.name == "Zero Gravity"

def test_pinball_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get("pinball")
    assert mode is not None
    assert mode.name == "Pinball Mode"

    class PinballMockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []

    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    world.arena = PinballMockArena()
    balls = [MockBall(1, 100, 100), MockBall(2, 200, 200)]
    mode.setup(world, balls)

    assert hasattr(world.arena, "hazards")
    assert len(world.arena.hazards) >= 20
    assert any(h.kind == "bumper" for h in world.arena.hazards)


def test_dynamic_hazards_mode():
    from ai.game_modes import DynamicHazardsMode
    mode = DynamicHazardsMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})())

    mode.setup(world, [])

    # Simulate time passing to trigger spawn
    for _ in range(200):  # 200 * 0.016 > 3.0 seconds
        mode.tick(world, [], 0.016)

    assert len(world.arena.hazards) > 0
    h = world.arena.hazards[0]
    assert hasattr(h, 'vx')
    assert hasattr(h, 'vy')

    # Simulate more time to test movement and survival
    initial_x = h.x
    for _ in range(10):
        mode.tick(world, [], 0.016)

    # Assert hazard moved
    assert world.arena.hazards[0].x != initial_x

    # Test out of bounds removal
    h.x = 2000 # Way out of bounds
    mode.tick(world, [], 0.016)
    assert len(world.arena.hazards) == 0

def test_floor_is_lava_mode():
    from ai.game_modes import FloorIsLavaMode
    mode = FloorIsLavaMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})())

    ball = MockBall(1)
    ball.x = 900
    ball.y = 900
    ball.hp = 100
    ball.radius = 15.0

    mode.setup(world, [ball])
    assert len(mode.platforms) > 0
    assert mode.lava_radius == 1000.0

    mode.lava_radius = 500.0 # Force lava to shrink
    mode.tick(world, [ball], delta=1.0)

    # Ball is outside lava_radius (dist to center is ~565, lava_radius is 485), and outside center platform, so it takes damage
    assert ball.hp < 100





def test_cursed_buff_zone_mode():
    from ai.game_modes import CursedBuffZoneMode
    mode = CursedBuffZoneMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})())

    mode.setup(world, [])
    assert len(world.arena.hazards) == 3
    for h in world.arena.hazards:
        assert h.kind == "cursed_buff_zone"

    zone = world.arena.hazards[0]
    zone.x = 500
    zone.y = 500
    zone.radius = 150

    b1 = MockBall(1)
    b1.x = 500
    b1.y = 500 # Inside
    b1.hp = 100
    b1.max_hp = 100
    b1.speed = 100
    b1.base_speed = 100
    b1.damage = 10
    b1.base_damage = 10

    b2 = MockBall(2)
    b2.x = 900
    b2.y = 900 # Outside
    b2.hp = 100
    b2.max_hp = 100
    b2.speed = 100
    b2.base_speed = 100
    b2.damage = 10
    b2.base_damage = 10

    balls = [b1, b2]

    # Tick 1 second
    # Force curse type to hp_drain for deterministic testing
    zone.curse_type = "hp_drain"
    mode.tick(world, balls, delta=1.0)

    # b1 inside: gets 3x speed and 2.5x damage, loses 5% of max HP
    assert b1.speed == 300
    assert b1.damage == 25
    assert b1.hp == 95

    # b2 outside: stats remain base, no damage
    assert b2.speed == 100
    assert b2.damage == 10
    assert b2.hp == 100

    # Test inverted steering
    zone.curse_type = "inverted_steering"
    b1.hp = 100
    b1.invert_timer = 0.0
    mode.tick(world, balls, delta=1.0)
    assert b1.hp == 100 # No HP drain
    assert b1.invert_timer > 0.0


def test_meteor_shower_mode():
    from ai.game_modes import MeteorShowerMode
    mode = MeteorShowerMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})())

    mode.setup(world, [])
    assert len(world.arena.hazards) == 0

    # Tick below spawn timer
    mode.tick(world, [], delta=0.5)
    assert len(world.arena.hazards) == 0

    # Tick above spawn timer
    mode.tick(world, [], delta=0.6)
    assert len(world.arena.hazards) == 1

    hazard = world.arena.hazards[0]
    assert hazard.kind == "meteor"
    assert hazard.damage == 200.0
    assert hazard.radius == 30.0

def test_day_night_mode_indestructible_wall_cover():
    from ai.game_modes import DayNightMode
    world = type('MockWorld', (), {})()
    world.arena = type('MockArena', (), {'is_night': False, 'hazards': []})()

    hazard = type('MockHazard', (), {'kind': 'indestructible_wall', 'x': 500.0, 'y': 500.0, 'radius': 50.0})()
    world.arena.hazards.append(hazard)

    mode = DayNightMode()
    mode.setup(world, [])

    b = type('MockBall', (), {'alive': True, 'ball_type': 'vampire', 'x': 450.0, 'y': 500.0, 'hp': 100})()

    mode.active_sunlight_beams.append({'x': 550.0, 'y': 500.0, 'radius': 200.0, 'duration': 2.0})
    mode.tick(world, [b], delta=1.0)

    assert b.hp == 100, "Ball should not take damage from sunlight beam when behind indestructible wall"


def test_battle_royale_meteor_shower():
    from ai.game_modes import BattleRoyaleMode
    mode = BattleRoyaleMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()

    # 3 teams alive
    balls = [
        MockBall(1, "warrior"),
        MockBall(2, "scout"),
        MockBall(3, "mage")
    ]
    balls[0].team = "A"
    balls[1].team = "B"
    balls[2].team = "C"

    # No meteors initially
    mode.match_time = 50.0
    mode.tick(world, balls, 2.0)
    assert len(world.arena.hazards) == 0

    # Meteors spawn when 2 teams remain
    balls[2].alive = False
    mode.tick(world, balls, 2.0)
    assert len(world.arena.hazards) > 0
    assert world.arena.hazards[0].kind == "wall"

def test_bouncy_terrain_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get("bouncy_terrain")
    assert mode is not None, "BouncyTerrainMode should be registered in GAME_MODES"
    assert mode.name == "Bouncy Terrain"

    # Check that action logic is handling it properly.
    from ai.action import Action
    world = MockWorld()
    world.game_mode = mode
    world.width = 1000
    world.height = 1000
    world.arena = type('MockArena', (), {'clamp_position': lambda self, x, y, r: (x, y, False)})()
    ball = MockBall(1, "warrior")
    ball.x = 0  # To trigger bounce
    ball.y = 500
    ball.vx = -100
    ball.vy = 0
    ball.hp = 100
    ball.radius = 15.0

    action = Action(ball, world)

    # Overwrite the _clamp_position method for testing reflection
    def override_clamp():
        # Force a bounce on the left wall
        if action.ball.x <= action.ball.radius:
            action.ball.x = action.ball.radius
            return True
        return False

    action._clamp_position = override_clamp

    action.execute("idle", 0.016)

    # The new speed should be multiplied by 2.0 (200), because it's Bouncy Terrain
    # and not deal damage
    assert ball.hp == 100
    assert abs(ball.vx) > 150 # speed multiplied by 2.0 and randomized angle slightly, so abs(vx) should be significantly higher than 100

def test_battle_royale_final_boss_spawn():
    mode = BattleRoyaleMode()
    world = MockWorld()
    if not hasattr(world, "events"):
        world.events = []

    if not hasattr(world, "add_event"):
        def add_event(type, data):
            world.events.append((type, data))
        world.add_event = add_event

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    world.balls = []
    balls = [MockBall(1, "warrior")]

    mode.setup(world, balls)

    mode.tick(world, balls, delta=75.0)

    assert mode.final_boss_spawned == True

    bosses = [b for b in world.balls if getattr(b, "is_final_boss", False)]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.team == "Boss"
    assert boss.max_hp == 3000.0

    boss.hp = 0
    boss.alive = False
    boss.killer_id = 1

    balls.append(boss)

    mode.tick(world, balls, delta=1.0)

    defeated_events = [e for e in world.events if e[0] == "boss_defeated"]
    assert len(defeated_events) == 1
    assert defeated_events[0][1]["killer_id"] == 1
    assert defeated_events[0][1]["points"] == 5000

def test_invisible_decoys_mode():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES.get("invisible_decoys")
    assert mode is not None
    assert mode.name == "Invisible Decoys"

    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []

    world = MockWorld()
    world.arena = MockArena()
    world.balls = [MockBall(1, "warrior")]

    mode.setup(world, world.balls)

    # Check that decoys were spawned
    decoys = [b for b in world.balls if getattr(b, "is_decoy", False)]
    assert len(decoys) == 20

    decoy = decoys[0]
    assert decoy.invisible is True
    assert decoy.decoy_type == "explosive"
    assert decoy.team == "neutral"
