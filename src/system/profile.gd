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
            if not data.has("inventory"):
                data["inventory"] = {"materials": {}, "crafted_items": {}}
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
            if not data.has("login_streak"):
                data["login_streak"] = 0
            if not data.has("last_login_date"):
                data["last_login_date"] = ""
            if not data.has("guild_name"):
                data["guild_name"] = ""
            if not data.has("clan_name"):
                data["clan_name"] = ""
            return

    # Default profile
    data = {
        "skill_points": 0,
        "inventory": {"materials": {}, "crafted_items": {}},
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
        "nemeses": {},
        "login_streak": 0,
        "last_login_date": "",
        "guild_name": "",
        "clan_name": ""
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


func get_unlocked_balls() -> Array:
    var unlocked = []
    if data.has("unlocked_balls"):
        unlocked = data["unlocked_balls"].duplicate()
    if data.get("prestige_upgrades", {}).get("unlock_time_mage", 0) > 0:
        if not unlocked.has("time_mage"):
            unlocked.append("time_mage")
    return unlocked

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
	return data.get("prestige_level", 0) >= 5 or data.get("prestige_upgrades", {}).get("mutator_unlocked", 0) > 0

func can_prestige() -> bool:
    var unlocked_balls = get_unlocked_balls()
    var unlocked_all_balls = unlocked_balls.size() >= TOTAL_BALLS
    var bonuses = data.get("bonuses", {})
    var maxed_hp = bonuses.get("bonus_hp", 0) >= MAX_BONUS_LEVEL
    var maxed_speed = bonuses.get("bonus_speed", 0) >= MAX_BONUS_LEVEL
    var maxed_damage = bonuses.get("bonus_damage", 0) >= MAX_BONUS_LEVEL
    return unlocked_all_balls and maxed_hp and maxed_speed and maxed_damage


func _to_roman(num: int) -> String:
    var val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    var syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    var roman_num = ""
    var i = 0
    while num > 0:
        for _k in range(num / val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

func do_prestige() -> bool:
    if can_prestige():
        var current_prestige = data.get("prestige_level", 0)
        var tokens_earned = 5 + current_prestige + (data.get("skill_points", 0) / 100)
        var current_tokens = data.get("prestige_tokens", 0)
        var current_upgrades = data.get("prestige_upgrades", {})

        data = {
            "skill_points": 0,
            "inventory": {"materials": {}, "crafted_items": {}},
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
        "badges": data.get("badges", []),
            "status_effects": data.get("status_effects", []),
            "nemeses": data.get("nemeses", {}),
            "login_streak": data.get("login_streak", 0),
            "last_login_date": data.get("last_login_date", ""),
            "guild_name": data.get("guild_name", "")
        }

        var new_prestige = current_prestige + 1
        var level = 5
        while level <= new_prestige:
            if level == 5:
                if not data["titles"].has("Prestige V Champion"):
                    data["titles"].append("Prestige V Champion")
                if not data["cosmetics"].has("prestige_aura_gold"):
                    data["cosmetics"].append("prestige_aura_gold")
                if not data["unlocked_balls"].has("prestige_master"):
                    data["unlocked_balls"].append("prestige_master")
            elif level == 10:
                if not data["titles"].has("Prestige X Grandmaster"):
                    data["titles"].append("Prestige X Grandmaster")
                if not data["cosmetics"].has("prestige_aura_diamond"):
                    data["cosmetics"].append("prestige_aura_diamond")
                if not data["unlocked_balls"].has("prestige_grandmaster"):
                    data["unlocked_balls"].append("prestige_grandmaster")
            else:
                var roman = _to_roman(level)
                var title = "Prestige " + roman + " Legend"
                var aura = "prestige_aura_tier_" + str(level)
                var skin = "prestige_skin_" + str(level)

                if not data["titles"].has(title):
                    data["titles"].append(title)
                if not data["cosmetics"].has(aura):
                    data["cosmetics"].append(aura)
                if not data["unlocked_balls"].has(skin):
                    data["unlocked_balls"].append(skin)
            level += 5

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

func add_badge(badge_name: String):
    if not data.has("badges"):
        data["badges"] = []
    if not data["badges"].has(badge_name):
        data["badges"].append(badge_name)
        save_profile()

func save_loadout(loadout_name: String, ball_type: String, trap_variant: String, preferred_bonuses: Dictionary = {}, cosmetic: String = "", title: String = "", badge: String = ""):
    if not data.has("loadouts"):
        data["loadouts"] = {}
    data["loadouts"][loadout_name] = {
        "ball_type": ball_type,
        "trap_variant": trap_variant,
        "preferred_bonuses": preferred_bonuses,
        "cosmetic": cosmetic,
        "title": title,
        "badge": badge
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


func generate_loadout_code(loadout_name: String) -> String:
    var loadout = get_loadout(loadout_name)
    if loadout.is_empty():
        return ""
    var json_str = JSON.stringify(loadout)
    var compressed = json_str.to_utf8_buffer().compress(FileAccess.COMPRESSION_DEFLATE)
    var b64 = Marshalls.raw_to_base64(compressed).replace("+", "-").replace("/", "_").trim_suffix("=")
    return b64

func import_loadout_code(loadout_name: String, code: String) -> bool:
    if code == "":
        return false
    var padding = ""
    var m = (4 - (code.length() % 4)) % 4
    for i in range(m):
        padding += "="
    var b64_bytes = Marshalls.base64_to_raw(code.replace("-", "+").replace("_", "/") + padding)
    if b64_bytes.size() == 0:
        return false
    var decompressed = b64_bytes.decompress_dynamic(-1, FileAccess.COMPRESSION_DEFLATE)
    if decompressed.size() == 0:
        return false
    var json = JSON.new()
    var error = json.parse(decompressed.get_string_from_utf8())
    if error == OK:
        var parsed = json.get_data()
        if typeof(parsed) == TYPE_DICTIONARY and parsed.has("ball_type") and parsed.has("trap_variant"):
            if not data.has("inventory"):
                data["inventory"] = {"materials": {}, "crafted_items": {}}
            if not data.has("loadouts"):
                data["loadouts"] = {}
            data["loadouts"][loadout_name] = parsed
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

func process_daily_login(current_date_str: String) -> Dictionary:
    var last_date_str = data.get("last_login_date", "")
    if last_date_str == current_date_str:
        return {}

    var streak = data.get("login_streak", 0)

    if last_date_str != "":
        var current_time = Time.get_unix_time_from_datetime_string(current_date_str + "T00:00:00")
        var last_time = Time.get_unix_time_from_datetime_string(last_date_str + "T00:00:00")
        var diff_days = round((current_time - last_time) / 86400.0)
        if diff_days == 1:
            streak += 1
        else:
            streak = 1
    else:
        streak = 1

    data["login_streak"] = streak
    data["last_login_date"] = current_date_str

    var sp_reward = 10 * min(streak, 10)

    var current_time_unix = Time.get_unix_time_from_datetime_string(current_date_str + "T00:00:00")
    var current_datetime = Time.get_datetime_dict_from_unix_time(current_time_unix)
    var is_weekend = current_datetime.weekday == Time.WEEKDAY_SATURDAY or current_datetime.weekday == Time.WEEKDAY_SUNDAY
    if is_weekend:
        sp_reward *= 2

    add_skill_points(sp_reward)
    var rewards = {"skill_points": sp_reward}

    if streak > 0 and streak % 7 == 0:
        data["prestige_tokens"] = data.get("prestige_tokens", 0) + 1
        rewards["prestige_tokens"] = 1
        var cosmetic_name = "streak_master_" + str(streak)
        add_cosmetic(cosmetic_name)
        rewards["cosmetics"] = cosmetic_name

    save_profile()
    return rewards

func add_ancient_fragment() -> bool:
    var count = data.get("ancient_fragments", 0) + 1
    data["ancient_fragments"] = count
    if count >= 3:
        data["ancient_fragments"] -= 3
        var unlocked = false
        if not data.get("cosmetics", []).has("ancient_aura"):
            add_cosmetic("ancient_aura")
            unlocked = true
        if not data.get("unlocked_balls", []).has("ancient_guardian"):
            if not data.has("unlocked_balls"):
                data["unlocked_balls"] = []
            data["unlocked_balls"].append("ancient_guardian")
            unlocked = true
        if unlocked:
            save_profile()
        return true
    save_profile()
    return false

func add_material(material_name: String, amount: int) -> void:
    if not data.has("inventory"):
        data["inventory"] = {"materials": {}, "crafted_items": {}}
    var mats = data["inventory"]["materials"]
    if mats.has(material_name):
        mats[material_name] += amount
    else:
        mats[material_name] = amount
    save_profile()

func craft_item(recipe_id: String) -> bool:
    var recipes = {
        "health_potion": {"materials": {"Iron Ore": 1, "Magic Dust": 1}, "yields": 1},
        "speed_boost": {"materials": {"Magic Dust": 2}, "yields": 1},
        "artifact": {"materials": {"Void Shard": 3}, "crafted_items": {"health_potion": 1}, "yields": 1}
    }
    if not recipes.has(recipe_id): return false
    if not data.has("inventory"): data["inventory"] = {"materials": {}, "crafted_items": {}}
    var inv = data["inventory"]
    var req = recipes[recipe_id]
    var req_mats = req.get("materials", {})
    var req_craft = req.get("crafted_items", {})

    for m in req_mats.keys():
        if not inv["materials"].has(m) or inv["materials"][m] < req_mats[m]: return false
    for c_item in req_craft.keys():
        if not inv["crafted_items"].has(c_item) or inv["crafted_items"][c_item] < req_craft[c_item]: return false

    for m in req_mats.keys():
        inv["materials"][m] -= req_mats[m]
    for c_item in req_craft.keys():
        inv["crafted_items"][c_item] -= req_craft[c_item]

    if inv["crafted_items"].has(recipe_id):
        inv["crafted_items"][recipe_id] += req["yields"]
    else:
        inv["crafted_items"][recipe_id] = req["yields"]
    save_profile()
    return true
