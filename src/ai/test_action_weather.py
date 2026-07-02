from ai.action import Action
import math

class MockArena:
    def __init__(self, is_raining=False, is_foggy=False):
        self.is_raining = is_raining
        self.is_foggy = is_foggy
        self.hazards = []
        self.weather = "thunderstorm" if is_raining else "clear"
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self, is_raining=False, is_foggy=False):
        self.arena = MockArena(is_raining, is_foggy)
        self.balls = []
        self.get_nearby_entities = lambda b, r: [e for e in self.balls if e != b]

class MockEntity:
    def __init__(self, x, y, hp=100, is_stunned=False):
        self.id = id(self)
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = 100
        self.is_stunned = is_stunned
        self.stun_timer = 0.0
        self.alive = True
        self.ball_type = "enemy"
        self.BALL_TYPE = "enemy"
        self.team = 2
        self.is_invisible = False
        self.traits = []
        self.radius = 20
        self.invisible = False
        self.stealth = False
        self.stealth_timer = 0

    def take_damage(self, dmg):
        self.hp -= dmg

class MockBall(MockEntity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage = 24.0
        self.team = 1
        self.ball_type = "elementalist"
        self.BALL_TYPE = "elementalist"
        self.traits = []
        self.speed = 100
        self.base_speed = 100
        self.radius = 20
        self.active_skill = "lightning_strike"
        self.skill_timer = 0.0
        self.skill_cooldown = 1.0

def test_lightning_strike_weather():
    world = MockWorld(is_raining=True)
    ball = MockBall(0, 0)
    world.balls.append(ball)

    enemies = [
        MockEntity(100, 0, hp=100)
    ]
    world.balls.extend(enemies)

    action = Action(ball, world)
    action._spawn_skill_particles = lambda x: None

    action.execute("use_skill", 1.0)

    assert enemies[0].hp == 100 - 36
    print("Success lightning_strike")

def test_elemental_burst_weather():
    world = MockWorld(is_raining=True)
    ball = MockBall(0, 0)
    ball.active_skill = "elemental_burst"
    world.balls.append(ball)

    enemies = [
        MockEntity(100, 0, hp=100),
        MockEntity(150, 0, hp=100)
    ]
    world.balls.extend(enemies)

    action = Action(ball, world)
    action.execute("use_skill", 1.0)

    assert enemies[0].hp == 100 - 30
    assert enemies[1].hp == 100 - 15
    print("Success elemental_burst")

if __name__ == "__main__":
    test_lightning_strike_weather()
    test_elemental_burst_weather()
