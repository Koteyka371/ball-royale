from arena.procedural_arena import ProceduralArena

def test_arena_generation():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) > 0
    # Hazards should be generated probabilistically
    assert isinstance(arena.hazards, list)

def test_random_spawn():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    x, y = arena.get_random_spawn_point(10.0)
    assert arena.is_point_inside(x, y, 10.0)

def test_clamp_position():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    # Get a point inside
    rx, ry = arena.rooms[0].x + 50, arena.rooms[0].y + 50
    cx, cy, bounced = arena.clamp_position(rx, ry, 10.0)
    assert not bounced
    assert cx == rx and cy == ry

    # Get a point outside
    ox, oy = -100, -100
    cx, cy, bounced = arena.clamp_position(ox, oy, 10.0)
    assert bounced
    assert arena.is_point_inside(cx, cy, 10.0)

def test_hazards_damage_application():
    from ai.action import Action
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    # Ensure there's at least one hazard for the test
    arena.hazards.append({'x': 500, 'y': 500, 'radius': 20, 'damage': 10, 'type': 'lava'})
    hazard = arena.hazards[-1]

    class MockBall:
        def __init__(self):
            self.x = hazard['x']
            self.y = hazard['y']
            self.hp = 100
            self.radius = 10
            self.alive = True
            self.ball_type = "test"

    class MockWorld:
        def __init__(self, a):
            self.arena = a
            self.tick = 1

    ball = MockBall()
    world = MockWorld(arena)
    action = Action(ball, world)

    # Execution inside the hazard should reduce HP
    action.execute("idle", 1.0)
    assert ball.hp == 90.0
