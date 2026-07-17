from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 222
        self.is_blinded = True
        self.blindness_timer = 1.0
        self.base_perception_radius = 250.0
        self.perception_radius = 50.0
        self.hp = 100
        self.alive = True
        self.team = "enemy"
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.radius = 15.0
        self.ball_type = "basic"
        self.glitch_timer = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.time = 0.0

def test_blindness_restoration():
    enemy = MockBall()
    world = MockWorld()
    world.balls = [enemy]

    action_enemy = Action(enemy, world)
    action_enemy.execute("idle", 2.0)

    print("enemy.is_blinded:", enemy.is_blinded)
    print("enemy.blindness_timer:", enemy.blindness_timer)
    print("enemy.perception_radius:", enemy.perception_radius)

if __name__ == "__main__":
    test_blindness_restoration()
