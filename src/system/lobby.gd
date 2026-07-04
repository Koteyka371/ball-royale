class_name PreGameLobby
extends RefCounted

var selections = {}

var daily_quests = [
    {"description": "Survive for 5 minutes", "reward": 50},
    {"description": "Defeat 10 enemies with sniper ball", "reward": 100},
    {"description": "Heal allies for 500 HP", "reward": 75},
    {"description": "Win a Battle Royale match", "reward": 200},
    {"description": "Deal 1000 damage in a single match", "reward": 150}
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
