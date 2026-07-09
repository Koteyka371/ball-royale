from ai.game_modes import GameMode
from ai.action import Action
from ai.test_action_advanced import MockBall, MockWorld

def test_necromancer_death_enrages_minions():
    world = MockWorld()
    necro = MockBall()
    necro.ball_type = "necromancer"
    necro.id = 1

    minion = MockBall()
    minion.ball_type = "minion"
    minion.minion_owner = 1
    minion.id = 2
    minion.base_speed = 2.0
    minion.base_damage = 10.0
    minion.speed = 2.0
    minion.damage = 10.0

    world.balls = [necro, minion]

    mode = GameMode()
    mode.on_ball_died(world, necro, killer=None)

    assert getattr(minion, "is_enraged", False) == True
    assert minion.enrage_timer == 5.0
    assert minion.base_speed == 4.0
    assert minion.base_damage == 15.0
    assert minion.speed == 4.0
    assert minion.damage == 15.0

def test_minion_decay_when_enraged():
    world = MockWorld()
    minion = MockBall()
    minion.ball_type = "minion"
    minion.is_minion = True
    minion.is_enraged = True
    minion.enrage_timer = 5.0
    minion.hp = 100.0

    world.balls = [minion]

    action = Action(minion, world)
    action.execute(strategy={}, delta=1.0)

    assert minion.enrage_timer == 4.0
    assert minion.hp <= 80.0

    action.execute(strategy={}, delta=4.0)
    assert minion.hp == 0
    assert getattr(minion, "alive", True) == False
    assert getattr(minion, "is_enraged", True) == False
