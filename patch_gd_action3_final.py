with open("src/ai/action.gd", "r") as f:
    content = f.read()

search = """					elif e_type == "hazard" or e_type == "item" or e_type == "booster":
						var n_t_var = ""
						if typeof(next_entity) == TYPE_OBJECT and next_entity.has_meta("trap_variant"): n_t_var = next_entity.get_meta("trap_variant")"""

replace = """					elif e_type == "hazard" or e_type == "item" or e_type == "booster":
						var n_kind = next_entity.get("kind") if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("kind") else (next_entity.kind if typeof(next_entity) == TYPE_OBJECT and "kind" in next_entity else "")
						var n_team = next_entity.get("team") if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("team") else (next_entity.team if typeof(next_entity) == TYPE_OBJECT and "team" in next_entity else null)
						var a_team = attacker.get_meta("team") if attacker.has_method("get_meta") and attacker.has_meta("team") else (attacker["team"] if typeof(attacker) == TYPE_DICTIONARY and attacker.has("team") else (attacker.team if "team" in attacker else null))

						if n_kind == "mirage_decoy" and n_team != a_team:
							var n_owner = next_entity.get("owner_id") if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("owner_id") else (next_entity.owner_id if typeof(next_entity) == TYPE_OBJECT and "owner_id" in next_entity else null)
							var n_x = next_entity.get("x") if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("x") else (next_entity.x if typeof(next_entity) == TYPE_OBJECT and "x" in next_entity else 0.0)
							var n_y = next_entity.get("y") if typeof(next_entity) == TYPE_DICTIONARY and next_entity.has("y") else (next_entity.y if typeof(next_entity) == TYPE_OBJECT and "y" in next_entity else 0.0)

							var emp = {
								"id": 21000 + self.world.arena.hazards.size(),
								"x": n_x,
								"y": n_y,
								"radius": 40.0,
								"kind": "emp_burst",
								"damage": 20.0,
								"duration": 0.5,
								"owner_id": n_owner,
								"team": n_team
							}
							self.world.arena.hazards.append(emp)
							var idx = self.world.arena.hazards.find(next_entity)
							if idx != -1:
								self.world.arena.hazards.remove_at(idx)

						var n_t_var = ""
						if typeof(next_entity) == TYPE_OBJECT and next_entity.has_meta("trap_variant"): n_t_var = next_entity.get_meta("trap_variant")"""

if search in content:
    content = content.replace(search, replace, 1)
    with open("src/ai/action.gd", "w") as f:
        f.write(content)
    print("Action.gd execute attack patched successfully")
else:
    print("Search string not found in action.gd execute attack")
