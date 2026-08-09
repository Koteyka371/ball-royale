extends Node

var name = "Bone Prison Trap"
var description = "Skill that drops a trap which entombs an enemy in a bone prison, disabling movement and providing a destructible shell."

func tick(world: Dictionary, balls: Array, delta: float = 0.016) -> void:
	if not world.has("arena") or not world.arena.has("hazards"):
		return

	var hazards_to_remove = []
	var new_hazards = []

	for h in world.arena.hazards:
		var kind = ""
		if typeof(h) == TYPE_DICTIONARY:
			kind = h.get("kind", "")
		elif h != null and h.get("kind") != null:
			kind = h.get("kind")

		if kind == "bone_prison":
			var duration = -1.0
			var hp = 1.0
			var trapped_id = -1
			var h_x = 0.0
			var h_y = 0.0

			if typeof(h) == TYPE_DICTIONARY:
				if h.has("duration"): duration = h.get("duration")
				hp = h.get("hp", 1.0)
				trapped_id = h.get("trapped_ball_id", -1)
				h_x = h.get("x", 0.0)
				h_y = h.get("y", 0.0)
			else:
				if h.get("duration") != null: duration = h.get("duration")
				if h.get("hp") != null: hp = h.get("hp")
				if h.get("trapped_ball_id") != null: trapped_id = h.get("trapped_ball_id")
				if h.get("x") != null: h_x = h.get("x")
				if h.get("y") != null: h_y = h.get("y")

			if duration != -1.0:
				duration -= delta
				if typeof(h) == TYPE_DICTIONARY:
					h["duration"] = duration
				else:
					h.set("duration", duration)

				if duration <= 0:
					hazards_to_remove.append(h)
					if trapped_id != -1:
						for b in balls:
							var bid = -2
							if typeof(b) == TYPE_DICTIONARY: bid = b.get("id", -2)
							elif b != null and b.get("id") != null: bid = b.get("id")
							if bid == trapped_id:
								if typeof(b) == TYPE_DICTIONARY:
									b["trapped"] = false
									b["bone_prison_id"] = -1
								else:
									b.set("trapped", false)
									b.set("bone_prison_id", -1)
								break
					continue

			if hp <= 0:
				hazards_to_remove.append(h)
				if trapped_id != -1:
					for b in balls:
						var bid = -2
						if typeof(b) == TYPE_DICTIONARY: bid = b.get("id", -2)
						elif b != null and b.get("id") != null: bid = b.get("id")
						if bid == trapped_id:
							if typeof(b) == TYPE_DICTIONARY:
								b["trapped"] = false
								b["bone_prison_id"] = -1
							else:
								b.set("trapped", false)
								b.set("bone_prison_id", -1)
							break
				continue

			if trapped_id != -1:
				for b in balls:
					var bid = -2
					if typeof(b) == TYPE_DICTIONARY: bid = b.get("id", -2)
					elif b != null and b.get("id") != null: bid = b.get("id")
					if bid == trapped_id:
						var hid = -1
						if typeof(h) == TYPE_DICTIONARY: hid = h.get("id", -1)
						elif h != null and h.get("id") != null: hid = h.get("id")

						if typeof(b) == TYPE_DICTIONARY:
							b["x"] = h_x
							b["y"] = h_y
							b["vx"] = 0.0
							b["vy"] = 0.0
							b["speed"] = 0.0
							b["trapped"] = true
							b["bone_prison_id"] = hid
						else:
							b.set("x", h_x)
							b.set("y", h_y)
							b.set("vx", 0.0)
							b.set("vy", 0.0)
							b.set("speed", 0.0)
							b.set("trapped", true)
							b.set("bone_prison_id", hid)
						break

		elif kind == "bone_prison_trap":
			var act_timer = -1.0
			var h_team = ""
			var h_x = 0.0
			var h_y = 0.0
			var h_rad = 30.0
			var p_dur = 3.0
			var p_hp = 50.0

			if typeof(h) == TYPE_DICTIONARY:
				if h.has("activation_timer"): act_timer = h.get("activation_timer")
				h_team = h.get("owner_team", "")
				h_x = h.get("x", 0.0)
				h_y = h.get("y", 0.0)
				h_rad = h.get("radius", 30.0)
				p_dur = h.get("prison_duration", 3.0)
				p_hp = h.get("prison_hp", 50.0)
			else:
				if h.get("activation_timer") != null: act_timer = h.get("activation_timer")
				if h.get("owner_team") != null: h_team = h.get("owner_team")
				if h.get("x") != null: h_x = h.get("x")
				if h.get("y") != null: h_y = h.get("y")
				if h.get("radius") != null: h_rad = h.get("radius")
				if h.get("prison_duration") != null: p_dur = h.get("prison_duration")
				if h.get("prison_hp") != null: p_hp = h.get("prison_hp")

			if act_timer != -1.0:
				act_timer -= delta
				if typeof(h) == TYPE_DICTIONARY:
					h["activation_timer"] = act_timer
				else:
					h.set("activation_timer", act_timer)
				if act_timer > 0:
					continue

			for b in balls:
				var alive = false
				var b_team = ""
				var b_x = 0.0
				var b_y = 0.0
				var b_rad = 15.0
				var b_id = -1

				if typeof(b) == TYPE_DICTIONARY:
					alive = b.get("alive", false)
					b_team = b.get("team", "")
					b_x = b.get("x", 0.0)
					b_y = b.get("y", 0.0)
					b_rad = b.get("radius", 15.0)
					b_id = b.get("id", -1)
				elif b != null:
					if b.get("alive") != null: alive = b.get("alive")
					if b.get("team") != null: b_team = b.get("team")
					if b.get("x") != null: b_x = b.get("x")
					if b.get("y") != null: b_y = b.get("y")
					if b.get("radius") != null: b_rad = b.get("radius")
					if b.get("id") != null: b_id = b.get("id")

				if alive and b_team != h_team:
					var dist = sqrt(pow(b_x - h_x, 2) + pow(b_y - h_y, 2))
					if dist <= h_rad + b_rad:
						hazards_to_remove.append(h)

						var prison_id = 99999
						if world.has("next_id"):
							prison_id = world["next_id"]
							world["next_id"] += 1

						var prison = {
							"id": prison_id,
							"x": b_x,
							"y": b_y,
							"radius": 20.0,
							"kind": "bone_prison",
							"damage": 0.0,
							"duration": p_dur,
							"hp": p_hp,
							"trapped_ball_id": b_id,
							"owner_team": h_team
						}

						new_hazards.append(prison)

						if typeof(b) == TYPE_DICTIONARY:
							b["trapped"] = true
							b["bone_prison_id"] = prison_id
						else:
							b.set("trapped", true)
							b.set("bone_prison_id", prison_id)
						break

	for h in hazards_to_remove:
		world.arena.hazards.erase(h)

	for h in new_hazards:
		world.arena.hazards.append(h)
