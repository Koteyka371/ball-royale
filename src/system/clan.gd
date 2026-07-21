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
            for clan_name in data["clans"].keys():
                var clan = data["clans"][clan_name]
                if not clan.has("perks"):
                    clan["perks"] = []
                if not clan.has("decorations"):
                    clan["decorations"] = []
                if not clan.has("hub"):
                    clan["hub"] = []
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
		"roles": {creator_id: "leader"},
		"stash": {},
		"quests": [],
		"points": 0,
		"territories": [],
		"perks": [],
		"decorations": [],
		"hub": []
	}
    save_clans()
    return true

func join_clan(clan_name: String, player_id: String) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if not clan["members"].has(player_id):
            clan["members"].append(player_id)
            if not clan.has("roles"):
                clan["roles"] = {}
            clan["roles"][player_id] = "member"
            save_clans()
            return true
    return false

func leave_clan(clan_name: String, player_id: String) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan["members"].has(player_id):
            clan["members"].erase(player_id)
            if clan.has("roles") and clan["roles"].has(player_id):
                clan["roles"].erase(player_id)
            if clan["members"].size() == 0:
                data["clans"].erase(clan_name)
            save_clans()
            return true
    return false

func set_member_role(clan_name: String, admin_id: String, target_id: String, new_role: String) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if not clan.has("roles"):
            clan["roles"] = {}
            for m in clan["members"]:
                clan["roles"][m] = "member"
            if clan["members"].size() > 0:
                clan["roles"][clan["members"][0]] = "leader"

        var admin_role = "member"
        if clan["roles"].has(admin_id):
            admin_role = clan["roles"][admin_id]

        if admin_role == "leader" and clan["members"].has(target_id):
            clan["roles"][target_id] = new_role
            save_clans()
            return true
    return false

func deposit_to_stash(clan_name: String, player_id: String, item_name: String, amount: int) -> bool:
    if amount <= 0:
        return false
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan["members"].has(player_id):
            if not clan.has("stash"):
                clan["stash"] = {}
            if not clan["stash"].has(item_name):
                clan["stash"][item_name] = 0
            clan["stash"][item_name] += amount
            save_clans()
            return true
    return false

func withdraw_from_stash(clan_name: String, player_id: String, item_name: String, amount: int) -> bool:
    if amount <= 0:
        return false
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan["members"].has(player_id):
            if not clan.has("roles"):
                clan["roles"] = {}
                for m in clan["members"]:
                    clan["roles"][m] = "member"
                if clan["members"].size() > 0:
                    clan["roles"][clan["members"][0]] = "leader"

            var role = "member"
            if clan["roles"].has(player_id):
                role = clan["roles"][player_id]

            if role == "leader" or role == "officer":
                if not clan.has("stash"):
                    clan["stash"] = {}
                if clan["stash"].has(item_name) and clan["stash"][item_name] >= amount:
                    clan["stash"][item_name] -= amount
                    if clan["stash"][item_name] == 0:
                        clan["stash"].erase(item_name)
                    save_clans()
                    return true
    return false

func add_clan_quest(clan_name: String, description: String, required_progress: int, rewards: Array = []) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        clan["quests"].append({
            "description": description,
            "required": required_progress,
            "current": 0,
            "completed": false,
            "rewards": rewards,
            "contributors": {}
        })
        save_clans()
        return true
    return false

func progress_clan_quest(clan_name: String, quest_index: int, amount: int, player_id: String = "") -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if quest_index >= 0 and quest_index < clan["quests"].size():
            var quest = clan["quests"][quest_index]
            if not quest["completed"]:
                quest["current"] += amount
                if player_id != "":
                    if not quest.has("contributors"):
                        quest["contributors"] = {}
                    if not quest["contributors"].has(player_id):
                        quest["contributors"][player_id] = 0
                    quest["contributors"][player_id] += amount
                if quest["current"] >= quest["required"]:
                    quest["current"] = quest["required"]
                    quest["completed"] = true
                    clan["points"] += 10
                    var rewards = []
                    if quest.has("rewards"):
                        rewards = quest["rewards"]
                    for reward in rewards:
                        var rtype = reward["type"]
                        var rval = reward["value"]
                        if rtype == "points":
                            clan["points"] += rval
                        elif rtype == "buff":
                            if not clan.has("buffs"):
                                clan["buffs"] = []
                            if not clan["buffs"].has(rval):
                                clan["buffs"].append(rval)
                        elif rtype == "cosmetic":
                            if not clan.has("cosmetics"):
                                clan["cosmetics"] = []
                            if not clan["cosmetics"].has(rval):
                                clan["cosmetics"].append(rval)
                        elif rtype == "stash_item":
                            if not clan.has("stash"):
                                clan["stash"] = {}
                            if not clan["stash"].has(rval):
                                clan["stash"][rval] = 0
                            var amt = 1
                            if reward.has("amount"):
                                amt = reward["amount"]
                            clan["stash"][rval] += amt
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


func unlock_buff(clan_name: String, buff_name: String) -> bool:
    if data["clans"].has(clan_name):
        if not data["clans"][clan_name].has("buffs"):
            data["clans"][clan_name]["buffs"] = []
        if not data["clans"][clan_name]["buffs"].has(buff_name):
            data["clans"][clan_name]["buffs"].append(buff_name)
            save_clans()
            return true
    return false


