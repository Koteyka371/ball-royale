class_name ProfileManager
extends RefCounted

const TOTAL_BALLS = 34
const MAX_BONUS_LEVEL = 10

var filename = "user://profile.json"
var data = {}

func _init():
    load_profile()

func load_profile():
    var file = FileAccess.open(filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            data = json.get_data()
            if not data.has("loadouts"):
                data["loadouts"] = {}
            if not data.has("prestige_level"):
                data["prestige_level"] = 0
            if not data.has("prestige_tokens"):
                data["prestige_tokens"] = 0
            if not data.has("prestige_upgrades"):
                data["prestige_upgrades"] = {}
            if not data.has("quests"):
                data["quests"] = []
            if not data.has("cosmetics"):
                data["cosmetics"] = []
            if not data.has("titles"):
                data["titles"] = []
            if not data.has("status_effects"):
                data["status_effects"] = []
            if not data.has("nemeses"):
                data["nemeses"] = {}
            return

    # Default profile
    data = {
        "skill_points": 0,
        "unlocked_balls": ["basic"],
        "bonuses": {
            "bonus_hp": 0,
            "bonus_speed": 0,
            "bonus_damage": 0
        },
        "loadouts": {},
        "prestige_level": 0,
            "prestige_tokens": 0,
            "prestige_upgrades": {},
        "quests": [],
        "cosmetics": [],
        "titles": [],
        "status_effects": [],
        "nemeses": {}
    }

func add_quest(quest_description: String, reward: int):
    if not data.has("quests"):
        data["quests"] = []
    data["quests"].append({
        "description": quest_description,
        "reward": reward,
        "completed": false
    })
    save_profile()

func get_quests() -> Array:
    return data.get("quests", [])

func complete_quest(quest_index: int) -> bool:
    if data.has("quests") and quest_index >= 0 and quest_index < data["quests"].size():
        var quest = data["quests"][quest_index]
        if not quest.get("completed", false):
            quest["completed"] = true
            add_skill_points(quest["reward"])
            return true
    return false

func save_profile():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func add_skill_points(points: int):
    data["skill_points"] += points
    save_profile()

func unlock_ball(ball_name: String, cost: int) -> bool:
    if data["skill_points"] >= cost and not data["unlocked_balls"].has(ball_name):
        data["skill_points"] -= cost
        data["unlocked_balls"].append(ball_name)
        save_profile()
        return true
    return false

func upgrade_bonus(bonus_name: String, cost: int) -> bool:
    if data["bonuses"].has(bonus_name) and data["skill_points"] >= cost:
        data["skill_points"] -= cost
        data["bonuses"][bonus_name] += 1
        save_profile()
        return true
    return false

func are_mutators_unlocked() -> bool:
	return data.get("prestige_level", 0) >= 5

func can_prestige() -> bool:
    var unlocked_balls = data.get("unlocked_balls", [])
    var unlocked_all_balls = unlocked_balls.size() >= TOTAL_BALLS
    var bonuses = data.get("bonuses", {})
    var maxed_hp = bonuses.get("bonus_hp", 0) >= MAX_BONUS_LEVEL
    var maxed_speed = bonuses.get("bonus_speed", 0) >= MAX_BONUS_LEVEL
    var maxed_damage = bonuses.get("bonus_damage", 0) >= MAX_BONUS_LEVEL
    return unlocked_all_balls and maxed_hp and maxed_speed and maxed_damage

func do_prestige() -> bool:
    if can_prestige():
        var current_prestige = data.get("prestige_level", 0)
        var tokens_earned = 5 + current_prestige + (data.get("skill_points", 0) / 100)
        var current_tokens = data.get("prestige_tokens", 0)
        var current_upgrades = data.get("prestige_upgrades", {})

        data = {
            "skill_points": 0,
            "unlocked_balls": ["basic"],
            "bonuses": {
                "bonus_hp": 0,
                "bonus_speed": 0,
                "bonus_damage": 0
            },
            "loadouts": data.get("loadouts", {}),
            "prestige_level": current_prestige + 1,
            "prestige_tokens": current_tokens + tokens_earned,
            "prestige_upgrades": current_upgrades,
            "quests": [],
            "cosmetics": data.get("cosmetics", []),
            "titles": data.get("titles", []),
            "status_effects": data.get("status_effects", []),
            "nemeses": data.get("nemeses", {})
        }
        save_profile()
        var lm = load("res://src/system/leaderboard.gd").new(self)
        lm.update_prestige("local_player", current_prestige + 1)
        lm.check_season()
        return true
    return false

func buy_prestige_upgrade(upgrade_name: String, cost: int) -> bool:
    var current_tokens = data.get("prestige_tokens", 0)
    var upgrades = data.get("prestige_upgrades", {})

    if current_tokens >= cost:
        data["prestige_tokens"] = current_tokens - cost
        upgrades[upgrade_name] = upgrades.get(upgrade_name, 0) + 1
        data["prestige_upgrades"] = upgrades
        save_profile()
        return true
    return false

func add_cosmetic(cosmetic_name: String):
    if not data.has("cosmetics"):
        data["cosmetics"] = []
    if not data["cosmetics"].has(cosmetic_name):
        data["cosmetics"].append(cosmetic_name)
        save_profile()

func add_title(title_name: String):
    if not data.has("titles"):
        data["titles"] = []
    if not data["titles"].has(title_name):
        data["titles"].append(title_name)
        save_profile()

func save_loadout(loadout_name: String, ball_type: String, trap_variant: String, preferred_bonuses: Dictionary = {}, cosmetic: String = "", title: String = ""):
    if not data.has("loadouts"):
        data["loadouts"] = {}
    data["loadouts"][loadout_name] = {
        "ball_type": ball_type,
        "trap_variant": trap_variant,
        "preferred_bonuses": preferred_bonuses,
        "cosmetic": cosmetic,
        "title": title
    }
    save_profile()

func set_default_loadout(loadout_name: String) -> bool:
    if data.has("loadouts") and data["loadouts"].has(loadout_name):
        data["default_loadout"] = loadout_name
        save_profile()
        return true
    return false

func get_default_loadout() -> String:
    return data.get("default_loadout", "")

func get_loadout(loadout_name: String) -> Dictionary:
    if data.has("loadouts") and data["loadouts"].has(loadout_name):
        return data["loadouts"][loadout_name]
    return {}

func get_all_loadouts() -> Dictionary:
    if data.has("loadouts"):
        return data["loadouts"]
    return {}

func delete_loadout(loadout_name: String) -> bool:
    if data.has("loadouts") and data["loadouts"].has(loadout_name):
        data["loadouts"].erase(loadout_name)
        save_profile()
        return true
    return false

func add_status_effect(effect_name: String):
    if not data.has("status_effects"):
        data["status_effects"] = []
    if not data["status_effects"].has(effect_name):
        data["status_effects"].append(effect_name)
        save_profile()

func add_kill(killer_type: String, victim_type: String) -> void:
    if not data.has("nemeses"):
        data["nemeses"] = {}
    if not data["nemeses"].has(killer_type):
        data["nemeses"][killer_type] = {}
    if not data["nemeses"][killer_type].has(victim_type):
        data["nemeses"][killer_type][victim_type] = 0
    data["nemeses"][killer_type][victim_type] += 1
    save_profile()

func is_nemesis(killer_type: String, victim_type: String) -> bool:
    if not data.has("nemeses"):
        return false
    if data["nemeses"].has(killer_type) and data["nemeses"][killer_type].has(victim_type):
        return data["nemeses"][killer_type][victim_type] >= 2
    return false
