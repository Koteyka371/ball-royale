class_name PreGameLobby
extends RefCounted

var selections = {}

var daily_quests = [
    {"description": "Survive for 5 minutes", "reward": {"skill_points": 50, "material": "Iron Ore", "material_amount": 2}},
    {"description": "Defeat 10 enemies with sniper ball", "reward": 100},
    {"description": "Heal allies for 500 HP", "reward": 75},
    {"description": "Win a Battle Royale match", "reward": {"skill_points": 200, "cosmetic": "winner_crown"}},
    {"description": "Deal 1000 damage in a single match", "reward": 150},
    {"description": "Deal 10,000 damage", "reward": {"skill_points": 300, "prestige_tokens": 1}},
    {"description": "Play 3 matches in the current weekly mutator mode", "reward": {"skill_points": 250, "cosmetic": "mutator_badge"}},
    {"description": "Get 50 kills in a single match", "reward": {"mutator_tokens": 1}},
]

func get_daily_quests(current_date_str: String = "") -> Array:
    var quests = daily_quests.duplicate()
    quests.shuffle()
    var result = []
    for i in range(min(3, quests.size())):
        result.append(quests[i])

    var is_weekend = false
    if current_date_str == "":
        var current_datetime = Time.get_datetime_dict_from_system()
        is_weekend = current_datetime.weekday == Time.WEEKDAY_SATURDAY or current_datetime.weekday == Time.WEEKDAY_SUNDAY
    else:
        var current_time = Time.get_unix_time_from_datetime_string(current_date_str + "T00:00:00")
        if current_time > 0:
            var current_datetime = Time.get_datetime_dict_from_unix_time(current_time)
            is_weekend = current_datetime.weekday == Time.WEEKDAY_SATURDAY or current_datetime.weekday == Time.WEEKDAY_SUNDAY

    if is_weekend:
        var weekend_quest = {"description": "Win a match with the active mutator", "reward": {"mutator_tokens": 5}}
        if result.size() > 0:
            result[0] = weekend_quest
        else:
            result.append(weekend_quest)

    return result

func assign_daily_quests_to_profile(profile, current_date_str: String = "") -> void:
    var quests = get_daily_quests(current_date_str)
    for quest in quests:
        profile.add_quest(quest["description"], quest["reward"])

func get_new_daily_quest(existing_quests: Array) -> Dictionary:
    var existing_descriptions = []
    for q in existing_quests:
        if q.has("description"):
            existing_descriptions.append(q["description"])

    var available_quests = []
    for q in daily_quests:
        if not existing_descriptions.has(q["description"]):
            available_quests.append(q)

    if available_quests.size() == 0:
        return daily_quests[randi() % daily_quests.size()]

    return available_quests[randi() % available_quests.size()]

func reroll_daily_quest(profile, quest_index: int) -> bool:
    if profile.data.has("mutator_tokens") and profile.data["mutator_tokens"] >= 1:
        var quests = profile.get_quests()
        if quest_index >= 0 and quest_index < quests.size():
            var new_quest = get_new_daily_quest(quests)
            quests[quest_index] = {
                "description": new_quest["description"],
                "reward": new_quest["reward"],
                "completed": false
            }
            profile.data["mutator_tokens"] -= 1
            profile.save_profile()
            return true
    return false

func select_trap_variant(ball_id: int, variant: String) -> void:
    if variant in ["normal", "poison", "stun", "ricochet", "emp", "hologram", "chain_lightning", "decoy", "blackout", "blindness", "shriek", "mine", "elemental_mine", "time_dilation_mine", "warp", "clone", "tar", "link", "repulsion", "swap", "reversal"]:
        selections[ball_id] = variant

func get_trap_variant(ball_id: int) -> String:
    if selections.has(ball_id):
        return selections[ball_id]
    return "normal"

func get_trap_level(ball_id: int) -> int:
    var key = str(ball_id) + "_trap_level"
    if selections.has(key):
        return selections[key]
    return 1

func select_perk(ball_id: int, perk: String) -> void:
    var key = str(ball_id) + "_perks"
    if not selections.has(key):
        selections[key] = []
    if selections[key].size() < 2 and not selections[key].has(perk):
        selections[key].append(perk)

func select_perks(ball_id: int, perks: Array) -> void:
    var key = str(ball_id) + "_perks"
    selections[key] = []
    for perk in perks:
        select_perk(ball_id, perk)

func select_traits(ball_id: int, traits: Array) -> void:
    var key = str(ball_id) + "_traits"
    selections[key] = []
    for trait in traits:
        if trait in ["swift", "slow", "sturdy", "fragile", "lethal", "weak", "soul_dropper", "quantum_entangled", "quantum_echo", "storm_chaser"]:
            selections[key].append(trait)

func get_traits(ball_id: int) -> Array:
    var key = str(ball_id) + "_traits"
    if selections.has(key):
        return selections[key]
    return []

func get_perks(ball_id: int) -> Array:
    var key = str(ball_id) + "_perks"
    if selections.has(key):
        return selections[key]
    return []



func get_mutator_options() -> Array:
    return ["low_gravity", "double_damage", "high_speed", "vampirism", "global_hp", "global_cooldown", "invisible_hazards", "kinetic_ghost", "bouncy_walls", "bouncy_payload", "sudden_death_event", "shifting_mirror_walls", "stamina_vampire", "frictionless_arena_modifier", "low_hp_swap_mutator", "invert_controls_mutator"]

