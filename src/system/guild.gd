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
                        "cosmetics": [],
                        "mini_games": {},
                        "training_arena_unlocked": false
                    }
                elif not data["guilds"][g_name]["hq"].has("mini_games"):
                    data["guilds"][g_name]["hq"]["mini_games"] = {}

                if not data["guilds"][g_name].has("guild_xp"):
                    data["guilds"][g_name]["guild_xp"] = 0
                if not data["guilds"][g_name].has("perks"):
                    data["guilds"][g_name]["perks"] = []
                if not data["guilds"][g_name].has("active_bounties"):
                    data["guilds"][g_name]["active_bounties"] = {}
                if not data["guilds"][g_name].has("prestige_pool"):
                    data["guilds"][g_name]["prestige_pool"] = 0
                if not data["guilds"][g_name].has("titles"):
                    data["guilds"][g_name]["titles"] = []
                if not data["guilds"][g_name].has("cosmetic_auras"):
                    data["guilds"][g_name]["cosmetic_auras"] = []
                if not data["guilds"][g_name].has("emblem"):
                    data["guilds"][g_name]["emblem"] = {"shape": "circle", "color": "white", "symbol": "none"}
                if not data["guilds"][g_name].has("unlocked_emblem_parts"):
                    data["guilds"][g_name]["unlocked_emblem_parts"] = {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]}
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
        "level": 1,
        "resources": 0,
        "prestige_pool": 0,
        "titles": [],
        "cosmetic_auras": [],
        "buffs": {
            "bonus_hp": 0,
            "bonus_speed": 0,
            "bonus_damage": 0
        },
        "gvg_points": 0,
        "guild_xp": 0,
        "perks": [],
        "active_bounties": {},
        "chat_history": [],
        "vault": [],
        "boss_progress": {},
        "hq": {
            "statues": [],
            "banners": [],
            "cosmetics": [],
            "mini_games": {},
            "training_arena_unlocked": false
        },
        "emblem": {"shape": "circle", "color": "white", "symbol": "none"},
        "unlocked_emblem_parts": {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]}
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


func donate_prestige(guild_name: String, amount: int) -> bool:
    if data["guilds"].has(guild_name):
        if not data["guilds"][guild_name].has("prestige_pool"):
            data["guilds"][guild_name]["prestige_pool"] = 0
        data["guilds"][guild_name]["prestige_pool"] += amount
        save_guilds()
        return true
    return false

