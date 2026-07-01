from ai.action import Action
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self):
        self.hazards = [Hazard(id=1, x=100.0, y=100.0, radius=15.0, kind="decoy_hazard", damage=0.0)]

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
    def add_event(self, event_type, event_data):
        self.events.append((event_type, event_data))

class MockBall:
    def __init__(self):
        self.x = 100.0
        self.y = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "A"
        self.ball_type = "basic"
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.radius = 10.0
        self.traits = []

def test_decoy_hazard_targeted():
    world = MockWorld()
    ball = MockBall()
    action = Action(ball, world)
    enemies = action._get_enemies()
    assert len(enemies) == 1
    assert enemies[0].kind == "decoy_hazard"

def test_decoy_hazard_explosion():
    from arena.procedural_arena import ProceduralArena
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3)
    h = Hazard(id=1, x=100.0, y=100.0, radius=15.0, kind="decoy_hazard", damage=0.0)
    h.hp = 0.0
    arena.hazards = [h]
    arena.update_zone(120, 1.0)
    clouds = [x for x in arena.hazards if getattr(x, "kind", "") == "poison_cloud"]
    assert len(clouds) == 1
    assert not getattr(h, "active", True)
