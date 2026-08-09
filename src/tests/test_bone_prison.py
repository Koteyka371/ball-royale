import pytest

def test_bone_prison_logic():
    from ai.bone_prison_trap import BonePrisonTrapMode

    class MockHazard:
        def __init__(self, id, x, y, kind):
            self.id = id
            self.x = x
            self.y = y
            self.kind = kind
            self.radius = 30.0
            self.owner_team = "A"
            self.activation_timer = 0.0
            self.prison_duration = 3.0
            self.prison_hp = 50.0

    class MockBall:
        def __init__(self, id, x, y, team):
            self.id = id
            self.x = x
            self.y = y
            self.team = team
            self.alive = True
            self.radius = 15.0
            self.speed = 100.0

    class MockArena:
        def __init__(self):
            self.hazards = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()
            self.next_id = 1000

    mode = BonePrisonTrapMode()
    world = MockWorld()

    trap = MockHazard(1, 100, 100, "bone_prison_trap")
    world.arena.hazards.append(trap)

    b = MockBall(1, 100, 100, "B")

    # Trigger trap
    mode.tick(world, [b], 0.1)

    assert len(world.arena.hazards) == 1
    prison = world.arena.hazards[0]
    assert prison.kind == "bone_prison"
    assert getattr(prison, "hp", 0) == 50.0
    assert getattr(prison, "duration", 0) == 3.0
    assert getattr(prison, "trapped_ball_id", None) == 1

    assert getattr(b, "trapped", False) == True
    assert getattr(b, "bone_prison_id", None) == prison.id

    # Tick again, b should be constrained to prison's location and speed=0
    b.x = 110
    b.y = 110
    b.speed = 50
    mode.tick(world, [b], 0.1)
    assert b.x == prison.x
    assert b.y == prison.y
    assert b.speed == 0

    # Let prison expire
    mode.tick(world, [b], 3.5)
    assert len(world.arena.hazards) == 0
    assert getattr(b, "trapped", True) == False
    assert getattr(b, "bone_prison_id", 123) == None
