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
                        "flags": [],
                        "backgrounds": [],
                        "announcer_voices": [],
                        "mini_games": {},
                        "training_arena_unlocked": false
                    }
                elif not data["guilds"][g_name]["hq"].has("mini_games"):
                    data["guilds"][g_name]["hq"]["mini_games"] = {}

                if not data["guilds"][g_name].has("guild_xp"):
                    data["guilds"][g_name]["guild_xp"] = 0
                if not data["guilds"][g_name].has("perks"):
                    data["guilds"][g_name]["perks"] = []
                if not data["guilds"][g_name].has("active_abilities"):
                    data["guilds"][g_name]["active_abilities"] = []
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
                if not data["guilds"][g_name].has("allies"):
                    data["guilds"][g_name]["allies"] = []
            return

    data = {"guilds": {}, "territories": {}}

func save_guilds():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))


func pool_mutator_tokens(guild_name: String, amount: int, profile) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var current_tokens = 0
        if profile.data.has("mutator_tokens"):
            current_tokens = profile.data["mutator_tokens"]

        if current_tokens >= amount:
            profile.data["mutator_tokens"] = current_tokens - amount
            if profile.has_method("save_profile"):
                profile.save_profile()

            if not guild.has("mutator_token_pool"):
                guild["mutator_token_pool"] = 0
            guild["mutator_token_pool"] += amount
            save_guilds()
            return true
    return false

func cast_gvg_mutator_vote(guild_name: String, mutator: String, tokens_to_spend: int) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var pool = 0
        if guild.has("mutator_token_pool"):
            pool = guild["mutator_token_pool"]

        if pool >= tokens_to_spend:
            guild["mutator_token_pool"] = pool - tokens_to_spend

            if not guild.has("gvg_mutator_votes"):
                guild["gvg_mutator_votes"] = {}

            var current_votes = 0
            if guild["gvg_mutator_votes"].has(mutator):
                current_votes = guild["gvg_mutator_votes"][mutator]

            guild["gvg_mutator_votes"][mutator] = current_votes + tokens_to_spend
            save_guilds()
            return true
    return false

func get_gvg_match_mutator(guild1_name: String, guild2_name: String) -> String:
    var votes = {}

    var check_guilds = [guild1_name, guild2_name]
    for g_name in check_guilds:
        if data["guilds"].has(g_name):
            var guild = data["guilds"][g_name]
            if guild.has("gvg_mutator_votes"):
                var g_votes = guild["gvg_mutator_votes"]
                for mutator in g_votes.keys():
                    if not votes.has(mutator):
                        votes[mutator] = 0
                    votes[mutator] += g_votes[mutator]

    if votes.is_empty():
        var options = ["low_gravity", "double_damage", "high_speed", "vampirism", "global_hp", "global_cooldown", "invisible_hazards", "kinetic_ghost"]
        return options[randi() % options.size()]

    var max_votes = -1
    var winning_mutator = ""
    for mutator in votes.keys():
        if votes[mutator] > max_votes:
            max_votes = votes[mutator]
            winning_mutator = mutator

    return winning_mutator

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
        "active_abilities": [],
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
        "unlocked_emblem_parts": {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]},
        "allies": []
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

func unlock_perk(guild_name: String, perk_name: String, cost: int, required_perk: String = "", required_level: int = 1, currency: String = "guild_xp") -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var current_level = 1
        if guild.has("level"):
            current_level = guild["level"]

        if current_level >= required_level:
            if guild.has(currency) and guild[currency] >= cost:
                if not guild.has("perks"):
                    guild["perks"] = []
                if not guild.has("active_abilities"):
                    guild["active_abilities"] = []
                if not guild["perks"].has(perk_name):
                    if required_perk == "" or guild["perks"].has(required_perk):
                        guild[currency] -= cost
                        guild["perks"].append(perk_name)
                        save_guilds()
                        return true
    return false

func buy_active_ability(guild_name: String, ability_name: String, cost: int, currency: String = "resources") -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has(currency) and guild[currency] >= cost:
            if not guild.has("active_abilities"):
                guild["active_abilities"] = []
            if not guild["active_abilities"].has(ability_name):
                guild[currency] -= cost
                guild["active_abilities"].append(ability_name)
                save_guilds()
                return true
    return false

func get_active_abilities(guild_name: String) -> Array:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("active_abilities"):
            return guild["active_abilities"]
    return []

