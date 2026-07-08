from arena.shrinking_hazards import ShrinkingHazardsArena

def test_shrinking_hazards_arena_logic():
    arena = ShrinkingHazardsArena(arena_size=1000.0)

    # Tick loop to exceed 5.0 seconds. Ensure we change the tick so update_zone logic executes.
    for tick in range(1, 301): # 300 ticks @ 0.016 = 4.8s
        arena.update_zone(tick, 0.016)

    hazards_count = len([h for h in arena.hazards if getattr(h, "kind", "") == "shrinking_zone_hazard"])
    assert hazards_count == 0

    # Trigger spawn on this tick
    arena.update_zone(302, 0.5)

    # A new hazard should be spawned
    hazards_count = len([h for h in arena.hazards if getattr(h, "kind", "") == "shrinking_zone_hazard"])
    assert hazards_count > 0

    new_hazards = [h for h in arena.hazards if getattr(h, "kind", "") == "shrinking_zone_hazard"]
    h = new_hazards[0]
    initial_radius = h.radius
    assert initial_radius > 10.0 # It grew in the same tick it was spawned

    # Tick again to trigger growth
    arena.update_zone(303, 1.0)

    assert h.radius > initial_radius
