class_name PreGameLobby
extends RefCounted

var selections = {}

func select_trap_variant(ball_id: int, variant: String) -> void:
    if variant in ["normal", "poison", "stun"]:
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
