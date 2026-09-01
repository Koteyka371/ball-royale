from ai.action import Action
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
        self.boundary_offsets = {"top":0,"bottom":0,"left":0,"right":0}
        self.platforms = []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = []
        self.projectiles = []
        self.tick = 0
        self.time = 0.0

class MockBall:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.ball_type = "player"
        self.hp = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.base_speed = 50.0
        self.speed = 50.0
        self.mass = 1.0
        self.base_mass = 1.0
        self.team = "blue"
        self.is_dashing = False
        self.stutter_timer = 0.0

def test_stamina_drain_trap():
    ball = MockBall(1, 100.0, 100.0)
    trap = Hazard(2, 100.0, 100.0, 30.0, "stamina_drain_trap", 0.0)
    trap.drain_rate = 50.0
    world = MockWorld(MockArena([trap]), [ball])
    action = Action(ball, world)

    action.execute("idle", 1.0)

    # Ball's stamina should be drained
    assert ball.stamina < 100.0, f"Stamina was not drained, currently {ball.stamina}"
    print(f"Stamina after trap: {ball.stamina}")

if __name__ == '__main__':
    test_stamina_drain_trap()
