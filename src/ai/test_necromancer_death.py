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
    assert minion.base_speed == 6.0
    assert minion.base_damage == 25.0
    assert minion.speed == 6.0
    assert minion.damage == 25.0

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

def test_enraged_minion_large_delta():
    world = MockWorld()
    minion = MockBall()
    minion.ball_type = "minion"
    minion.is_minion = True
    minion.is_enraged = True
    minion.enrage_timer = 5.0
    minion.hp = 10.0

    world.balls = [minion]

    action = Action(minion, world)
    # Applying a large delta to see if hp is properly bounded to 0
    action.execute(strategy={}, delta=10.0)

    assert minion.enrage_timer == -5.0
    assert minion.hp == 0
    assert getattr(minion, "alive", True) == False
    assert getattr(minion, "is_enraged", True) == False

def test_necromancer_redirects_fatal_damage():
    import math
    from ai.ball_types_necromancer import Necromancer
    from ai.test_action_advanced import MockWorld, MockBall

    world = MockWorld()

    necro = Necromancer(1, 0.0, 0.0)
    necro._cached_world = world

    minion1 = MockBall()
    minion1.id = 2
    minion1.x = 10.0
    minion1.y = 0.0
    minion1.minion_owner = 1
    minion1.alive = True
    minion1.hp = 10.0
    minion1.ball_type = "minion"

    minion2 = MockBall()
    minion2.id = 3
    minion2.x = 500.0
    minion2.y = 0.0
    minion2.minion_owner = 1
    minion2.alive = True
    minion2.hp = 10.0
    minion2.ball_type = "minion"

    world.balls = [necro, minion1, minion2]

    necro.hp = 10.0
    necro.take_damage(20.0)

    assert necro.hp > 0
    assert necro.alive == True
    assert minion1.alive == False
    assert minion2.alive == True
