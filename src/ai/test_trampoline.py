from ai.action import Action

class MockEntity:
    def __init__(self):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.speed_boost_timer = 0.0
        self.hazard_immunity_timer = 0.0
        self.ball_type = "basic"
        self.suspended_projectiles = []
        self.state_history = []
        self.time_rewind_timer = 0.0
        self.hp = 100

class MockHazard:
    def __init__(self, kind):
        self.id = 1
        self.x = 5.0
        self.y = 0.0
        self.radius = 20.0
        self.kind = kind
        self.damage = 0.0
        self.active = True

class MockArena:
    def __init__(self):
        self.name = 'mock_arena'
        self.weather = 'clear'
        self.hazards = [MockHazard("trampoline")]

    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.next_id = 9999
        self.hazards = []
        self.boosters = []
        self.time = 0.0
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []

def test_trampoline_collision():
    player = MockEntity()
    world = MockWorld()
    world.balls.append(player)
    action = Action(player, world)

    # Run the physics step logic to process collision
    # Delta of 0.1 means timers will decrease by 0.1 at end of tick
    action.execute("idle", 0.1)

    # Assert timers were set to 2.0 and ticked down
    assert player.speed_boost_timer >= 1.9
    assert player.hazard_immunity_timer >= 1.9

    # Assert bump distance
    # With dt 0.1, vx would be modified by friction and physics, but it should be high
    assert abs(player.vx) > 1000.0
