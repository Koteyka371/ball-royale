from arena.procedural_arena import ProceduralArena

arena = ProceduralArena(arena_size=1000.0, num_rooms=3, seed=42)
hazards = [h for h in arena.hazards if h.kind == "shrinking_zone"]
print(len(hazards))