func capture_territory(clan_name: String, territory_name: String) -> bool:
	if data["clans"].has(clan_name):
		for c_name in data["clans"].keys():
			var c_data = data["clans"][c_name]
			if c_data.has("territories") and c_data["territories"].has(territory_name):
				c_data["territories"].erase(territory_name)

		if not data["clans"][clan_name].has("territories"):
			data["clans"][clan_name]["territories"] = []

		if not data["clans"][clan_name]["territories"].has(territory_name):
			data["clans"][clan_name]["territories"].append(territory_name)
			save_clans()
			return true
	return false

func get_clan_territories(clan_name: String) -> Array:
	if data["clans"].has(clan_name):
		var clan = data["clans"][clan_name]
		if clan.has("territories"):
			return clan["territories"]
	return []

func get_territory_owner(territory_name: String):
	for clan_name in data["clans"].keys():
		var clan_data = data["clans"][clan_name]
		if clan_data.has("territories") and clan_data["territories"].has(territory_name):
			return clan_name
	return null

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

func unlock_perk(clan_name: String, perk_name: String, cost: int, required_perk: String = "") -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        var current_points = 0
        if clan.has("points"):
            current_points = clan["points"]

        if current_points >= cost:
            if not clan.has("perks"):
                clan["perks"] = []

            if not clan["perks"].has(perk_name):
                if required_perk == "" or clan["perks"].has(required_perk):
                    clan["points"] -= cost
                    clan["perks"].append(perk_name)
                    save_clans()
                    return true
    return false

func get_clan_perks(clan_name: String) -> Array:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan.has("perks"):
            return clan["perks"]
    return []

func unlock_decoration(clan_name: String, decoration_name: String) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if not clan.has("decorations"):
            clan["decorations"] = []
        if not clan["decorations"].has(decoration_name):
            clan["decorations"].append(decoration_name)
            save_clans()
            return true
    return false

func place_decoration(clan_name: String, decoration_name: String, x: float, y: float) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan.has("decorations") and clan["decorations"].has(decoration_name):
            if not clan.has("hub"):
                clan["hub"] = []

            var new_hub = []
            for d in clan["hub"]:
                if d.has("x") and d.has("y"):
                    if d["x"] != x or d["y"] != y:
                        new_hub.append(d)

            new_hub.append({"decoration": decoration_name, "x": x, "y": y})
            clan["hub"] = new_hub
            save_clans()
            return true
    return false

func remove_decoration(clan_name: String, x: float, y: float) -> bool:
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan.has("hub"):
            var initial_len = clan["hub"].size()
            var new_hub = []
            for d in clan["hub"]:
                if d.has("x") and d.has("y"):
                    if d["x"] != x or d["y"] != y:
                        new_hub.append(d)
            clan["hub"] = new_hub
            if clan["hub"].size() < initial_len:
                save_clans()
                return true
    return false

func get_hub_buffs(clan_name: String) -> Array:
    var buffs = []
    if data["clans"].has(clan_name):
        var clan = data["clans"][clan_name]
        if clan.has("hub"):
            for d in clan["hub"]:
                if d.has("decoration"):
                    var dec_name = d["decoration"]
                    if dec_name == "Champion_Trophy":
                        if not buffs.has("Tournament_Champion_Aura"):
                            buffs.append("Tournament_Champion_Aura")
                    elif dec_name == "Speed_Statue":
                        if not buffs.has("Hub_Speed_Boost"):
                            buffs.append("Hub_Speed_Boost")
                    elif dec_name == "Health_Fountain":
                        if not buffs.has("Hub_Health_Regen"):
                            buffs.append("Hub_Health_Regen")
    return buffs

func start_weekly_tournament() -> bool:
    data["tournament_active"] = true
    data["tournament_scores"] = {}
    for clan_name in data["clans"].keys():
        data["tournament_scores"][clan_name] = 0
    save_clans()
    return true

func add_tournament_points(clan_name: String, points: int) -> bool:
    if data.has("tournament_active") and data["tournament_active"]:
        if not data.has("tournament_scores"):
            data["tournament_scores"] = {}
        if data["clans"].has(clan_name):
            if not data["tournament_scores"].has(clan_name):
                data["tournament_scores"][clan_name] = 0
            data["tournament_scores"][clan_name] += points
            save_clans()
            return true
    return false

func end_weekly_tournament() -> bool:
    if not (data.has("tournament_active") and data["tournament_active"]):
        return false

    var scores = {}
    if data.has("tournament_scores"):
        scores = data["tournament_scores"]

    var ranked_clans = []
    for clan_name in scores.keys():
        ranked_clans.append({"name": clan_name, "score": scores[clan_name]})

    ranked_clans.sort_custom(func(a, b): return a["score"] > b["score"])

    for i in range(ranked_clans.size()):
        var clan_name = ranked_clans[i]["name"]
        if not data["clans"].has(clan_name):
            continue

        if i == 0:
            add_clan_points(clan_name, 5000)
            unlock_cosmetic(clan_name, "Weekly_Champion_Aura")
            unlock_buff(clan_name, "Currency_Boost_Tier3")
        elif i == 1:
            add_clan_points(clan_name, 3000)
            unlock_buff(clan_name, "Currency_Boost_Tier2")
        elif i == 2:
            add_clan_points(clan_name, 2000)
            unlock_buff(clan_name, "Currency_Boost_Tier1")

    data["tournament_active"] = false
    data["tournament_scores"] = {}
    save_clans()
    return true
