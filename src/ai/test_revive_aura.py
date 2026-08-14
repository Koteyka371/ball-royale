from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.ball_type = "player"
        self.team = "players"
        self.tag_team_id = None
        self.tag_original_ball_type = None
        self.tag_original_team = None

class MockWorld:
    def __init__(self):
        self.dead_balls = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

def test_revive_aura():
    mode = GAME_MODES["tag_team"]

    world = MockWorld()
    b1 = MockBall(1, 10.0, 10.0)
    b2 = MockBall(2, 20.0, 20.0)

    b_enemy1 = MockBall(3, 100.0, 100.0)
    b_enemy1.team = "enemies"
    b_enemy2 = MockBall(4, 100.0, 100.0)
    b_enemy2.team = "enemies"

    balls = [b1, b2, b_enemy1, b_enemy2]
    mode.setup(world, balls)

    if b1.ball_type == "player":
        active = b1
        inactive = b2
    else:
        active = b2
        inactive = b1

    world.dead_balls.append(active.id)
    active.hp = 0.0
    mode.tick(world, balls, delta=0.1)

    assert getattr(active, "is_downed", False) == True


    # Move active (now downed) close to inactive (now active)
    active.x = inactive.x
    active.y = inactive.y

    # Enemy nearby
    b_enemy1.x = active.x + 50.0
    b_enemy1.y = active.y

    assert getattr(b_enemy1, "slow_timer", 0.0) == 0.0

    mode.tick(world, balls, delta=0.1)

    assert getattr(b_enemy1, "slow_timer", 0.0) >= 0.0
    print("Test passed!")

if __name__ == "__main__":
    test_revive_aura()
