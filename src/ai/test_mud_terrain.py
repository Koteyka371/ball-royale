from ai.action import Action
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

def test_mud_slowdown():
    ball = MockBall("tank")
    world = MockWorld()
    action = Action(ball, world)
    action.execute("idle", 0.1)
    assert ball.speed == 50.0

    ball_swamp = MockBall("swamp_monster")
    action_swamp = Action(ball_swamp, world)
    action_swamp.execute("idle", 0.1)
    assert ball_swamp.speed == 100.0

    ball_water = MockBall("elementalist")
    action_water = Action(ball_water, world)
    action_water.execute("idle", 0.1)
    assert ball_water.speed == 100.0

    # test not dirt/sand
    world.arena.terrain_type = "grass"
    ball_grass = MockBall("tank")
    action_grass = Action(ball_grass, world)
    action_grass.execute("idle", 0.1)
    assert ball_grass.speed == 100.0

    # test not raining
    world.arena.terrain_type = "dirt"
    world.arena.is_raining = False
    ball_norain = MockBall("tank")
    action_norain = Action(ball_norain, world)
    action_norain.execute("idle", 0.1)
    assert ball_norain.speed == 100.0

if __name__ == "__main__":
    test_mud_slowdown()
    print("All tests passed!")
