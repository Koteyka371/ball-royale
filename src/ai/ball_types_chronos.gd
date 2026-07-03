extends RefCounted
class_name Chronos

const BALL_TYPE = "chronos"
const HP = 120.0
const SPEED = 5.0
const DAMAGE = 5.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 350.0
const AGGRESSION = 0.2
const COLOR = "purple"
const SKILL = "time_rewind"
const SKILL_COOLDOWN = 15.0

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
var damage: float
var state_history: Array

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
	self.damage = DAMAGE
	self.state_history = []

func get_hp_percent() -> float:
	if max_hp > 0:
		return hp / max_hp
	return 0.0

func flee(delta: float) -> void:
	current_action = "flee"

func attack(delta: float) -> void:
	current_action = "attack"

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
	return "%s#%d HP=%f/%f [%s]" % [BALL_TYPE, id, hp, max_hp, current_action]
