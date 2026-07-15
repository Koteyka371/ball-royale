class_name TimeMage

const BALL_TYPE = "time_mage"
const HP = 90.0
const SPEED = 4.5
const DAMAGE = 8.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.4
const COLOR = "blue"
const SKILL = "time_rewind_self"
const SKILL_COOLDOWN = 20.0

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
	if self.max_hp > 0:
		return self.hp / self.max_hp
	return 0.0

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
	if self.hp <= 0:
		self.alive = false

func use_skill() -> bool:
	if self.skill_timer <= 0:
		self.skill_timer = SKILL_COOLDOWN
		return true
	return false

func _to_string() -> String:
	return "%s#%d HP=%.1f/%.1f [%s]" % [BALL_TYPE, self.id, self.hp, self.max_hp, self.current_action]
