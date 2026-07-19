import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from ai.action import Action

class MockArena:
    def __init__(self, is_dark=False):
        self.is_night = is_dark
        self.is_eclipse = False
        self.is_solar_eclipse = False
        self.is_lunar_eclipse = False
        self.width = 1000.0
        self.height = 1000.0
        self.safe_zone_center = (500, 500)
        self.safe_zone_radius = 500

class MockGameMode:
    def __init__(self, is_blackout=False):
        self.is_blackout = is_blackout

class MockBall:
    def __init__(self, is_enemy=False):
        self.id = 1 if not is_enemy else 2
        self.ball_type = "solar_bot" if not is_enemy else "enemy"
        self.team = "team1" if not is_enemy else "team2"
        self.x = 0
        self.y = 0
        self.hp = 50
        self.max_hp = 100
        self.stamina = 50
        self.max_stamina = 100
        self.base_speed = 100
        self.speed = 100
        self.base_damage = 20
        self.damage = 20
        self.skill = "solar_flare"
        self.skill_timer = 0
        self.alive = True
        self.on_fire = False
        self.burning_timer = 0

    def take_damage(self, dmg):
        self.hp -= dmg

class MockWorld:
    def __init__(self, is_dark=False):
        self.arena = MockArena(is_dark)
        self.game_mode = MockGameMode(False)
        self.balls = []
        self.flare_light_timer = 0.0

    def get_nearby_entities(self, x, y, radius):
        return {"enemies": [b for b in self.balls if b.id != 1], "allies": [], "hazards": []}

    def add_event(self, name, data):
        pass

def test_solar_bot_light_regen():
    world = MockWorld(is_dark=False)
    bot = MockBall()
    world.balls = [bot]

    action = Action(bot, world)
    action.execute("idle", 1.0)

    # Check HP and stamina regen (base 50)
    assert bot.hp == 55.0  # 50 + 5*1
    assert bot.stamina == 100.0  # 50 + 20*1

    # Speed and damage shouldn't be debuffed
    assert bot.speed == 100
    assert bot.damage >= 20

def test_solar_bot_dark_debuff():
    world = MockWorld(is_dark=True)
    bot = MockBall()
    world.balls = [bot]

    action = Action(bot, world)
    action.execute("idle", 1.0)

    # Check debuff applied
    assert bot.speed == 50.0  # 100 * 0.5
    assert bot.damage == 10.0 # 20 * 0.5

def test_solar_bot_solar_flare_skill():
    world = MockWorld(is_dark=True)
    bot = MockBall()
    bot.skill_timer = 0.0
    bot.skill = "solar_flare"

    enemy = MockBall(is_enemy=True)
    enemy.x = 10
    enemy.y = 10
    world.balls = [bot, enemy]

    action = Action(bot, world)
    # Ensure skill branch runs
    action._get_enemies_internal = lambda: [enemy]
    action._get_enemies = lambda: [enemy]
    action._use_skill()

    # Flare should set flare_light_timer
    assert world.flare_light_timer == 3.0

    # Enemy should take burn damage
    assert enemy.hp == 20.0 # 50 - 30
    assert enemy.on_fire == True
    assert enemy.burning_timer == 3.0

def test_solar_bot_light_from_flare():
    world = MockWorld(is_dark=True)
    world.flare_light_timer = 3.0
    bot = MockBall()
    world.balls = [bot]

    action = Action(bot, world)
    action.execute("idle", 1.0)

    # Because flare is active, bot should get regen instead of debuff
    assert bot.hp == 55.0
    assert bot.stamina == 100.0
    assert bot.speed == 100  # No debuff
