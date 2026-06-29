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
            if not data.has("quests"):
                data["quests"] = []
            if not data.has("cosmetics"):
                data["cosmetics"] = []
            if not data.has("titles"):
                data["titles"] = []
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
        "quests": [],
        "cosmetics": [],
        "titles": []
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
            "quests": [],
            "cosmetics": data.get("cosmetics", []),
            "titles": data.get("titles", [])
        }
        save_profile()
        var lm = load("res://src/system/leaderboard.gd").new(self)
        lm.update_prestige("local_player", current_prestige + 1)
        lm.check_season()
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

func save_loadout(loadout_name: String, ball_type: String, trap_variant: String, preferred_bonuses: Dictionary = {}):
    if not data.has("loadouts"):
        data["loadouts"] = {}
    data["loadouts"][loadout_name] = {
        "ball_type": ball_type,
        "trap_variant": trap_variant,
        "preferred_bonuses": preferred_bonuses
    }
    save_profile()

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
