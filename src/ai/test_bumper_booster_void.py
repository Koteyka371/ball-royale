from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.name = 'mock_arena'
        self.weather = 'clear'
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.time = 0.0
        self.next_id = 9999
    def _deal_damage(self, hazard, target, amount):
        target.hp -= amount

class MockEntity(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.ball_type = getattr(self, 'ball_type', 'basic')
        self.vx = getattr(self, 'vx', 0.0)
        self.vy = getattr(self, 'vy', 0.0)
        self.radius = getattr(self, 'radius', 10.0)

def test_bumper_booster_immunity():
    ball = MockEntity(id=1, x=0, y=0, hp=100.0, alive=True, bumper_booster_timer=5.0)
    void_panel = MockEntity(x=0, y=0, kind="void_panel", radius=50.0, damage=0.0)

    arena = MockArena([void_panel])
    world = MockWorld(arena, [ball])

    action = Action(ball, world)
    # Using a high delta to evaluate the hazard loop
    action.execute("move", 0.1)

    assert ball.hp == 100.0

def test_void_panel_death():
    ball = MockEntity(id=1, x=0, y=0, hp=100.0, alive=True, bumper_booster_timer=0.0)
    void_panel = MockEntity(x=0, y=0, kind="void_panel", radius=50.0, damage=0.0)

    arena = MockArena([void_panel])
    world = MockWorld(arena, [ball])

    action = Action(ball, world)
    action.execute("move", 0.1)

    assert ball.hp < 0.0
