class_name Alchemist extends RefCounted

const BALL_TYPE = "alchemist"
const HP = 90.0
const SPEED = 2.0
const DAMAGE = 15.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 200.0
const AGGRESSION = 0.5
const COLOR = Color(0.0, 0.4, 0.0)
const SKILL = "poison_nova"
const SKILL_COOLDOWN = 8.0

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
var personality = null
var team: String = ""
var speed_multiplier: float = 1.0

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

func get_hp_percent() -> float:
	if self.max_hp > 0:
		return self.hp / self.max_hp
	return 0.0

func take_damage(amount: float) -> void:
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

	if self.hp == self.max_hp and amount > 0:
		self.first_hit_taken = true
	self.hp -= amount

	if self.hp <= 0 and self.get("quantum_relay_timer") != null and self.get("quantum_relay_timer") > 0.0:
		self.hp = self.max_hp * 0.2
		self.x = self.get("quantum_relay_x") if self.get("quantum_relay_x") != null else self.x
		self.y = self.get("quantum_relay_y") if self.get("quantum_relay_y") != null else self.y
		self.set("quantum_relay_timer", 0.0)
		return

	if self.hp <= 0:
		self.alive = false


func flee(delta: float, target=null) -> void:
	self.current_action = "flee"

func attack(delta: float, target=null) -> void:
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
		var step = self.SPEED * delta * 60.0

		var speed_mult = self.speed_multiplier if "speed_multiplier" in self else 1.0
		self.x += nx * min(step * speed_mult, dist)
		self.y += ny * min(step * speed_mult, dist)

func defend(delta: float) -> void:
	self.current_action = "defend"

func collect_booster(delta: float) -> void:
	self.current_action = "collect_booster"

func idle(delta: float) -> void:
	self.current_action = "idle"

func use_skill() -> bool:
	if self.skill_timer <= 0:
		self.skill_timer = SKILL_COOLDOWN
		return true
	return false