func unlock_global_cosmetic(guild_name: String, cosmetic_id: String, cost: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("prestige_pool"):
            guild["prestige_pool"] = 0
        if guild["prestige_pool"] >= cost:
            if not guild.has("cosmetic_auras"):
                guild["cosmetic_auras"] = []
            if not guild["cosmetic_auras"].has(cosmetic_id):
                guild["prestige_pool"] -= cost
                guild["cosmetic_auras"].append(cosmetic_id)
                save_guilds()
                return true
    return false

func unlock_global_title(guild_name: String, title_id: String, cost: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("prestige_pool"):
            guild["prestige_pool"] = 0
        if guild["prestige_pool"] >= cost:
            if not guild.has("titles"):
                guild["titles"] = []
            if not guild["titles"].has(title_id):
                guild["prestige_pool"] -= cost
                guild["titles"].append(title_id)
                save_guilds()
                return true
    return false

func get_unlocked_cosmetics(guild_name: String) -> Array:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("cosmetic_auras"):
            return guild["cosmetic_auras"]
    return []

func get_unlocked_titles(guild_name: String) -> Array:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("titles"):
            return guild["titles"]
    return []

func donate_resources(guild_name: String, amount: int) -> bool:
    if data["guilds"].has(guild_name):
        data["guilds"][guild_name]["resources"] += amount
        save_guilds()
        return true
    return false


func upgrade_guild_level(guild_name: String, cost: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var points = 0
        if guild.has("gvg_points"):
            points = guild["gvg_points"]

        if points >= cost:
            guild["gvg_points"] = points - cost
            if not guild.has("level"):
                guild["level"] = 1
            guild["level"] += 1
            save_guilds()
            return true
    return false

func unlock_buff(guild_name: String, buff_name: String, cost: int, required_level: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var current_level = 1
        if guild.has("level"):
            current_level = guild["level"]
        if guild["resources"] >= cost and guild["buffs"].has(buff_name) and current_level >= required_level:
            guild["resources"] -= cost
            guild["buffs"][buff_name] += 1
            save_guilds()
            return true
    return false


func place_bounty(guild_name: String, target_guild_name: String, reward_points: int) -> bool:
    if data["guilds"].has(guild_name) and data["guilds"].has(target_guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("resources") and guild["resources"] >= reward_points:
            guild["resources"] -= reward_points
            var target_guild = data["guilds"][target_guild_name]
            if not target_guild.has("active_bounties"):
                target_guild["active_bounties"] = {}

            if not target_guild["active_bounties"].has(guild_name):
                target_guild["active_bounties"][guild_name] = 0
            target_guild["active_bounties"][guild_name] += reward_points
            save_guilds()
            return true
    return false

func get_bounties_on_guild(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("active_bounties"):
            return guild["active_bounties"]
    return {}

func unlock_emblem_part(guild_name: String, part_type: String, part_id: String, cost: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var resources = 0
        if guild.has("resources"):
            resources = guild["resources"]

        if resources >= cost:
            var unlocked_parts = {"shapes": [], "colors": [], "symbols": []}
            if guild.has("unlocked_emblem_parts"):
                unlocked_parts = guild["unlocked_emblem_parts"]

            if unlocked_parts.has(part_type):
                if not unlocked_parts[part_type].has(part_id):
                    guild["resources"] -= cost
                    unlocked_parts[part_type].append(part_id)
                    guild["unlocked_emblem_parts"] = unlocked_parts
                    save_guilds()
                    return true
    return false

func update_emblem(guild_name: String, shape: String, color: String, symbol: String) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var unlocked = {"shapes": [], "colors": [], "symbols": []}
        if guild.has("unlocked_emblem_parts"):
            unlocked = guild["unlocked_emblem_parts"]

        var shapes = []
        if unlocked.has("shapes"): shapes = unlocked["shapes"]
        var colors = []
        if unlocked.has("colors"): colors = unlocked["colors"]
        var symbols = []
        if unlocked.has("symbols"): symbols = unlocked["symbols"]

        if shapes.has(shape) and colors.has(color) and symbols.has(symbol):
            guild["emblem"] = {"shape": shape, "color": color, "symbol": symbol}
            save_guilds()
            return true
    return false

func claim_bounty(target_guild_name: String, claiming_guild_name: String) -> int:
    if data["guilds"].has(target_guild_name) and data["guilds"].has(claiming_guild_name):
        var target_guild = data["guilds"][target_guild_name]
        var claiming_guild = data["guilds"][claiming_guild_name]

        if target_guild.has("active_bounties"):
            var bounties = target_guild["active_bounties"]
            if bounties.has(claiming_guild_name) and bounties[claiming_guild_name] > 0:
                var reward = bounties[claiming_guild_name]
                if not claiming_guild.has("resources"):
                    claiming_guild["resources"] = 0
                claiming_guild["resources"] += reward
                bounties[claiming_guild_name] = 0
                save_guilds()
                return reward
    return 0


func register_for_tournament(guild_name: String, tournament_id: String) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("tournaments"):
            guild["tournaments"] = []
        if not guild["tournaments"].has(tournament_id):
            guild["tournaments"].append(tournament_id)
            save_guilds()
            return true
    return false

func process_tournament_results(tournament_id: String, rankings: Array) -> bool:
    for entry in rankings:
        var guild_name = entry["guild_name"]
        var rank = entry["rank"]
        if data["guilds"].has(guild_name):
            var guild = data["guilds"][guild_name]
            if guild.has("tournaments") and guild["tournaments"].has(tournament_id):
                if rank == 1:
                    if not guild.has("titles"):
                        guild["titles"] = []
                    guild["titles"].append("Tournament Champion")
                    if not guild.has("cosmetic_auras"):
                        guild["cosmetic_auras"] = []
                    guild["cosmetic_auras"].append("Champion Aura")
                    if not guild.has("prestige_pool"):
                        guild["prestige_pool"] = 0
                    guild["prestige_pool"] += 10000
                elif rank <= 3:
                    if not guild.has("titles"):
                        guild["titles"] = []
                    guild["titles"].append("Tournament Finalist")
                    if not guild.has("prestige_pool"):
                        guild["prestige_pool"] = 0
                    guild["prestige_pool"] += 5000
                elif rank <= 10:
                    if not guild.has("prestige_pool"):
                        guild["prestige_pool"] = 0
                    guild["prestige_pool"] += 1000
    save_guilds()
    return true

func get_guild_buffs(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        return data["guilds"][guild_name]["buffs"]
    return {"bonus_hp": 0, "bonus_speed": 0, "bonus_damage": 0}

func record_gvg_match(guild1_name: String, guild2_name: String, winner_name: String) -> bool:
    if data["guilds"].has(guild1_name) and data["guilds"].has(guild2_name):
        if winner_name == guild1_name:
            data["guilds"][guild1_name]["gvg_points"] += 10
            data["guilds"][guild1_name]["guild_xp"] += 50
            data["guilds"][guild2_name]["gvg_points"] = max(0, data["guilds"][guild2_name]["gvg_points"] - 5)
            data["guilds"][guild2_name]["guild_xp"] += 10
        elif winner_name == guild2_name:
            data["guilds"][guild2_name]["gvg_points"] += 10
            data["guilds"][guild2_name]["guild_xp"] += 50
            data["guilds"][guild1_name]["gvg_points"] = max(0, data["guilds"][guild1_name]["gvg_points"] - 5)
            data["guilds"][guild1_name]["guild_xp"] += 10
        save_guilds()
        return true
    return false

func unlock_perk(guild_name: String, perk_name: String, cost: int, required_perk: String = "") -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild["guild_xp"] >= cost:
            if not guild.has("perks"):
                guild["perks"] = []
            if not guild["perks"].has(perk_name):
                if required_perk == "" or guild["perks"].has(required_perk):
                    guild["guild_xp"] -= cost
                    guild["perks"].append(perk_name)
                    save_guilds()
                    return true
    return false

func get_guild_perks(guild_name: String) -> Array:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("perks"):
            return guild["perks"]
    return []

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

func record_boss_damage(guild_name: String, damage: float, week_id: String, tier: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("boss_progress"):
            guild["boss_progress"] = {}
        if not guild["boss_progress"].has(week_id):
            guild["boss_progress"][week_id] = {}
        if guild["boss_progress"][week_id].has("damage_dealt"):
            var old = guild["boss_progress"][week_id]
            guild["boss_progress"][week_id] = {"1": old}
        var tier_str = str(tier)
        if not guild["boss_progress"][week_id].has(tier_str):
            guild["boss_progress"][week_id][tier_str] = {"damage_dealt": 0.0, "claimed_by": []}
        guild["boss_progress"][week_id][tier_str]["damage_dealt"] += damage
        save_guilds()
        return true
    return false

func check_boss_defeated(guild_name: String, week_id: String, required_damage: float, tier: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("boss_progress") and guild["boss_progress"].has(week_id):
            var progress = guild["boss_progress"][week_id]
            if progress.has("damage_dealt"):
                progress = {"1": progress}
            var tier_str = str(tier)
            if progress.has(tier_str):
                return progress[tier_str]["damage_dealt"] >= required_damage
    return false

func claim_boss_reward(guild_name: String, player_id: String, week_id: String, required_damage: float, tier: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("boss_progress") and guild["boss_progress"].has(week_id):
            var progress = guild["boss_progress"][week_id]
            if progress.has("damage_dealt"):
                progress = {"1": progress}
                guild["boss_progress"][week_id] = progress
            var tier_str = str(tier)
            if progress.has(tier_str):
                var tier_prog = progress[tier_str]
                if tier_prog["damage_dealt"] >= required_damage and not tier_prog["claimed_by"].has(player_id):
                    tier_prog["claimed_by"].append(player_id)
                    var reward_amount = 100 * tier
                    if not guild.has("resources"):
                        guild["resources"] = 0
                    guild["resources"] += reward_amount
                    save_guilds()
                    return true
    return false

func unlock_hq_feature(guild_name: String, feature_type: String, feature_id: String, cost: int, required_level: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var current_level = 1
        if guild.has("level"):
            current_level = guild["level"]
        if guild["resources"] >= cost and current_level >= required_level:
            if not guild.has("hq"):
                guild["hq"] = {"statues": [], "banners": [],
            "cosmetics": [], "training_arena_unlocked": false}

            if feature_type == "training_arena":
                if not guild["hq"]["training_arena_unlocked"]:
                    guild["resources"] -= cost
                    guild["hq"]["training_arena_unlocked"] = true
                    save_guilds()
                    return true
            elif feature_type in ["statues", "banners", "cosmetics"]:
                if not guild["hq"].has(feature_type):
                    guild["hq"][feature_type] = []
                if not guild["hq"][feature_type].has(feature_id):
                    guild["resources"] -= cost
                    guild["hq"][feature_type].append(feature_id)
                    save_guilds()
                    return true
            elif feature_type == "mini_games":
                if not guild["hq"].has("mini_games"):
                    guild["hq"]["mini_games"] = {}
                if not guild["hq"]["mini_games"].has(feature_id):
                    guild["resources"] -= cost
                    guild["hq"]["mini_games"][feature_id] = {"high_scores": {}}
                    save_guilds()
                    return true
    return false

func record_mini_game_score(guild_name: String, mini_game_id: String, player_id: String, score: float) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("hq") and guild["hq"].has("mini_games") and guild["hq"]["mini_games"].has(mini_game_id):
            var mini_game = guild["hq"]["mini_games"][mini_game_id]
            if not mini_game.has("high_scores"):
                mini_game["high_scores"] = {}
            var high_scores = mini_game["high_scores"]
            var current_score = 0.0
            if high_scores.has(player_id):
                current_score = high_scores[player_id]

            if score > current_score:
                high_scores[player_id] = score
                save_guilds()
                return true
    return false

func get_mini_game_leaderboard(guild_name: String, mini_game_id: String) -> Array:
    var scores = []
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("hq") and guild["hq"].has("mini_games") and guild["hq"]["mini_games"].has(mini_game_id):
            var mini_game = guild["hq"]["mini_games"][mini_game_id]
            if mini_game.has("high_scores"):
                var high_scores = mini_game["high_scores"]
                for player_id in high_scores.keys():
                    scores.append({"player_id": player_id, "score": high_scores[player_id]})

                scores.sort_custom(func(a, b): return a["score"] > b["score"])
    return scores

func get_hq_status(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var hq = {"statues": [], "banners": [], "cosmetics": [], "mini_games": {}, "training_arena_unlocked": false}
        if guild.has("hq"):
            if guild["hq"].has("statues"): hq["statues"] = guild["hq"]["statues"]
            if guild["hq"].has("banners"): hq["banners"] = guild["hq"]["banners"]
            if guild["hq"].has("cosmetics"): hq["cosmetics"] = guild["hq"]["cosmetics"]
            if guild["hq"].has("mini_games"): hq["mini_games"] = guild["hq"]["mini_games"]
            if guild["hq"].has("training_arena_unlocked"): hq["training_arena_unlocked"] = guild["hq"]["training_arena_unlocked"]
        return hq
    return {}