func deploy_active_ability(guild_name: String, ability_name: String) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("active_abilities") and guild["active_abilities"].has(ability_name):
            guild["active_abilities"].erase(ability_name)
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

    var incomes = {}
    for territory in data["territories"].keys():
        var owner = data["territories"][territory]
        if data["guilds"].has(owner):
            if incomes.has(owner):
                incomes[owner] += 5
            else:
                incomes[owner] = 5

            var allies = []
            if data["guilds"][owner].has("allies"):
                allies = data["guilds"][owner]["allies"]

            for ally in allies:
                if data["guilds"].has(ally):
                    if incomes.has(ally):
                        incomes[ally] += 2
                    else:
                        incomes[ally] = 2

    for guild_name in incomes.keys():
        var amount = incomes[guild_name]
        var guild = data["guilds"][guild_name]
        var pay_taxes_to = []
        if guild.has("pay_taxes_to"):
            pay_taxes_to = guild["pay_taxes_to"]

        if pay_taxes_to.size() > 0:
            var tax_rate = 0.5
            var tax_amount = int(amount * tax_rate)
            amount -= tax_amount

            var tax_per_winner = tax_amount / pay_taxes_to.size()
            for winner in pay_taxes_to:
                if data["guilds"].has(winner):
                    data["guilds"][winner]["resources"] += tax_per_winner

        data["guilds"][guild_name]["resources"] += amount

    save_guilds()

func declare_war(guild1_name: String, guild2_name: String) -> bool:
    if data["guilds"].has(guild1_name) and data["guilds"].has(guild2_name) and guild1_name != guild2_name:
        break_alliance(guild1_name, guild2_name)

        var guild1 = data["guilds"][guild1_name]
        var guild2 = data["guilds"][guild2_name]

        if not guild1.has("wars"): guild1["wars"] = []
        if not guild2.has("wars"): guild2["wars"] = []

        if not guild1["wars"].has(guild2_name) and not guild2["wars"].has(guild1_name):
            guild1["wars"].append(guild2_name)
            guild2["wars"].append(guild1_name)
            save_guilds()
            return true
    return false

func end_war(winner_name: String, loser_name: String) -> bool:
    if data["guilds"].has(winner_name) and data["guilds"].has(loser_name):
        var winner = data["guilds"][winner_name]
        var loser = data["guilds"][loser_name]

        var modified = false
        if winner.has("wars") and winner["wars"].has(loser_name):
            winner["wars"].erase(loser_name)
            modified = true
        if loser.has("wars") and loser["wars"].has(winner_name):
            loser["wars"].erase(winner_name)
            modified = true

        if modified:
            var territories_to_transfer = get_territories(loser_name)
            for t in territories_to_transfer:
                capture_territory(winner_name, t)

            if not loser.has("pay_taxes_to"):
                loser["pay_taxes_to"] = []
            if not loser["pay_taxes_to"].has(winner_name):
                loser["pay_taxes_to"].append(winner_name)

            save_guilds()
            return true
    return false

func form_alliance(guild1_name: String, guild2_name: String) -> bool:
    if data["guilds"].has(guild1_name) and data["guilds"].has(guild2_name) and guild1_name != guild2_name:
        var guild1 = data["guilds"][guild1_name]
        var guild2 = data["guilds"][guild2_name]

        if not guild1.has("allies"):
            guild1["allies"] = []
        if not guild2.has("allies"):
            guild2["allies"] = []

        if not guild1["allies"].has(guild2_name) and not guild2["allies"].has(guild1_name):
            guild1["allies"].append(guild2_name)
            guild2["allies"].append(guild1_name)
            save_guilds()
            return true
    return false

func break_alliance(guild1_name: String, guild2_name: String) -> bool:
    if data["guilds"].has(guild1_name) and data["guilds"].has(guild2_name):
        var guild1 = data["guilds"][guild1_name]
        var guild2 = data["guilds"][guild2_name]

        var modified = false
        if guild1.has("allies") and guild1["allies"].has(guild2_name):
            guild1["allies"].erase(guild2_name)
            modified = true
        if guild2.has("allies") and guild2["allies"].has(guild1_name):
            guild2["allies"].erase(guild1_name)
            modified = true

        if modified:
            save_guilds()
            return true
    return false

