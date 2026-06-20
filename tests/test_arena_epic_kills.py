from arena.arena_types import EpicKillsArena

def test_epic_kills_arena_generation():
    # Arrange
    arena_size = 2000.0
    arena = EpicKillsArena(arena_size=arena_size)

    # Act
    arena.generate()

    # Assert
    # 1 center room + 4 corner safe zones = 5 rooms
    assert len(arena.rooms) == 5, f"Expected 5 rooms, got {len(arena.rooms)}"

    # 2 corridors for each of the 4 corner rooms = 8 corridors
    assert len(arena.corridors) == 8, f"Expected 8 corridors, got {len(arena.corridors)}"

    # 1 large central lava hazard
    assert len(arena.hazards) == 1, f"Expected 1 hazard, got {len(arena.hazards)}"

    # Verify the hazard is lava and in the center
    hazard = arena.hazards[0]
    assert hazard.kind == "lava"
    assert hazard.x == arena_size / 2
    assert hazard.y == arena_size / 2
    assert hazard.radius == 100.0
    assert hazard.damage == 50.0