func cast_mutator_vote(player_id: String, mutator: String, profile: ProfileManager, spend_currency: bool = false, currency_type: String = "skill_points") -> bool:
    if not selections.has("mutator_votes"):
        selections["mutator_votes"] = {}

    if not selections.has("player_voted_mutators"):
        selections["player_voted_mutators"] = []

    if selections["player_voted_mutators"].has(player_id):
        return false

    if not get_mutator_options().has(mutator):
        return false

    var vote_weight = 1

    if spend_currency:
        if currency_type == "skill_points":
            var current_points = profile.data.get("skill_points", 0)
            if current_points >= 50:
                profile.add_skill_points(-50)
                vote_weight = 3
            else:
                return false
        elif currency_type == "mutator_tokens":
            var current_tokens = profile.data.get("mutator_tokens", 0)
            if current_tokens >= 1:
                profile.data["mutator_tokens"] = current_tokens - 1
                profile.save_profile()
                vote_weight = 5
            else:
                return false
        else:
            return false

    var current_votes = 0
    if selections["mutator_votes"].has(mutator):
        current_votes = selections["mutator_votes"][mutator]

    selections["mutator_votes"][mutator] = current_votes + vote_weight
    selections["player_voted_mutators"].append(player_id)
    return true

func get_winning_mutator() -> String:
    if not selections.has("mutator_votes") or selections["mutator_votes"].is_empty():
        var opts = get_mutator_options()
        return opts[randi() % opts.size()]

    var votes = selections["mutator_votes"]
    var vote_list = []
    for mutator in votes.keys():
        vote_list.append({"mutator": mutator, "count": votes[mutator]})

    vote_list.sort_custom(func(a, b): return a["count"] > b["count"])

    if vote_list.size() >= 2:
        var top1 = vote_list[0]["mutator"]
        var top2 = vote_list[1]["mutator"]
        if (top1 == "high_speed" and top2 == "bouncy_walls") or (top1 == "bouncy_walls" and top2 == "high_speed"):
            return "pinball_mutator"

    return vote_list[0]["mutator"]

func apply_loadout_to_ball(ball_id: int, profile: ProfileManager, loadout_name: String) -> bool:
    var loadout = profile.get_loadout(loadout_name)
    if not loadout.is_empty():
        var trap = loadout.get("trap_variant", "normal")
        select_trap_variant(ball_id, trap)
        selections[str(ball_id) + "_trap_level"] = profile.get_trap_level(trap) if profile.has_method("get_trap_level") else 1
        if loadout.has("ball_type"):
            selections[str(ball_id) + "_ball_type"] = loadout["ball_type"]
        if loadout.has("preferred_bonuses"):
            selections[str(ball_id) + "_preferred_bonuses"] = loadout["preferred_bonuses"]
        if loadout.has("cosmetic") and loadout["cosmetic"] != "":
            selections[str(ball_id) + "_cosmetic"] = loadout["cosmetic"]
        if loadout.has("title") and loadout["title"] != "":
            selections[str(ball_id) + "_title"] = loadout["title"]
        if loadout.has("badge") and loadout["badge"] != "":
            selections[str(ball_id) + "_badge"] = loadout["badge"]
        if loadout.has("perks"):
            select_perks(ball_id, loadout["perks"])
        if loadout.has("traits"):
            select_traits(ball_id, loadout["traits"])
        return true
    return false

func apply_random_loadout(ball_id: int, profile: ProfileManager) -> bool:
    var unlocked_balls = profile.data.get("unlocked_balls", ["basic"])
    if unlocked_balls.is_empty():
        unlocked_balls = ["basic"]

    var ball_type = unlocked_balls[randi() % unlocked_balls.size()]
    var trap_variants = ["normal", "poison", "stun", "ricochet", "emp", "hologram", "chain_lightning", "decoy", "blackout", "mine", "elemental_mine", "warp", "siphon", "clone", "tar", "link", "web", "sticky_bomb", "swap", "reversal"]
    var trap_variant = trap_variants[randi() % trap_variants.size()]

    select_trap_variant(ball_id, trap_variant)
    selections[str(ball_id) + "_trap_level"] = profile.get_trap_level(trap_variant) if profile.has_method("get_trap_level") else 1
    selections[str(ball_id) + "_ball_type"] = ball_type

    # Add random loadout challenge quest
    profile.add_quest("Win a match using a Random Loadout", 300)

    return true

func apply_default_loadout(ball_id: int, profile: ProfileManager) -> bool:
    var default_loadout = profile.get_default_loadout()
    if default_loadout != "":
        return apply_loadout_to_ball(ball_id, profile, default_loadout)
    return false


func join_spectator_queue(player_id: String, target_match_id: String = "") -> bool:
    if not selections.has("spectator_queue"):
        selections["spectator_queue"] = []
    selections["spectator_queue"].append({"player_id": player_id, "match_id": target_match_id})
    return true

func get_spectators_for_match(match_id: String) -> Array:
    var result = []
    if not selections.has("spectator_queue"):
        return result
    for s in selections["spectator_queue"]:
        if s["match_id"] == match_id or s["match_id"] == "":
            result.append(s["player_id"])
    return result

# Static global instance
static var instance: PreGameLobby

static func get_instance() -> PreGameLobby:
    if instance == null:
        instance = PreGameLobby.new()
    return instance
