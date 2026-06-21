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

class PhysicsChainReactionsArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w := float(width)
        var h := float(height)
        var cx := w / 2.0
        var cy := h / 2.0

        rooms.append(ProceduralArena.Room.new(cx - 300, cy - 300, 600, 600))

        rooms.append(ProceduralArena.Room.new(cx - 700, cy - 200, 200, 400))
        rooms.append(ProceduralArena.Room.new(cx + 500, cy - 200, 200, 400))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy - 700, 400, 200))
        rooms.append(ProceduralArena.Room.new(cx - 200, cy + 500, 400, 200))

        corridors.append(ProceduralArena.Corridor.new(cx - 550, cy - 100, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx + 250, cy - 100, 300, 200))
        corridors.append(ProceduralArena.Corridor.new(cx - 100, cy - 550, 200, 300))
        corridors.append(ProceduralArena.Corridor.new(cx - 100, cy + 250, 200, 300))

        var h0 = ProceduralArena.Hazard.new()
        h0.id = 0; h0.x = cx - 150; h0.y = cy - 150; h0.radius = 50.0; h0.kind = "spikes"; h0.damage = 30.0; hazards.append(h0)
        var h1 = ProceduralArena.Hazard.new()
        h1.id = 1; h1.x = cx + 150; h1.y = cy - 150; h1.radius = 50.0; h1.kind = "spikes"; h1.damage = 30.0; hazards.append(h1)
        var h2 = ProceduralArena.Hazard.new()
        h2.id = 2; h2.x = cx - 150; h2.y = cy + 150; h2.radius = 50.0; h2.kind = "spikes"; h2.damage = 30.0; hazards.append(h2)
        var h3 = ProceduralArena.Hazard.new()
        h3.id = 3; h3.x = cx + 150; h3.y = cy + 150; h3.radius = 50.0; h3.kind = "spikes"; h3.damage = 30.0; hazards.append(h3)
        var h4 = ProceduralArena.Hazard.new()
        h4.id = 4; h4.x = cx; h4.y = cy; h4.radius = 80.0; h4.kind = "lava"; h4.damage = 20.0; hazards.append(h4)

class NeuralBallArena extends ProceduralArena:
    func generate() -> void:
        rooms.clear()
        corridors.clear()
        hazards.clear()
        var w := float(width)
        var h := float(height)
        var cx := w / 2.0
        var cy := h / 2.0

        var room_w := w * 0.1
        var room_h := h * 0.1

        rooms.append(ProceduralArena.Room.new(cx - w*0.15, cy - h*0.15, w*0.3, h*0.3))
        rooms.append(ProceduralArena.Room.new(w*0.1, h*0.1, room_w, room_h))
        rooms.append(ProceduralArena.Room.new(w*0.8, h*0.1, room_w, room_h))
        rooms.append(ProceduralArena.Room.new(w*0.1, h*0.8, room_w, room_h))
        rooms.append(ProceduralArena.Room.new(w*0.8, h*0.8, room_w, room_h))

        corridors.append(ProceduralArena.Corridor.new(w*0.15, h*0.15, w*0.25, h*0.25))
        corridors.append(ProceduralArena.Corridor.new(w*0.6, h*0.15, w*0.25, h*0.25))
        corridors.append(ProceduralArena.Corridor.new(w*0.15, h*0.6, w*0.25, h*0.25))
        corridors.append(ProceduralArena.Corridor.new(w*0.6, h*0.6, w*0.25, h*0.25))

        var h0 = ProceduralArena.Hazard.new()
        h0.id = 0
        h0.x = cx
        h0.y = cy
        h0.radius = w * 0.025
        h0.kind = "lava"
        h0.damage = 20.0
        hazards.append(h0)

const ARENAS = [
	"neural_ball",
	"emotional_contagion",
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
    "ambush",
    "physics_chain_reactions"
]
