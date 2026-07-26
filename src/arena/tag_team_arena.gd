class_name TagTeamArena
extends ProceduralArena

var boundary_states: Dictionary = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
var boundary_health: Dictionary = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}
var swap_cooldown: float = 5.0
var team_cooldowns: Dictionary = {}
var last_tick: int = -1

func _init(_arena_size: float = 2000.0, _num_rooms: int = 5, _seed = null):
	super(_arena_size, _num_rooms, _seed)
	name = "Tag Team Arena"

func generate() -> void:
	super.generate()
	rooms.clear()
	corridors.clear()
	hazards.clear()
	team_cooldowns.clear()

func update_zone(current_tick: int, delta: float) -> void:
	super.update_zone(current_tick, delta)

	for team_id in team_cooldowns.keys():
		if team_cooldowns[team_id] > 0:
			team_cooldowns[team_id] -= delta
		if team_cooldowns[team_id] <= 0:
			team_cooldowns[team_id] = 0.0

func trigger_swap(team_id: int, ball1, ball2) -> bool:
	if not team_cooldowns.has(team_id) or team_cooldowns[team_id] <= 0:
		var temp_x = ball1.x if "x" in ball1 else (ball1["x"] if typeof(ball1) == TYPE_DICTIONARY else 0.0)
		var temp_y = ball1.y if "y" in ball1 else (ball1["y"] if typeof(ball1) == TYPE_DICTIONARY else 0.0)

		var b2_x = ball2.x if "x" in ball2 else (ball2["x"] if typeof(ball2) == TYPE_DICTIONARY else 0.0)
		var b2_y = ball2.y if "y" in ball2 else (ball2["y"] if typeof(ball2) == TYPE_DICTIONARY else 0.0)

		if typeof(ball1) == TYPE_DICTIONARY:
			ball1["x"] = b2_x
			ball1["y"] = b2_y
		else:
			ball1.x = b2_x
			ball1.y = b2_y

		if typeof(ball2) == TYPE_DICTIONARY:
			ball2["x"] = temp_x
			ball2["y"] = temp_y
		else:
			ball2.x = temp_x
			ball2.y = temp_y

		team_cooldowns[team_id] = swap_cooldown
		return true
	return false
