from ai.action import Action
from ai.game_modes import SurvivalMode
from arena.procedural_arena import ProceduralArena

class MockBall:
    def __init__(self, t):
        self.ball_type = t
        self.x = 100
        self.y = 100
        self.vx = 0
        self.vy = 0
        self.speed = 100
        self.base_speed = 100
        self.radius = 10
        self.id = 1
        self.hp = 100

class MockWorld:
    def __init__(self):
        self.arena = ProceduralArena()
        self.arena.terrain_type = "dirt"
        self.arena.is_raining = True
        self.events = []

    def get_nearby_entities(self, entity, radius):
        return {'enemies': [], 'allies': [], 'items': [], 'boosters': []}

ball = MockBall("tank")
world = MockWorld()
action = Action(ball, world)
action.execute("idle", 0.1)
print(f"Tank speed: {ball.speed}")

ball_swamp = MockBall("swamp_monster")
action_swamp = Action(ball_swamp, world)
action_swamp.execute("idle", 0.1)
print(f"Swamp speed: {ball_swamp.speed}")
