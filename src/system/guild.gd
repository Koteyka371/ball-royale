class_name GuildManager
extends RefCounted

var filename = "user://guilds.json"
var data = {}

func _init():
    load_guilds()

func load_guilds():
    var file = FileAccess.open(filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            data = json.get_data()
            if not data.has("guilds"):
                data["guilds"] = {}
            if not data.has("territories"):
                data["territories"] = {}
            for g_name in data["guilds"].keys():
                if not data["guilds"][g_name].has("hq"):
                    data["guilds"][g_name]["hq"] = {
                        "statues": [],
                        "banners": [],
                        "training_arena_unlocked": false
                    }
            return

    data = {"guilds": {}, "territories": {}}

func save_guilds():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func create_guild(guild_name: String, creator_id: String) -> bool:
    if data["guilds"].has(guild_name):
        return false

    data["guilds"][guild_name] = {
        "members": [creator_id],
        "resources": 0,
        "buffs": {
            "bonus_hp": 0,
            "bonus_speed": 0,
            "bonus_damage": 0
        },
        "gvg_points": 0,
        "chat_history": [],
        "vault": [],
        "boss_progress": {},
        "hq": {
            "statues": [],
            "banners": [],
            "training_arena_unlocked": false
        }
    }
    save_guilds()
    return true

func join_guild(guild_name: String, player_id: String) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild["members"].has(player_id):
            guild["members"].append(player_id)
            save_guilds()
            return true
    return false

func leave_guild(guild_name: String, player_id: String) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild["members"].has(player_id):
            guild["members"].erase(player_id)
            if guild["members"].size() == 0:
                data["guilds"].erase(guild_name)
            save_guilds()
            return true
    return false

func donate_resources(guild_name: String, amount: int) -> bool:
    if data["guilds"].has(guild_name):
        data["guilds"][guild_name]["resources"] += amount
        save_guilds()
        return true
    return false

func unlock_buff(guild_name: String, buff_name: String, cost: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild["resources"] >= cost and guild["buffs"].has(buff_name):
            guild["resources"] -= cost
            guild["buffs"][buff_name] += 1
            save_guilds()
            return true
    return false

func get_guild_buffs(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        return data["guilds"][guild_name]["buffs"]
    return {"bonus_hp": 0, "bonus_speed": 0, "bonus_damage": 0}

func record_gvg_match(guild1_name: String, guild2_name: String, winner_name: String) -> bool:
    if data["guilds"].has(guild1_name) and data["guilds"].has(guild2_name):
        if winner_name == guild1_name:
            data["guilds"][guild1_name]["gvg_points"] += 10
            data["guilds"][guild2_name]["gvg_points"] = max(0, data["guilds"][guild2_name]["gvg_points"] - 5)
        elif winner_name == guild2_name:
            data["guilds"][guild2_name]["gvg_points"] += 10
            data["guilds"][guild1_name]["gvg_points"] = max(0, data["guilds"][guild1_name]["gvg_points"] - 5)
        save_guilds()
        return true
    return false

func get_guild(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        return data["guilds"][guild_name]
    return {}

func send_chat_message(guild_name: String, sender_id: String, message: String) -> bool:
    if data["guilds"].has(guild_name):
        if not data["guilds"][guild_name].has("chat_history"):
            data["guilds"][guild_name]["chat_history"] = []
        data["guilds"][guild_name]["chat_history"].append({
            "sender": sender_id,
            "message": message
        })
        save_guilds()
        return true
    return false

func get_chat_history(guild_name: String) -> Array:
    if data["guilds"].has(guild_name) and data["guilds"][guild_name].has("chat_history"):
        return data["guilds"][guild_name]["chat_history"]
    return []

func get_guild_leaderboard() -> Array:
    var guilds_list = []
    for guild_name in data["guilds"].keys():
        var info = data["guilds"][guild_name]
        var points = 0
        if info.has("gvg_points"):
            points = info["gvg_points"]
        guilds_list.append({
            "name": guild_name,
            "gvg_points": points
        })
    guilds_list.sort_custom(func(a, b): return a["gvg_points"] > b["gvg_points"])
    return guilds_list

func deposit_item(guild_name: String, item: String) -> bool:
    if data["guilds"].has(guild_name):
        if not data["guilds"][guild_name].has("vault"):
            data["guilds"][guild_name]["vault"] = []
        data["guilds"][guild_name]["vault"].append(item)
        save_guilds()
        return true
    return false

func withdraw_item(guild_name: String, item: String) -> bool:
    if data["guilds"].has(guild_name):
        if data["guilds"][guild_name].has("vault"):
            var vault = data["guilds"][guild_name]["vault"]
            if vault.has(item):
                vault.erase(item)
                save_guilds()
                return true
    return false

func capture_territory(guild_name: String, territory_name: String) -> bool:
    if data["guilds"].has(guild_name):
        if not data.has("territories"):
            data["territories"] = {}
        data["territories"][territory_name] = guild_name
        save_guilds()
        return true
    return false

func get_territories(guild_name: String) -> Array:
    var result = []
    if data.has("territories"):
        for t in data["territories"].keys():
            if data["territories"][t] == guild_name:
                result.append(t)
    return result

func collect_passive_resources():
    if not data.has("territories"):
        return
    for territory in data["territories"].keys():
        var owner = data["territories"][territory]
        if data["guilds"].has(owner):
            data["guilds"][owner]["resources"] += 5
    save_guilds()

func record_boss_damage(guild_name: String, damage: float, week_id: String) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("boss_progress"):
            guild["boss_progress"] = {}
        if not guild["boss_progress"].has(week_id):
            guild["boss_progress"][week_id] = {"damage_dealt": 0.0, "claimed_by": []}
        guild["boss_progress"][week_id]["damage_dealt"] += damage
        save_guilds()
        return true
    return false

func check_boss_defeated(guild_name: String, week_id: String, required_damage: float) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("boss_progress") and guild["boss_progress"].has(week_id):
            return guild["boss_progress"][week_id]["damage_dealt"] >= required_damage
    return false

func claim_boss_reward(guild_name: String, player_id: String, week_id: String, required_damage: float) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("boss_progress") and guild["boss_progress"].has(week_id):
            var progress = guild["boss_progress"][week_id]
            if progress["damage_dealt"] >= required_damage and not progress["claimed_by"].has(player_id):
                progress["claimed_by"].append(player_id)
                save_guilds()
                return true
    return false

func unlock_hq_feature(guild_name: String, feature_type: String, feature_id: String, cost: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild["resources"] >= cost:
            if not guild.has("hq"):
                guild["hq"] = {"statues": [], "banners": [], "training_arena_unlocked": false}

            if feature_type == "training_arena":
                if not guild["hq"]["training_arena_unlocked"]:
                    guild["resources"] -= cost
                    guild["hq"]["training_arena_unlocked"] = true
                    save_guilds()
                    return true
            elif feature_type in ["statues", "banners"]:
                if not guild["hq"].has(feature_type):
                    guild["hq"][feature_type] = []
                if not guild["hq"][feature_type].has(feature_id):
                    guild["resources"] -= cost
                    guild["hq"][feature_type].append(feature_id)
                    save_guilds()
                    return true
    return false

func get_hq_status(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("hq"):
            return guild["hq"]
        return {"statues": [], "banners": [], "training_arena_unlocked": false}
    return {}
