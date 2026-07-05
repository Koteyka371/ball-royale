class_name ClanManager
extends RefCounted

var filename = "user://clans.json"
var data = {}

func _init():
    load_clans()

func load_clans():
    var file = FileAccess.open(filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            data = json.get_data()
            if not data.has("clans"):
                data["clans"] = {}
            return

    data = {"clans": {}}

func save_clans():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func create_clan(clan_name: String, creator_id: String) -> bool:
    if data["clans"].has(clan_name):
        return false

    data["clans"][clan_name] = {
        "members": [creator_id],
        "quests": [],
        "points": 0
    }
    save_clans()
    return true

func join_clan(clan_name: String, player_id: String) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if not clan["members"].has(player_id):
            clan["members"].append(player_id)
            save_clans()
            return true
    return false

func leave_clan(clan_name: String, player_id: String) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan["members"].has(player_id):
            clan["members"].erase(player_id)
            if clan["members"].size() == 0:
                data["clans"].erase(clan_name)
            save_clans()
            return true
    return false

func add_clan_quest(clan_name: String, description: String, required_progress: int) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        clan["quests"].append({
            "description": description,
            "required": required_progress,
            "current": 0,
            "completed": false
        })
        save_clans()
        return true
    return false

func progress_clan_quest(clan_name: String, quest_index: int, amount: int) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if quest_index >= 0 and quest_index < clan["quests"].size():
            var quest = clan["quests"][quest_index]
            if not quest["completed"]:
                quest["current"] += amount
                if quest["current"] >= quest["required"]:
                    quest["current"] = quest["required"]
                    quest["completed"] = true
                    clan["points"] += 10
                save_clans()
                return true
    return false

func get_clan_quests(clan_name: String) -> Array:
    if data["clans"].has(clan_name):
        return data["clans"][clan_name]["quests"]
    return []

func add_clan_points(clan_name: String, amount: int) -> bool:
    if data["clans"].has(clan_name):
        data["clans"][clan_name]["points"] += amount
        save_clans()
        return true
    return false

func unlock_cosmetic(clan_name: String, cosmetic: String) -> bool:
    if data["clans"].has(clan_name):
        if not data["clans"][clan_name].has("cosmetics"):
            data["clans"][clan_name]["cosmetics"] = []
        if not data["clans"][clan_name]["cosmetics"].has(cosmetic):
            data["clans"][clan_name]["cosmetics"].append(cosmetic)
            save_clans()
            return true
    return false

func get_clan_leaderboard() -> Array:
    var clans_list = []
    for clan_name in data["clans"].keys():
        var info = data["clans"][clan_name]
        var pts = 0
        if info.has("points"):
            pts = info["points"]
        clans_list.append({
            "name": clan_name,
            "points": pts
        })
    clans_list.sort_custom(func(a, b): return a["points"] > b["points"])
    return clans_list
