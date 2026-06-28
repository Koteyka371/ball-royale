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
    if variant in ["normal", "poison", "stun", "ricochet", "emp"]:
        selections[ball_id] = variant

func get_trap_variant(ball_id: int) -> String:
    if selections.has(ball_id):
        return selections[ball_id]
    return "normal"

# Static global instance
static var instance: PreGameLobby

static func get_instance() -> PreGameLobby:
    if instance == null:
        instance = PreGameLobby.new()
    return instance
