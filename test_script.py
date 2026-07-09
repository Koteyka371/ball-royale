from ai.action import Action
from arena.procedural_arena import ProceduralArena

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena(1000)
        self.events = []

class MockBall:
    def __init__(self):
        self.x = 500
        self.y = 500
        self.vx = 100
        self.vy = 100
        self.hp = 100
        self.stamina = 100
        self.team = "player"
        self.ball_type = "scout"
        self.cosmetic = "none"

world = MockWorld()

world.arena.is_raining = True
world.arena.is_heatwave = False
print(world.arena.is_raining)

action = Action(1, world)
action.ball = MockBall()
action.ball.id = 1

b = action.ball

# We will just manually trigger logic instead of full action execute
is_raining = getattr(world.arena, "is_raining", False)
print("Rain is", is_raining)
