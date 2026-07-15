# Auto-generated ball type: Leech

extends RefCounted
class_name Leech

const BALL_TYPE = "leech"
const HP = 80.0
const SPEED = 3.5
const DAMAGE = 2.0
const RADIUS = 12.0
const PERCEPTION_RADIUS = 250.0
const AGGRESSION = 0.8
const COLOR = Color("purple")
const SKILL = "leech_tether"
const SKILL_COOLDOWN = 6.0
const ATTACK_RANGE = 25.0

var id: int
var hp: float
var max_hp: float
var x: float
var y: float
var alive: bool
var kills: int
var first_hit_taken: bool
var current_action: String
var skill_timer: float
var attack_timer: float
var attack_range: float
var team: String = ""
var speed: float
var damage: float
var radius: float
var leech_tether_timer: float
var leech_tether_target

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	self.id = ball_id
	self.hp = HP
	self.max_hp = HP
	self.x = start_x
	self.y = start_y
	self.alive = true
	self.kills = 0
	self.first_hit_taken = false
	self.current_action = "idle"
	self.skill_timer = 0.0
	self.attack_timer = 0.0
	self.attack_range = ATTACK_RANGE
	self.speed = SPEED
	self.damage = DAMAGE
	self.radius = RADIUS
	self.leech_tether_timer = 0.0
	self.leech_tether_target = null

func get_hp_percent() -> float:
	if self.max_hp > 0.0:
		return self.hp / self.max_hp
	return 0.0

func flee(delta: float, target = null) -> void:
	self.current_action = "flee"

func attack(delta: float, target = null) -> void:
	self.current_action = "attack"
	if target == null:
		return

	var dx = target.x - self.x
	var dy = target.y - self.y
	var dist_sq = dx * dx + dy * dy
	if dist_sq > 0.0001:
		var dist = sqrt(dist_sq)
		var nx = dx / dist
		var ny = dy / dist
		var step_size = self.speed * delta * 60.0

		self.x += nx * min(step_size, dist)
		self.y += ny * min(step_size, dist)

		var target_radius = 10.0
		if "radius" in target:
			target_radius = float(target.radius)
		elif typeof(target) != TYPE_DICTIONARY and target.has_method("has_meta") and target.has_meta("radius"):
			target_radius = float(target.get_meta("radius"))

		var rng = self.radius + target_radius + 5.0
		var new_dx = target.x - self.x
		var new_dy = target.y - self.y
		var new_dist = sqrt(new_dx * new_dx + new_dy * new_dy)

		if new_dist <= rng:
			if self.attack_timer <= 0.0:
				var spd = self.speed
				if spd <= 0.0:
					spd = 1.0
				self.attack_timer = max(0.2, 2.0 / spd)

func defend(delta: float) -> void:
	self.current_action = "defend"

func collect_booster(delta: float) -> void:
	self.current_action = "opportunistic"

func idle(delta: float) -> void:
	self.current_action = "idle"

func take_damage(amount: float) -> void:
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

	if self.hp == self.max_hp and amount > 0.0:
		self.first_hit_taken = true
	self.hp -= amount
	if self.hp <= 0.0:
		self.alive = false

func use_skill() -> bool:
	if self.skill_timer <= 0.0:
		self.skill_timer = SKILL_COOLDOWN
		return true
	return false

func _to_string() -> String:
	return BALL_TYPE + "#" + str(self.id) + " HP=" + str(self.hp) + "/" + str(self.max_hp) + " [" + self.current_action + "]"
