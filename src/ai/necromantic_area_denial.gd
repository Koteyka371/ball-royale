extends Node

class VolatilePoisonCloud:
	var x: float = 0.0
	var y: float = 0.0
	var team: String = ""
	var radius: float = 10.0
	var max_radius: float = 80.0
	var growth_rate: float = 15.0
	var timer: float = 5.0
	var kind: String = "volatile_poison_cloud"
	var damage_per_sec: float = 25.0
	var explosion_damage: float = 50.0

var name = "Necromantic Area Denial"
var description = "Skill that turns dead enemy remains into volatile poison clouds."

func tick(world: Dictionary, balls: Array, delta: float = 0.016) -> void:
	if not world.has("dead_balls"):
		world["dead_balls"] = []

	if not world.has("arena"):
		return

	if not world.arena.has("hazards"):
		world.arena["hazards"] = []

	# Find balls with the necromantic area denial skill activated
	for user in balls:
		if typeof(user) == TYPE_DICTIONARY:
			if user.get("alive", true) and user.get("skill", "") == "necromantic_denial" and user.get("skill_active", false):
				var to_remove = []
				for db in world.dead_balls:
					if db.get("team", "") != user.get("team", ""):
						var cloud = VolatilePoisonCloud.new()
						cloud.x = db.get("x", 0.0)
						cloud.y = db.get("y", 0.0)
						cloud.team = user.get("team", "")
						world.arena.hazards.append(cloud)
						to_remove.append(db)

				for db in to_remove:
					world.dead_balls.erase(db)

				user["skill_active"] = false
		elif user != null:
			# Object get method takes only 1 argument!
			var alive = true
			if user.get("alive") != null:
				alive = user.get("alive")

			var skill = ""
			if user.get("skill") != null:
				skill = user.get("skill")

			var skill_active = false
			if user.get("skill_active") != null:
				skill_active = user.get("skill_active")

			if alive and skill == "necromantic_denial" and skill_active:
				var to_remove = []
				var user_team = ""
				if user.get("team") != null:
					user_team = user.get("team")

				for db in world.dead_balls:
					var db_team = ""
					if typeof(db) == TYPE_DICTIONARY:
						db_team = db.get("team", "")
					elif db != null and db.get("team") != null:
						db_team = db.get("team")

					if db_team != user_team:
						var cloud = VolatilePoisonCloud.new()
						if typeof(db) == TYPE_DICTIONARY:
							cloud.x = db.get("x", 0.0)
							cloud.y = db.get("y", 0.0)
						elif db != null:
							if db.get("x") != null: cloud.x = db.get("x")
							if db.get("y") != null: cloud.y = db.get("y")
						cloud.team = user_team
						world.arena.hazards.append(cloud)
						to_remove.append(db)

				for db in to_remove:
					world.dead_balls.erase(db)

				user.set("skill_active", false)

	# Process existing clouds
	var active_hazards = []
	for hazard in world.arena.hazards:
		var kind = ""
		if typeof(hazard) == TYPE_DICTIONARY:
			kind = hazard.get("kind", "")
		elif hazard != null and hazard.get("kind") != null:
			kind = hazard.get("kind")

		if kind == "volatile_poison_cloud":
			var cur_radius = 10.0
			var max_rad = 80.0
			var gr = 15.0
			var timer = 5.0
			var dmg_sec = 25.0
			var exp_dmg = 50.0
			var h_team = ""
			var h_x = 0.0
			var h_y = 0.0

			if typeof(hazard) == TYPE_DICTIONARY:
				cur_radius = hazard.get("radius", 10.0)
				max_rad = hazard.get("max_radius", 80.0)
				gr = hazard.get("growth_rate", 15.0)
				timer = hazard.get("timer", 5.0)
				dmg_sec = hazard.get("damage_per_sec", 25.0)
				exp_dmg = hazard.get("explosion_damage", 50.0)
				h_team = hazard.get("team", "")
				h_x = hazard.get("x", 0.0)
				h_y = hazard.get("y", 0.0)
			elif hazard != null:
				if hazard.get("radius") != null: cur_radius = hazard.get("radius")
				if hazard.get("max_radius") != null: max_rad = hazard.get("max_radius")
				if hazard.get("growth_rate") != null: gr = hazard.get("growth_rate")
				if hazard.get("timer") != null: timer = hazard.get("timer")
				if hazard.get("damage_per_sec") != null: dmg_sec = hazard.get("damage_per_sec")
				if hazard.get("explosion_damage") != null: exp_dmg = hazard.get("explosion_damage")
				if hazard.get("team") != null: h_team = hazard.get("team")
				if hazard.get("x") != null: h_x = hazard.get("x")
				if hazard.get("y") != null: h_y = hazard.get("y")

			if cur_radius < max_rad:
				var new_rad = min(max_rad, cur_radius + gr * delta)
				if typeof(hazard) == TYPE_DICTIONARY:
					hazard["radius"] = new_rad
				else:
					hazard.set("radius", new_rad)
				cur_radius = new_rad

			for b in balls:
				if typeof(b) == TYPE_DICTIONARY:
					if b.get("alive", true) and b.get("team", "") != h_team:
						var dist = sqrt(pow(b.get("x", 0.0) - h_x, 2) + pow(b.get("y", 0.0) - h_y, 2))
						if dist <= cur_radius:
							var dmg = dmg_sec * delta
							b["hp"] = b.get("hp", 100.0) - dmg
							if b["hp"] <= 0:
								b["alive"] = false
				elif b != null:
					var alive = true
					if b.get("alive") != null: alive = b.get("alive")
					var b_team = ""
					if b.get("team") != null: b_team = b.get("team")

					if alive and b_team != h_team:
						var bx = 0.0
						if b.get("x") != null: bx = b.get("x")
						var by = 0.0
						if b.get("y") != null: by = b.get("y")

						var dist = sqrt(pow(bx - h_x, 2) + pow(by - h_y, 2))
						if dist <= cur_radius:
							var dmg = dmg_sec * delta
							if b.has_method("take_damage"):
								b.take_damage(dmg)
							else:
								var bhp = 100.0
								if b.get("hp") != null: bhp = b.get("hp")
								b.set("hp", bhp - dmg)
								if bhp - dmg <= 0:
									b.set("alive", false)

			timer -= delta
			if typeof(hazard) == TYPE_DICTIONARY:
				hazard["timer"] = timer
			else:
				hazard.set("timer", timer)

			if timer <= 0:
				for b in balls:
					if typeof(b) == TYPE_DICTIONARY:
						if b.get("alive", true) and b.get("team", "") != h_team:
							var dist = sqrt(pow(b.get("x", 0.0) - h_x, 2) + pow(b.get("y", 0.0) - h_y, 2))
							if dist <= cur_radius:
								b["hp"] = b.get("hp", 100.0) - exp_dmg
								if b["hp"] <= 0:
									b["alive"] = false
					elif b != null:
						var alive = true
						if b.get("alive") != null: alive = b.get("alive")
						var b_team = ""
						if b.get("team") != null: b_team = b.get("team")

						if alive and b_team != h_team:
							var bx = 0.0
							if b.get("x") != null: bx = b.get("x")
							var by = 0.0
							if b.get("y") != null: by = b.get("y")
							var dist = sqrt(pow(bx - h_x, 2) + pow(by - h_y, 2))
							if dist <= cur_radius:
								if b.has_method("take_damage"):
									b.take_damage(exp_dmg)
								else:
									var bhp = 100.0
									if b.get("hp") != null: bhp = b.get("hp")
									b.set("hp", bhp - exp_dmg)
									if bhp - exp_dmg <= 0:
										b.set("alive", false)

				if world.has_method("add_event"):
					world.add_event("explosion", {"x": h_x, "y": h_y, "radius": cur_radius, "damage": exp_dmg, "color": "green"})
			else:
				active_hazards.append(hazard)
		else:
			active_hazards.append(hazard)

	world.arena.hazards = active_hazards
