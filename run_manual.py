import sys
sys.path.append('src')

from ai.action import Action

class MockBall:
    def __init__(self):
        self.stamina = 100.0
        self.speed = 10.0
        self.x = 0.0
        self.y = 0.0
        self.alive = True

class MockArena:
    def __init__(self, weather=""):
        self.weather = weather

class MockWorld:
    def __init__(self, arena):
        self.arena = arena

ball = MockBall()
arena = MockArena(weather="heatwave")
world = MockWorld(arena=arena)

action = Action(ball, world)

# Let's mock what execute does directly
if hasattr(action.world, "arena"):
    print("Has arena")
    arena_weather = getattr(action.world.arena, "weather", "")
    print("Weather:", arena_weather)
    if arena_weather == "heatwave":
        print("Is heatwave")
        if hasattr(action.ball, "stamina"):
            print("Has stamina")
            action.ball.stamina = max(0.0, float(action.ball.stamina) - (10.0 * 1.0))

print("Expected stamina:", action.ball.stamina)
