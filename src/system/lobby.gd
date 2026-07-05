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
    {"description": "Play 3 matches in the current weekly mutator mode", "reward": {"skill_points": 250, "cosmetic": "mutator_badge"}}
]

func get_daily_quests() -> Array:
    var quests = daily_quests.duplicate()
    quests.shuffle()
    var result = []
    for i in range(min(3, quests.size())):
        result.append(quests[i])
    return result

func assign_daily_quests_to_profile(profile) -> void:
    var quests = get_daily_quests()
    for quest in quests:
        profile.add_quest(quest["description"], quest["reward"])

func select_trap_variant(ball_id: int, variant: String) -> void:
    if variant in ["normal", "poison", "stun", "ricochet", "emp", "hologram", "chain_lightning", "decoy", "blindness"]:
        selections[ball_id] = variant

func get_trap_variant(ball_id: int) -> String:
    if selections.has(ball_id):
        return selections[ball_id]
    return "normal"

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

func get_perks(ball_id: int) -> Array:
    var key = str(ball_id) + "_perks"
    if selections.has(key):
        return selections[key]
    return []


func apply_loadout_to_ball(ball_id: int, profile: ProfileManager, loadout_name: String) -> bool:
    var loadout = profile.get_loadout(loadout_name)
    if not loadout.is_empty():
        var trap = loadout.get("trap_variant", "normal")
        select_trap_variant(ball_id, trap)
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
        return true
    return false

func apply_random_loadout(ball_id: int, profile: ProfileManager) -> bool:
    var unlocked_balls = profile.data.get("unlocked_balls", ["basic"])
    if unlocked_balls.is_empty():
        unlocked_balls = ["basic"]

    var ball_type = unlocked_balls[randi() % unlocked_balls.size()]
    var trap_variants = ["normal", "poison", "stun", "ricochet", "emp", "hologram", "chain_lightning", "decoy", "mine"]
    var trap_variant = trap_variants[randi() % trap_variants.size()]

    select_trap_variant(ball_id, trap_variant)
    selections[str(ball_id) + "_ball_type"] = ball_type

    # Add random loadout challenge quest
    profile.add_quest("Win a match using a Random Loadout", 300)

    return true

func apply_default_loadout(ball_id: int, profile: ProfileManager) -> bool:
    var default_loadout = profile.get_default_loadout()
    if default_loadout != "":
        return apply_loadout_to_ball(ball_id, profile, default_loadout)
    return false

# Static global instance
static var instance: PreGameLobby

static func get_instance() -> PreGameLobby:
    if instance == null:
        instance = PreGameLobby.new()
    return instance
