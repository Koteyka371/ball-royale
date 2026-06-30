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
            return

    data = {"guilds": {}}

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
        "gvg_points": 0
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
