class_name WindRider
extends Node

var BALL_TYPE = "wind_rider"
var HP = 85
var SPEED = 6.0
var DAMAGE = 15
var RADIUS = 10
var PERCEPTION_RADIUS = 400
var AGGRESSION = 0.6
var COLOR = "lightblue"
var SKILL = "wind_rider"
var SKILL_COOLDOWN = 3.5

var id = 0
var hp = 85.0
var max_hp = 85.0
var x = 0.0
var y = 0.0
var alive = true
var kills = 0
var first_hit_taken = false
var current_action = "idle"
var skill_timer = 0.0
var personality = null

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	self.id = ball_id
	self.x = start_x
	self.y = start_y

	var PersonalityClass = load("res://src/ai/personality.gd")
	if PersonalityClass:
		self.personality = PersonalityClass.new("curious")

func get_hp_percent() -> float:
	return self.hp / self.max_hp if self.max_hp > 0 else 0.0

func flee(delta: float) -> void:
	self.current_action = "flee"

func attack(delta: float) -> void:
	self.current_action = "attack"

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

func use_skill() -> bool:
	if self.skill_timer <= 0:
		self.skill_timer = self.SKILL_COOLDOWN
		return true
	return false
