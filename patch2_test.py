from ai.action import Action

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.trap_variant = "warp"
        self.duration = 10.0
        self.x = 200
        self.y = 200
        self.radius = 20
        self.damage = 0
        self.active = True
        self.id = 1

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        nx = max(radius, min(1000 - radius, x))
        ny = max(radius, min(1000 - radius, y))
        return (nx, ny, x != nx or y != ny)

class MockEventList(list):
    def append(self, event):
        super().append(event)

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 123
        self.time = 0
        self.next_id = 9999
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [], 'allies': []}

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 100.0  # moving right
        self.vy = 0.0
        self.alive = True
        self.radius = 10

def test_warp_trap():
    import math
    trap = MockHazard("trap")
    arena = MockArena([trap])
    my_ball = MockBall(1, 200, 200)
    world = MockWorld(arena, [my_ball])
    action = Action(my_ball, world)

    action.execute("none", 0.0)

    print("Teleported to:", my_ball.x, my_ball.y)
    print("Trap duration:", trap.duration)

test_warp_trap()
