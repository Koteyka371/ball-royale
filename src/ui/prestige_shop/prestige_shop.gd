class_name PrestigeShop
extends Control

var profile_manager = null

func _init(pm = null):
	if pm != null:
		profile_manager = pm
	else:
		profile_manager = ProfileManager.new()

func get_available_upgrades() -> Dictionary:
	return {
		"permanent_hp": {"cost": 5, "description": "Increases max HP permanently"},
		"permanent_speed": {"cost": 5, "description": "Increases base speed permanently"},
		"permanent_damage": {"cost": 5, "description": "Increases base damage permanently"},
		"mutator_unlocked": {"cost": 15, "description": "Unlocks custom match mutators (run mutators)"},
		"starting_artifact_shield": {"cost": 10, "description": "Start matches with a shield artifact"},
		"starting_artifact_dash": {"cost": 10, "description": "Start matches with a dash artifact"},
		"unlock_time_mage": {"cost": 25, "description": "Unlocks the Time-Mage ball archetype"},
		"shield_capacity_up": {"cost": 10, "description": "Increases reflect shield capacity by 20"},
		"shield_duration_up": {"cost": 10, "description": "Increases reflect shield duration by 1s"},
		"skin_neon": {"cost": 15, "description": "Unlock the Neon skin"},
		"skin_ninja": {"cost": 15, "description": "Unlock the Ninja skin"}
	}

func buy_upgrade(upgrade_name: String) -> bool:
	var upgrades = get_available_upgrades()
	if not upgrades.has(upgrade_name):
		return false
	var cost = upgrades[upgrade_name]["cost"]
	return profile_manager.buy_prestige_upgrade(upgrade_name, cost)


func get_wheel_rewards() -> Dictionary:
	return {
		"skill_points_10": {"type": "skill_points", "amount": 10, "weight": 40},
		"skill_points_50": {"type": "skill_points", "amount": 50, "weight": 20},
		"prestige_token": {"type": "prestige_tokens", "amount": 1, "weight": 10},
		"cosmetic_spin_master": {"type": "cosmetics", "name": "spin_master", "weight": 5},
		"nothing": {"type": "nothing", "weight": 25}
	}

func spin_wheel(cost: int = 1) -> Array:
	var current_tokens = 0
	if profile_manager != null and "data" in profile_manager:
		current_tokens = profile_manager.data.get("prestige_tokens", 0)
	else:
		return [false, "Profile manager error"]

	if current_tokens < cost:
		return [false, "Not enough tokens"]

	profile_manager.data["prestige_tokens"] = current_tokens - cost
	if profile_manager.has_method("save_profile"):
		profile_manager.save_profile()

	var rewards = get_wheel_rewards()
	var total_weight = 0.0
	for key in rewards.keys():
		total_weight += rewards[key]["weight"]

	var rand_val = randf_range(0, total_weight)

	var current_weight = 0.0
	var selected_reward_key = "nothing"
	for key in rewards.keys():
		current_weight += rewards[key]["weight"]
		if rand_val <= current_weight:
			selected_reward_key = key
			break

	var reward = rewards[selected_reward_key]
	var msg = ""

	if reward["type"] == "skill_points":
		if profile_manager.has_method("add_skill_points"):
			profile_manager.add_skill_points(reward["amount"])
		msg = "Won " + str(reward["amount"]) + " Skill Points!"
	elif reward["type"] == "prestige_tokens":
		profile_manager.data["prestige_tokens"] = profile_manager.data.get("prestige_tokens", 0) + reward["amount"]
		if profile_manager.has_method("save_profile"):
			profile_manager.save_profile()
		msg = "Won " + str(reward["amount"]) + " Prestige Token(s)!"
	elif reward["type"] == "cosmetics":
		if profile_manager.has_method("add_cosmetic"):
			profile_manager.add_cosmetic(reward["name"])
		msg = "Won cosmetic: " + reward["name"] + "!"
	else:
		msg = "Won nothing, better luck next time!"

	return [true, msg]

func _on_spin_pressed():
	var result = spin_wheel()
	var success = result[0]
	var msg = result[1]
	print(msg)
	if success:
		_refresh_ui()


var container: VBoxContainer
var token_label: Label

func _ready():
	container = VBoxContainer.new()
	add_child(container)

	token_label = Label.new()
	container.add_child(token_label)

	_refresh_ui()

func _refresh_ui():
	# Clear existing buttons
	for child in container.get_children():
		if child is Button:
			container.remove_child(child)
			child.queue_free()

	var tokens = 0
	if profile_manager != null and "data" in profile_manager:
		tokens = profile_manager.data.get("prestige_tokens", 0)

	token_label.text = "Prestige Tokens: " + str(tokens)

	var spin_btn = Button.new()
	spin_btn.text = "Spin Wheel (1 Token)"
	spin_btn.pressed.connect(self._on_spin_pressed)
	container.add_child(spin_btn)


	var upgrades = get_available_upgrades()
	for upgrade_name in upgrades.keys():
		var upgrade_data = upgrades[upgrade_name]
		var btn = Button.new()
		btn.text = upgrade_data["description"] + " (" + str(upgrade_data["cost"]) + " Tokens)"
		btn.pressed.connect(self._on_buy_pressed.bind(upgrade_name))
		container.add_child(btn)


func equip_skin(skin_name: String) -> bool:
	if profile_manager != null and profile_manager.has_method("equip_skin"):
		return profile_manager.equip_skin(skin_name)
	return false

func _on_buy_pressed(upgrade_name: String):
	var success = buy_upgrade(upgrade_name)
	if success:
		print("Successfully bought " + upgrade_name)
		_refresh_ui()
	else:
		print("Not enough tokens to buy " + upgrade_name)
