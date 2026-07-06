extends RefCounted

const BALL_TYPE = "tracker"
const HP = 85.0
const SPEED = 8.0
const DAMAGE = 10.0
const RADIUS = 9.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.5
const COLOR = "cyan"
const SKILL = "sonar_ping"
const SKILL_COOLDOWN = 12.0

var id: int
var hp: float
var max_hp: float
var x: float
var y: float
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var sonar_ping_timer: float = 0.0
var personality_type: String = "curious"

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	self.id = ball_id
	self.hp = float(HP)
	self.max_hp = float(HP)
	self.x = start_x
	self.y = start_y
	self.alive = true
	self.kills = 0
	self.first_hit_taken = false
	self.current_action = "idle"
	self.skill_timer = 0.0
	self.sonar_ping_timer = 0.0
	self.personality_type = "curious"

func get_hp_percent() -> float:
	if self.max_hp > 0.0:
		return self.hp / self.max_hp
	return 0.0

func flee(_delta: float) -> void:
	self.current_action = "flee"

func attack(_delta: float) -> void:
	self.current_action = "attack"

func defend(_delta: float) -> void:
	self.current_action = "defend"

func collect_booster(_delta: float) -> void:
	self.current_action = "opportunistic"

func idle(_delta: float) -> void:
	self.current_action = "idle"

func take_damage(amount: float) -> void:
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
	return BALL_TYPE + "#" + str(self.id) + " HP=" + str(self.hp) + "/" + str(self.max_hp) + " [" + self.current_action + "]"
