from arena.procedural_arena import ProceduralArena

def test_arena_generation():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    assert len(arena.rooms) == 3
    assert len(arena.corridors) > 0

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

def test_hazard_generation():
    arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
    assert len(arena.hazards) >= arena.num_rooms * 2
    for hazard in arena.hazards:
        assert hazard.kind in ["tornado_warning", "spikes", "lava", "fake_booster", "decoy_item", "breakable_wall", "link_booster", "stamina_booster", "silence_booster", "freeze_booster", "poison_cloud", "proximity_trap", "explosive_barrel", "healing_spring", "trap", "spinning_laser", "laser_wall", "meteor", "conveyor_belt", "gravity_well", "reverse_gravity", "repulsion_field", "black_hole", "portal", "teleporter", "one_way_teleporter", "swap_portal", "placeable_trap_item", "portal_gun_item", "flare", "crater", "bumper", "tornado", "lightning_storm", "hidden_trap", "hidden_mine", "lightning_strike", "switch", "magnet", "temporal_rift", "fire_zone", "quicksand", "sinkhole", "massive_sinkhole", "damage_link", "weather_booster", "magnet_booster", "material_magnet_booster", "fire_ring", "wormhole", "clone_booster", "stealth_zone", "invert_booster", "stamina_drain_zone", "tether_trap", "reverse_gravity_booster", "anchor_booster", "anomaly_zone", "slip_zone", "tall_grass", "loadout_fragment", "vortex", "frictionless_zone", "singularity", "quantum_teleporter", "cursed_booster"]
        assert hazard.radius > 0
        assert hazard.damage > 0 or hazard.kind in ["healing_spring", "placeable_trap_item", "portal_gun_item", "decoy_item", "breakable_wall", "portal", "teleporter", "one_way_teleporter", "swap_portal", "flare", "crater", "bumper", "temporal_rift", "link_booster", "stamina_booster", "silence_booster", "freeze_booster", "drone_item", "stealth_drone_item", "shadow_booster", "switch", "magnet", "temporal_rift", "quicksand", "sinkhole", "massive_sinkhole", "damage_link", "weather_booster", "magnet_booster", "material_magnet_booster", "fire_ring", "wormhole", "clone_booster", "stealth_zone", "invert_booster", "stamina_drain_zone", "tether_trap", "reverse_gravity_booster", "anchor_booster", "anomaly_zone", "slip_zone", "tall_grass", "loadout_fragment", "vortex", "frictionless_zone", "singularity", "quantum_teleporter", "cursed_booster"]
        assert arena.is_point_inside(hazard.x, hazard.y, 0)

def test_siege_arena():
    from arena.arena_types import SiegeArena
    arena = SiegeArena(arena_size=2000.0)
    arena.generate()
    assert len(arena.rooms) == 2
    assert len(arena.corridors) == 2

    hazards_types = [h.kind for h in arena.hazards]
    assert "healing_spring" in hazards_types
    assert "bumper" in hazards_types
