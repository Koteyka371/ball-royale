extends GameMode

const BALL_TYPES_LIST = [
	"necromancer", "warrior", "tank", "assassin", "mirage",
	"nemesis_bomber", "paladin", "sniper", "medic", "rogue",
	"elementalist", "shuffler"
]

var artifact = null
var holder_id = null
var artifact_timer = 0.0

func _init():
	name = "Chaos Artifact"
	description = "An artifact spawns that gives a massive power boost to whoever holds it, but completely randomizes their abilities and ball type every 10 seconds."

func setup(world, balls):
	super.setup(world, balls)
	artifact = null
	holder_id = null
	artifact_timer = 0.0

func tick(world, balls, delta: float = 0.016):
	super.tick(world, balls, delta)

	var arena_w = 800.0
	var arena_h = 600.0
	if world != null and world.get("arena") != null:
		arena_w = world.arena.get("width") if world.arena.get("width") != null else 800.0
		arena_h = world.arena.get("height") if world.arena.get("height") != null else 600.0

	# Spawn artifact if it doesn't exist
	if artifact == null:
		artifact = {
			"x": randf_range(50, arena_w - 50),
			"y": randf_range(50, arena_h - 50),
			"radius": 15.0
		}
		if world != null and world.has_method("add_event"):
			world.add_event("chaos_artifact_spawned", {"x": artifact.x, "y": artifact.y})
		holder_id = null
		artifact_timer = 0.0

	var alive_balls = []
	for b in balls:
		var is_alive = false
		if typeof(b) == TYPE_DICTIONARY:
			is_alive = b.get("alive", false)
		else:
			is_alive = b.get("alive") if b.get("alive") != null else false
		if is_alive:
			alive_balls.append(b)

	# Check if holder died
	if holder_id != null:
		var holder = null
		for b in balls:
			var bid = null
			if typeof(b) == TYPE_DICTIONARY:
				bid = b.get("id")
			else:
				bid = b.get("id")
			if bid == holder_id:
				holder = b
				break

		var holder_alive = false
		if holder != null:
			if typeof(holder) == TYPE_DICTIONARY:
				holder_alive = holder.get("alive", false)
			else:
				holder_alive = holder.get("alive") if holder.get("alive") != null else false

		if not holder_alive:
			# Drop artifact
			holder_id = null
			artifact_timer = 0.0
			if holder != null:
				var hx = 0.0
				var hy = 0.0
				if typeof(holder) == TYPE_DICTIONARY:
					hx = holder.get("x", artifact.x)
					hy = holder.get("y", artifact.y)
				else:
					hx = holder.get("x") if holder.get("x") != null else artifact.x
					hy = holder.get("y") if holder.get("y") != null else artifact.y
				artifact.x = hx
				artifact.y = hy
			if world != null and world.has_method("add_event"):
				world.add_event("chaos_artifact_dropped", {"x": artifact.x, "y": artifact.y})

	# If no holder, check collisions
	if holder_id == null:
		for b in alive_balls:
			var bx = 0.0
			var by = 0.0
			var br = 10.0
			var bid = null

			if typeof(b) == TYPE_DICTIONARY:
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
				br = b.get("radius", 10.0)
				bid = b.get("id")
			else:
				bx = b.get("x") if b.get("x") != null else 0.0
				by = b.get("y") if b.get("y") != null else 0.0
				br = b.get("radius") if b.get("radius") != null else 10.0
				bid = b.get("id")

			var dx = bx - artifact.x
			var dy = by - artifact.y
			var dist = sqrt(dx * dx + dy * dy)

			if dist < br + artifact.radius:
				holder_id = bid
				artifact_timer = 0.0
				if world != null and world.has_method("add_event"):
					world.add_event("chaos_artifact_picked_up", {"holder_id": holder_id})
				break

	# If there is a holder, apply effects
	if holder_id != null:
		var holder = null
		for b in alive_balls:
			var bid = null
			if typeof(b) == TYPE_DICTIONARY:
				bid = b.get("id")
			else:
				bid = b.get("id")
			if bid == holder_id:
				holder = b
				break

		if holder != null:
			var hx = 0.0
			var hy = 0.0
			var base_speed = 100.0
			var base_damage = 10.0
			var cosmetics = []

			if typeof(holder) == TYPE_DICTIONARY:
				hx = holder.get("x", artifact.x)
				hy = holder.get("y", artifact.y)
				base_speed = holder.get("base_speed", 100.0)
				base_damage = holder.get("base_damage", 10.0)
				cosmetics = holder.get("cosmetics", [])

				artifact.x = hx
				artifact.y = hy

				holder["speed"] = base_speed * 2.0
				holder["damage"] = base_damage * 3.0

				if not "chaos_aura" in cosmetics:
					cosmetics.append("chaos_aura")
					holder["cosmetics"] = cosmetics
			else:
				hx = holder.get("x") if holder.get("x") != null else artifact.x
				hy = holder.get("y") if holder.get("y") != null else artifact.y
				base_speed = holder.get("base_speed") if holder.get("base_speed") != null else 100.0
				base_damage = holder.get("base_damage") if holder.get("base_damage") != null else 10.0
				var c = holder.get("cosmetics")
				if c != null:
					cosmetics = c

				artifact.x = hx
				artifact.y = hy

				if holder.has_method("set"):
					holder.set("speed", base_speed * 2.0)
					holder.set("damage", base_damage * 3.0)

					if not "chaos_aura" in cosmetics:
						cosmetics.append("chaos_aura")
						holder.set("cosmetics", cosmetics)

			artifact_timer += delta
			if artifact_timer >= 10.0:
				artifact_timer -= 10.0

				var new_type = BALL_TYPES_LIST[randi() % BALL_TYPES_LIST.size()]

				if typeof(holder) == TYPE_DICTIONARY:
					holder["ball_type"] = new_type
				else:
					if holder.has_method("set"):
						holder.set("ball_type", new_type)

				if world != null and world.has_method("add_event"):
					world.add_event("chaos_artifact_randomized", {"holder_id": holder_id, "new_type": new_type})
