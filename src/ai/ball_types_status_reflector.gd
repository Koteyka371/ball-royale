class_name StatusReflector

# Auto-generated ball type: Status Reflector
# A ball that perfectly reflects any negative status effect (like EMP or poison) back to the hazard source (destroying it) or directly to the attacker, but is highly vulnerable to pure kinetic damage.

const BALL_TYPE = "status_reflector"
const HP = 80
const SPEED = 4.0
const DAMAGE = 10
const RADIUS = 12
const PERCEPTION_RADIUS = 300
const AGGRESSION = 0.2
const COLOR = "mirror_finish"
const SKILL = "status_reflect"
const SKILL_COOLDOWN = 12.0
const ATTACK_RANGE = 20.0

var id: int
var hp: float
var max_hp: float
var x: float
var y: float
var radius: float
var alive: bool
var kills: int
var first_hit_taken: bool
var current_action: String
var skill_timer: float
var attack_timer: float
var attack_range: float

var is_stunned: bool
var stun_timer: float
var poison_timer: float
var blindness_timer: float
var slow_timer: float
var frozen_timer: float
var burn_timer: float
var emp_immunity_timer: float

var status_reflect_active: bool
var vulnerable_to_kinetic: bool

var _metadata = {}
func set_meta(key, value):
	_metadata[key] = value

func get_meta(key, default_val=null):
	return _metadata.get(key, default_val)

func has_meta(key):
	return _metadata.has(key)

func _init(ball_id: int = 0, px: float = 0.0, py: float = 0.0):
	self.id = ball_id
	self.hp = float(HP)
	self.max_hp = float(HP)
	self.x = px
	self.y = py
	self.radius = float(RADIUS)
	self.alive = true
	self.kills = 0
	self.first_hit_taken = false
	self.current_action = "idle"
	self.skill_timer = 0.0
	self.attack_timer = 0.0
	self.attack_range = float(ATTACK_RANGE)

	self.is_stunned = false
	self.stun_timer = 0.0
	self.poison_timer = 0.0
	self.blindness_timer = 0.0
	self.slow_timer = 0.0
	self.frozen_timer = 0.0
	self.burn_timer = 0.0
	self.emp_immunity_timer = 0.0

	self.status_reflect_active = true
	self.vulnerable_to_kinetic = true

	set_meta("personality", "defensive")

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
		var arange = RADIUS + target_radius + 5.0

		var new_dx = target.x - x
		var new_dy = target.y - y
		var new_dist_sq = new_dx * new_dx + new_dy * new_dy
		var new_dist = sqrt(new_dist_sq) if new_dist_sq > 0.0001 else 0.0

		if new_dist <= arange:
			if attack_timer <= 0:
				attack_timer = max(0.2, 2.0 / SPEED if SPEED > 0 else 1.0)

func defend(delta: float) -> void:
	current_action = "defend"

func collect_booster(delta: float) -> void:
	current_action = "opportunistic"

func idle(delta: float) -> void:
	current_action = "idle"

func take_damage(amount: float) -> void:
	if vulnerable_to_kinetic:
		amount *= 2.0

	var radiation_duration = get_meta("radiation_duration", 0.0)
	if radiation_duration > 0:
		amount *= get_meta("radiation_multiplier", 1.5)

	if hp == max_hp and amount > 0:
		first_hit_taken = true
	hp -= amount
	if hp <= 0:
		alive = false

func tick(delta: float) -> void:
	if not alive:
		return

func use_skill() -> bool:
	if skill_timer <= 0:
		skill_timer = SKILL_COOLDOWN
		return true
	return false