func _get_alliance_boss_damage(guild_name: String, week_id: String, tier_str: String) -> float:
    var total_damage = 0.0

    var get_damage = func(g_name):
        if data["guilds"].has(g_name):
            var guild = data["guilds"][g_name]
            if guild.has("boss_progress") and guild["boss_progress"].has(week_id):
                var progress = guild["boss_progress"][week_id]
                if progress.has("damage_dealt"):
                    progress = {"1": progress}
                if progress.has(tier_str):
                    return progress[tier_str]["damage_dealt"]
        return 0.0

    total_damage += get_damage.call(guild_name)

    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("allies"):
            for ally_name in guild["allies"]:
                total_damage += get_damage.call(ally_name)

    return total_damage

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
        var tier_str = str(tier)
        var total_damage = _get_alliance_boss_damage(guild_name, week_id, tier_str)
        return total_damage >= required_damage
    return false

func claim_boss_reward(guild_name: String, player_id: String, week_id: String, required_damage: float, tier: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var tier_str = str(tier)

        var total_damage = _get_alliance_boss_damage(guild_name, week_id, tier_str)
        if total_damage >= required_damage:
            if not guild.has("boss_progress"):
                guild["boss_progress"] = {}
            if not guild["boss_progress"].has(week_id):
                guild["boss_progress"][week_id] = {}

            var progress = guild["boss_progress"][week_id]
            if progress.has("damage_dealt"):
                progress = {"1": progress}
                guild["boss_progress"][week_id] = progress

            if not progress.has(tier_str):
                progress[tier_str] = {"damage_dealt": 0.0, "claimed_by": []}

            var tier_prog = progress[tier_str]
            if not tier_prog["claimed_by"].has(player_id):
                tier_prog["claimed_by"].append(player_id)
                var reward_amount = 100 * tier
                if not guild.has("resources"):
                    guild["resources"] = 0
                guild["resources"] += reward_amount
                save_guilds()
                return true
    return false

func unlock_hq_feature(guild_name: String, feature_type: String, feature_id: String, cost: int, required_level: int = 1, currency: String = "resources") -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var current_level = 1
        if guild.has("level"):
            current_level = guild["level"]

        if currency != "resources" and currency != "guild_xp":
            return false

        var current_currency = 0
        if guild.has(currency):
            current_currency = guild[currency]

        if current_currency >= cost and current_level >= required_level:
            if not guild.has("hq"):
                guild["hq"] = {"statues": [], "banners": [],
            "cosmetics": [], "flags": [], "backgrounds": [], "announcer_voices": [], "training_arena_unlocked": false}

            if feature_type == "training_arena":
                if not guild["hq"]["training_arena_unlocked"]:
                    guild[currency] -= cost
                    guild["hq"]["training_arena_unlocked"] = true
                    save_guilds()
                    return true
            elif feature_type in ["statues", "banners", "cosmetics", "flags", "backgrounds", "announcer_voices"]:
                if not guild["hq"].has(feature_type):
                    guild["hq"][feature_type] = []
                if not guild["hq"][feature_type].has(feature_id):
                    guild[currency] -= cost
                    guild["hq"][feature_type].append(feature_id)
                    save_guilds()
                    return true
            elif feature_type == "mini_games":
                if not guild["hq"].has("mini_games"):
                    guild["hq"]["mini_games"] = {}
                if not guild["hq"]["mini_games"].has(feature_id):
                    guild[currency] -= cost
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

func build_hq_defense(guild_name: String, defense_type: String, cost: int, amount: int = 1) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var current_resources = 0
        if guild.has("resources"):
            current_resources = guild["resources"]

        if current_resources >= cost:
            guild["resources"] = current_resources - cost
            if not guild.has("hq"):
                guild["hq"] = {"statues": [], "banners": [], "cosmetics": [], "flags": [], "backgrounds": [], "announcer_voices": [], "mini_games": {}, "defenses": {}, "training_arena_unlocked": false}
            if not guild["hq"].has("defenses"):
                guild["hq"]["defenses"] = {}

            var defenses = guild["hq"]["defenses"]
            if defenses.has(defense_type):
                defenses[defense_type] += amount
            else:
                defenses[defense_type] = amount

            save_guilds()
            return true
    return false

func get_hq_defenses(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("hq") and guild["hq"].has("defenses"):
            return guild["hq"]["defenses"]
    return {}

func record_siege_defense_broken(attacker_name: String, defender_name: String, stolen_amount: int) -> int:
    if data["guilds"].has(attacker_name) and data["guilds"].has(defender_name):
        var defender = data["guilds"][defender_name]
        var attacker = data["guilds"][attacker_name]

        var defender_resources = 0
        if defender.has("resources"):
            defender_resources = defender["resources"]

        var actual_stolen = min(defender_resources, stolen_amount)
        if actual_stolen > 0:
            defender["resources"] -= actual_stolen

            var attacker_resources = 0
            if attacker.has("resources"):
                attacker_resources = attacker["resources"]
            attacker["resources"] = attacker_resources + actual_stolen

            save_guilds()
        return actual_stolen
    return 0

func record_siege_held(defender_name: String, xp_reward: int) -> bool:
    if data["guilds"].has(defender_name):
        var defender = data["guilds"][defender_name]
        var current_xp = 0
        if defender.has("guild_xp"):
            current_xp = defender["guild_xp"]
        defender["guild_xp"] = current_xp + xp_reward
        save_guilds()
        return true
    return false

func get_hq_status(guild_name: String) -> Dictionary:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        var hq = {"statues": [], "banners": [], "cosmetics": [], "flags": [], "backgrounds": [], "announcer_voices": [], "mini_games": {}, "defenses": {}, "training_arena_unlocked": false, "layout": {}, "hall_of_fame": []}
        if guild.has("hq"):
            if guild["hq"].has("statues"): hq["statues"] = guild["hq"]["statues"]
            if guild["hq"].has("banners"): hq["banners"] = guild["hq"]["banners"]
            if guild["hq"].has("cosmetics"): hq["cosmetics"] = guild["hq"]["cosmetics"]
            if guild["hq"].has("flags"): hq["flags"] = guild["hq"]["flags"]
            if guild["hq"].has("backgrounds"): hq["backgrounds"] = guild["hq"]["backgrounds"]
            if guild["hq"].has("announcer_voices"): hq["announcer_voices"] = guild["hq"]["announcer_voices"]
            if guild["hq"].has("mini_games"): hq["mini_games"] = guild["hq"]["mini_games"]
            if guild["hq"].has("defenses"): hq["defenses"] = guild["hq"]["defenses"]
            if guild["hq"].has("training_arena_unlocked"): hq["training_arena_unlocked"] = guild["hq"]["training_arena_unlocked"]
            if guild["hq"].has("layout"): hq["layout"] = guild["hq"]["layout"]
            if guild["hq"].has("hall_of_fame"): hq["hall_of_fame"] = guild["hq"]["hall_of_fame"]
        return hq
    return {}

func arrange_hq_item(guild_name: String, item_type: String, item_id: String, position_x: float, position_y: float) -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("hq"):
            guild["hq"] = {"statues": [], "banners": [], "cosmetics": [], "flags": [], "backgrounds": [], "announcer_voices": [], "mini_games": {}, "defenses": {}, "training_arena_unlocked": false, "layout": {}, "hall_of_fame": []}
        if not guild["hq"].has("layout"):
            guild["hq"]["layout"] = {}
        if not guild["hq"]["layout"].has(item_type):
            guild["hq"]["layout"][item_type] = {}

        guild["hq"]["layout"][item_type][item_id] = {"x": position_x, "y": position_y}
        save_guilds()
        return true
    return false

func add_to_hall_of_fame(guild_name: String, player_id: String, category: String, value: float, description: String = "") -> bool:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if not guild.has("hq"):
            guild["hq"] = {"statues": [], "banners": [], "cosmetics": [], "flags": [], "backgrounds": [], "announcer_voices": [], "mini_games": {}, "defenses": {}, "training_arena_unlocked": false, "layout": {}, "hall_of_fame": []}
        if not guild["hq"].has("hall_of_fame"):
            guild["hq"]["hall_of_fame"] = []

        guild["hq"]["hall_of_fame"].append({
            "player_id": player_id,
            "category": category,
            "value": value,
            "description": description
        })

        # In GDScript, a custom sorter function is required for Array.sort_custom
        # Since we're mimicking dictionary, we might just leave it unsorted or do bubble sort for simplicity
        var hof = guild["hq"]["hall_of_fame"]
        var n = hof.size()
        for i in range(n):
            for j in range(0, n - i - 1):
                if hof[j].get("value", 0) < hof[j + 1].get("value", 0):
                    var temp = hof[j]
                    hof[j] = hof[j + 1]
                    hof[j + 1] = temp

        save_guilds()
        return true
    return false

func get_hall_of_fame(guild_name: String) -> Array:
    if data["guilds"].has(guild_name):
        var guild = data["guilds"][guild_name]
        if guild.has("hq") and guild["hq"].has("hall_of_fame"):
            return guild["hq"]["hall_of_fame"]
    return []
