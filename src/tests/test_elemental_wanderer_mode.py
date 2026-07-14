import pytest

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.weather = "clear"
        self.name = "default"

class MockWorld:
    def __init__(self):
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, ball_type="normal"):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.radius = 15.0
        self.base_damage = 10.0
        self.damage = 10.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.defense_multiplier = 1.0
        self.traits = []
        self.elemental_buff = None

def test_elemental_wanderer():
    import sys
    sys.path.insert(0, 'src')
    from ai.game_modes import ElementalWandererMode

    mode = ElementalWandererMode()
    world = MockWorld()
    balls = [MockBall(1)]

    mode.setup(world, balls)

    assert mode.npc is not None
    assert getattr(mode.npc, "current_element", None) is None

    fire_hz = next((h for h in world.arena.hazards if "fire" in h.kind), None)
    assert fire_hz is not None
    world.arena.hazards = [fire_hz]
    mode.npc.x = fire_hz.x
    mode.npc.y = fire_hz.y
    mode.npc.radius = 1.0
    fire_hz.radius = 100.0

    mode.tick(world, balls, 1.0)
    assert mode.npc.current_element == "fire"

    balls[0].x = mode.npc.x
    balls[0].y = mode.npc.y
    mode.tick(world, balls, 1.0)
    assert balls[0].elemental_buff == "fire"

    base_damage_before = getattr(balls[0], "base_damage", getattr(balls[0], "damage", 10.0))
    mode.apply_dynamic_traits(world, balls, 1.0)
    assert balls[0].damage == base_damage_before * 1.5
