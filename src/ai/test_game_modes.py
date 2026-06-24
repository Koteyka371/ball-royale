from ai.game_modes import (
    BattleRoyaleMode, TeamDeathmatchMode, ZombieInfectionMode,
    BossFightMode, VIPDefenseMode, SurvivalMode
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
