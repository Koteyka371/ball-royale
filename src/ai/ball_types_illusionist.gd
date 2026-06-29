extends RefCounted

const BALL_TYPE = "illusionist"
const HP = 85.0
const SPEED = 4.0
const DAMAGE = 14.0
const RADIUS = 9.0
const PERCEPTION_RADIUS = 270.0
const AGGRESSION = 0.6
const COLOR = "purple"
const SKILL = "deploy_static_decoy"
const SKILL_COOLDOWN = 4.0

var id: int
var hp: float
var max_hp: float
var x: float
var y: float
var alive: bool
var current_action: String
var skill_timer: float
var attack_timer: float
var kills: int
var first_hit_taken: bool
var base_speed: float
var base_damage: float
var difficulty: String

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	id = ball_id
	hp = HP
	max_hp = HP
	x = start_x
	y = start_y
	alive = true
	current_action = "idle"
	skill_timer = 0.0
	attack_timer = 0.0
	kills = 0
	first_hit_taken = false
	base_speed = SPEED
	base_damage = DAMAGE
	difficulty = "medium"

func get_hp_percent() -> float:
	if max_hp > 0:
		return hp / max_hp
	return 0.0

func flee(delta: float, target=null) -> void:
	current_action = "flee"

func attack(delta: float, target=null) -> void:
	current_action = "attack"
	if target == null:
		return

	var dx = target.x - x
	var dy = target.y - y
	var dist_sq = dx * dx + dy * dy
	if dist_sq > 0.0001:
		var dist = sqrt(dist_sq)
		var nx = dx / dist
		var ny = dy / dist
		var step = SPEED * delta * 60.0

		x += nx * min(step, dist)
		y += ny * min(step, dist)

		var target_radius = 10.0
		if "radius" in target:
			target_radius = target.radius
		var attack_range = RADIUS + target_radius + 5.0

		var new_dx = target.x - x
		var new_dy = target.y - y
		var new_dist_sq = new_dx * new_dx + new_dy * new_dy
		var new_dist = 0.0
		if new_dist_sq > 0.0001:
			new_dist = sqrt(new_dist_sq)

		if new_dist <= attack_range:
			if attack_timer <= 0:
				attack_timer = max(0.2, 2.0 / SPEED if SPEED > 0 else 1.0)

func defend(delta: float) -> void:
	current_action = "defend"

func collect_booster(delta: float) -> void:
	current_action = "opportunistic"

func idle(delta: float) -> void:
	current_action = "idle"

func take_damage(amount: float) -> void:
	if hp == max_hp and amount > 0:
		first_hit_taken = true
	hp -= amount
	if hp <= 0:
		alive = false

func use_skill() -> bool:
	if skill_timer <= 0:
		skill_timer = SKILL_COOLDOWN
		return true
	return false

func _to_string() -> String:
	return str(BALL_TYPE) + "#" + str(id) + " HP=" + str(hp) + "/" + str(max_hp) + " [" + str(current_action) + "]"
