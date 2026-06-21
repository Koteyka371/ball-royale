class_name ArenaTypes
extends RefCounted

class MetaEvolutionArena extends ProceduralArena:
	func generate():
		rooms.clear()
		corridors.clear()
		hazards.clear()
		var w = self.width
		var h = self.height
		var cx = w / 2.0
		var cy = h / 2.0

		# Center Room
		rooms.append(ProceduralArena.Room.new(cx - 200, cy - 200, 400, 400))
		# Top Room
		rooms.append(ProceduralArena.Room.new(cx - 150, cy - 700, 300, 300))
		# Bottom Left
		rooms.append(ProceduralArena.Room.new(cx - 700, cy + 100, 300, 300))
		# Bottom Right
		rooms.append(ProceduralArena.Room.new(cx + 400, cy + 100, 300, 300))

		# Corridors
		corridors.append(ProceduralArena.Corridor.new(cx - 50, cy - 400, 100, 200))
		corridors.append(ProceduralArena.Corridor.new(cx - 400, cy + 150, 200, 100))
		corridors.append(ProceduralArena.Corridor.new(cx + 200, cy + 150, 200, 100))

		# Hazards
		hazards.append(ProceduralArena.Hazard.new(0, cx, cy, 30.0, "lava", 10.0))
		hazards.append(ProceduralArena.Hazard.new(1, cx - 550, cy + 250, 80.0, "lava", 40.0))
		hazards.append(ProceduralArena.Hazard.new(2, cx + 550, cy + 250, 40.0, "spikes", 30.0))
		hazards.append(ProceduralArena.Hazard.new(3, cx + 500, cy + 180, 20.0, "spikes", 30.0))
		hazards.append(ProceduralArena.Hazard.new(4, cx + 600, cy + 320, 20.0, "spikes", 30.0))


class BodyBlockArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w := float(width)
        var h := float(height)
        var cx := w / 2.0
        var cy := h / 2.0

        # A central room where the main engagement happens
        rooms.append(ProceduralArena.Room.new(cx - 400, cy - 200, 800, 400))

        # Two smaller rooms representing "ally base" and "enemy spawn"
        rooms.append(ProceduralArena.Room.new(cx - 700, cy - 100, 200, 200)) # Left ally base
        rooms.append(ProceduralArena.Room.new(cx + 500, cy - 100, 200, 200)) # Right enemy base

        # Narrow choke point corridors connecting the bases to the center room to force body blocking
        corridors.append(ProceduralArena.Corridor.new(cx - 500, cy - 50, 100, 100))
        corridors.append(ProceduralArena.Corridor.new(cx + 400, cy - 50, 100, 100))

        # A central hazard to force players into tighter chokes
        var h0 = ProceduralArena.Hazard.new()
        h0.id = 0
        h0.x = cx
        h0.y = cy
        h0.radius = 50.0
        h0.kind = "lava"
        h0.damage = 25.0
        hazards.append(h0)

const ARENAS = [
	"flee",
	"body_block",
	"meta_evolution",
    "swarm_intelligence",
    "avoid_trap",
    "kite",
    "procedural",
    "cross",
    "ring",
    "four_rooms",
    "grid",
    "labyrinth",
    "hazard_pit",
    "duel",
    "long_corridor",
    "zigzag",
    "fortress",
    "split",
    "flank",
    "group_attack",
    "choke_point",
    "use_shield",
    "retreat_to_ally",
    "buff_ally",
    "aggressive_chase",
    "comebacks",
    "circle_strafe",
    "epic_kills",
    "reposition",
    "ball_relationships",
    "clutch_plays",
    "collect_booster",
    "finals_1v1",
    "team_wipes",
    "ambush"
]
