class_name BallGenetics
extends RefCounted

var battles_to_reproduce: int
var mutation_rate: float
var mutation_amount: float
var population_history: Dictionary
var colors: Array
var skills: Array

func _init(_battles_to_reproduce: int = 3, _mutation_rate: float = 0.1, _mutation_amount: float = 0.15) -> void:
	battles_to_reproduce = _battles_to_reproduce
	mutation_rate = _mutation_rate
	mutation_amount = _mutation_amount
	population_history = {}

	colors = [
		"red", "gray", "purple", "green", "blue", "orange", "crimson", "darkred",
		"cyan", "brown", "lime", "gold", "lightblue", "black", "white", "pink", "yellow"
	]

	skills = [
		"wave_attack", "shield", "dash", "health_link", "precision_shot",
		"explosion", "rage_burst", "ground_pound", "phase_through",
		"steal_boost", "clone", "protect_ally", "command", "stealth", "summon_minions"
	]

func _generate_dna_hash(dna: Dictionary) -> String:
	var rounded_dna = {}
	for k in dna.keys():
		var v = dna[k]
		if typeof(v) == TYPE_FLOAT:
			rounded_dna[k] = snapped(v, 0.01)
		else:
			rounded_dna[k] = v

	var keys = rounded_dna.keys()
	keys.sort()

	var hash_parts = []
	for k in keys:
		hash_parts.append(str(k) + ":" + str(rounded_dna[k]))

	return "-".join(hash_parts)

func extract_dna(ball: Object) -> Dictionary:
	return {
		"speed": ball.get("speed") if "speed" in ball else 2.0,
		"damage": ball.get("damage") if "damage" in ball else 15.0,
		"max_hp": ball.get("max_hp") if "max_hp" in ball else 100.0,
		"color": ball.get("color") if "color" in ball else "red",
		"skin": ball.get("skin") if "skin" in ball else "default",
		"skill": ball.get("skill") if "skill" in ball else "dash",
		"skill_cooldown": ball.get("skill_cooldown") if "skill_cooldown" in ball else 5.0,
		"ball_type": ball.get("ball_type") if "ball_type" in ball else "unknown"
	}

func register_survivors(survivors: Array) -> void:
	for ball in survivors:
		var dna = extract_dna(ball)
		var dna_hash = _generate_dna_hash(dna)

		if not population_history.has(dna_hash):
			population_history[dna_hash] = {
				"survivals": 1,
				"dna": dna
			}
		else:
			population_history[dna_hash]["survivals"] += 1

func generate_offspring(count: int) -> Array:
	var eligible_parents = []
	for hash_val in population_history.keys():
		var data = population_history[hash_val]
		if data["survivals"] >= battles_to_reproduce:
			var weight = max(1, data["survivals"] - battles_to_reproduce + 1)
			for i in range(weight):
				eligible_parents.append(data["dna"])

	if eligible_parents.is_empty():
		var sorted_history = population_history.values()
		sorted_history.sort_custom(func(a, b): return a["survivals"] > b["survivals"])

		var top_count = max(1, int(sorted_history.size() * 0.2))
		for i in range(min(top_count, sorted_history.size())):
			eligible_parents.append(sorted_history[i]["dna"])

	if eligible_parents.is_empty():
		return []

	var offspring = []
	for i in range(count):
		var parent_dna = eligible_parents[randi() % eligible_parents.size()]
		var child_dna = mutate(parent_dna)

		var survivals = 0
		for hash_v in population_history.keys():
			if population_history[hash_v]["dna"] == parent_dna:
				survivals = population_history[hash_v]["survivals"]
				break

		if survivals >= 10:
			child_dna["skin"] = "legendary"
		elif survivals >= 5:
			child_dna["skin"] = "elite"
		elif survivals >= 3:
			child_dna["skin"] = "veteran"
		else:
			child_dna["skin"] = "default"

		offspring.append(child_dna)

	return offspring

func mutate(dna: Dictionary) -> Dictionary:
	var child = dna.duplicate(true)
	var mutated = false

	for stat in ["speed", "damage", "max_hp", "skill_cooldown"]:
		if child.has(stat) and randf() < mutation_rate:
			var factor = 1.0 + randf_range(-mutation_amount, mutation_amount)
			child[stat] *= factor
			mutated = true

			if stat == "speed":
				child[stat] = max(0.5, child[stat])
			elif stat == "damage":
				child[stat] = max(1.0, child[stat])
			elif stat == "max_hp":
				child[stat] = max(10.0, child[stat])
			elif stat == "skill_cooldown":
				child[stat] = max(1.0, child[stat])

	if child.has("color") and randf() < (mutation_rate * 0.5):
		child["color"] = colors[randi() % colors.size()]
		mutated = true

	if child.has("skill") and randf() < (mutation_rate * 0.2):
		child["skill"] = skills[randi() % skills.size()]
		mutated = true

	if mutated and not child["ball_type"].ends_with("_evolved"):
		child["ball_type"] = child["ball_type"] + "_evolved"

	return child
