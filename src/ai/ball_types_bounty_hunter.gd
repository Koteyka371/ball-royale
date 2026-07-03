extends RefCounted
class_name BountyHunter

const BALL_TYPE = "bounty_hunter"
const HP = 85.0
const SPEED = 4.0
const DAMAGE = 25.0
const RADIUS = 9.0
const PERCEPTION_RADIUS = 350.0
const AGGRESSION = 0.7
const COLOR = "orange"
const SKILL = "target_lock"
const SKILL_COOLDOWN = 5.0

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
var personality: String = "cunning"

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	id = ball_id
	hp = HP
	max_hp = HP
	x = start_x
	y = start_y

func get_hp_percent() -> float:
	if max_hp > 0:
		return hp / max_hp
	return 0.0

func flee(_delta: float) -> void:
	current_action = "flee"

func attack(_delta: float) -> void:
	current_action = "attack"

func defend(_delta: float) -> void:
	current_action = "defend"

func collect_booster(_delta: float) -> void:
	current_action = "opportunistic"

func idle(_delta: float) -> void:
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
