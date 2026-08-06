import pytest
from unittest.mock import Mock
from ai.game_modes import HealingRainMode

def test_healing_rain():
    mode = HealingRainMode()
    world = Mock()
    world.add_event = Mock()
    world.dead_balls = []
    world.mutators = []
    world.events = []
    world.boosters = []
    world.mutators_active = False
    world.lightning_strike_timer = 0.0

    arena = Mock()
    arena.hazards = []
    arena.weather = "clear"
    arena.is_raining = False
    world.arena = arena

    pm = Mock()
    pm.data = {}
    world.profile_manager = pm

    b1 = Mock()
    b1.id = 1
    b1.x = 100.0
    b1.y = 100.0
    b1.vx = 0.0
    b1.vy = 0.0
    b1.alive = True
    b1.ball_type = "player"
    b1.hp = 50.0
    b1.max_hp = 200.0
    b1.base_speed = 200.0
    b1.speed = 200.0
    b1.traits = []
    b1.badges = []
    b1.active_perks = []
    b1.mutators = []
    b1.base_damage = 10.0
    b1.damage = 10.0
    b1.lifesteal = 0.0
    b1.cooldown_multiplier = 1.0
    b1.experience = 0.0
    b1.level = 1
    b1.hologram_clones = []

    balls = [b1]

    # Tick before storm starts (10 seconds interval)
    mode.tick(world, balls, delta=9.9)
    assert not mode.storm_active
    assert b1.hp == 50.0

    # Storm starts
    mode.tick(world, balls, delta=0.2)
    assert mode.storm_active
    world.add_event.assert_called_with("healing_rain_start", {"message": "A healing rain storm has started! Players are healed but slowed."})

    # Test heal and slow
    assert b1.hp == 50.0 + 10.0 * 0.2
    assert b1.speed == 100.0
    assert hasattr(b1, '_healing_rain_slowed')
    assert b1._healing_rain_slowed

    # tick until storm ends (duration 5s)
    mode.tick(world, balls, delta=4.9)
    assert mode.storm_active
    assert b1.hp == 52.0 + 10.0 * 4.9

    # Storm ends
    mode.tick(world, balls, delta=0.2)
    assert not mode.storm_active
    world.add_event.assert_called_with("healing_rain_end", {"message": "The healing rain has stopped."})

    # Assert speed restored
    assert b1.speed == 200.0
    assert not b1._healing_rain_slowed
