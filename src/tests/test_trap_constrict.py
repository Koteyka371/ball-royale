import pytest
from ai.action import Action
from arena.procedural_arena import ProceduralArena

class MockEventList(list):
    def append(self, event):
        super().append(event)

class MockArena(ProceduralArena):
    def __init__(self):
        super().__init__(arena_size=1000, num_rooms=1)
        self.hazards = []
        self.is_constricted = False
        self.constrict_timer = 0.0
        self.constrict_factor = 0.0
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = MockEventList()
        self.tick = 1
        self.time = 0

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 20
        self.hp = 100
        self.max_hp = 100
        self.alive = True

class MockHazard:
    def __init__(self, id, x, y, radius, kind, trap_variant):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.trap_variant = trap_variant
        self.duration = 5.0
        self.active = True

def test_constrict_trap_trigger():
    world = MockWorld()
    ball = MockBall(0, 500, 500)
    world.balls.append(ball)

    # Place a constrict trap near the ball
    trap = MockHazard(1, 500, 500, 30, "trap", "constrict")
    world.arena.hazards.append(trap)

    action = Action(ball, world)

    # Trigger trap (action.execute handles trap collision)
    action.execute("none", 0.016)

    # Verify trap sets arena properties
    assert world.arena.is_constricted == True
    assert world.arena.constrict_timer == 10.0
    assert trap.duration == 0.0

def test_procedural_arena_constrict_clamp():
    from arena.basic_arena import BasicArena
    arena = BasicArena(arena_size=1000)

    # Turn on constriction manually
    arena.is_constricted = True
    arena.constrict_factor = 1.0  # Max constrict

    # At constrict_factor 1.0, 40% of each side is removed,
    # meaning boundaries are from 400 to 600. So clamps to 400+R and 600-R

    res_x, res_y, bounced = arena.clamp_position(100, 100, 10)

    assert bounced == True
    assert res_x == 410.0  # 400 + 10
    assert res_y == 410.0

    res_x2, res_y2, bounced2 = arena.clamp_position(900, 900, 10)
    assert bounced2 == True
    assert res_x2 == 590.0  # 1000 - 400 - 10
    assert res_y2 == 590.0

def test_arena_constrict_timer_update():
    arena = ProceduralArena(arena_size=1000, num_rooms=1)

    arena.is_constricted = True
    arena.constrict_timer = 10.0
    arena.constrict_factor = 0.0

    # Shrinking phase
    arena.update_zone(1, 1.0)
    assert arena.constrict_timer == 9.0
    assert arena.constrict_factor == 0.5

    arena.update_zone(2, 1.0)
    assert arena.constrict_timer == 8.0
    assert arena.constrict_factor == 1.0

    # Hold phase
    arena.update_zone(3, 5.0)
    assert arena.constrict_timer == 3.0
    assert arena.constrict_factor == 1.0

    # Expand phase
    arena.update_zone(4, 1.0)
    assert arena.constrict_timer == 2.0
    assert arena.constrict_factor == 1.0

    arena.update_zone(5, 1.0)
    assert arena.constrict_timer == 1.0
    assert arena.constrict_factor == 0.5

    arena.update_zone(6, 1.0)
    assert arena.constrict_timer == 0.0
    assert arena.constrict_factor == 0.0
    assert arena.is_constricted == False
