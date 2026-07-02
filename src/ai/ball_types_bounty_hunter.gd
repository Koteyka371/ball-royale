extends RefCounted

const BALL_TYPE = "bounty_hunter"
const HP = 90.0
const SPEED = 5.0
const DAMAGE = 25.0
const RADIUS = 12.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.9
const COLOR = "orange"
const SKILL = "tracking_beacon"
const SKILL_COOLDOWN = 6.0

var id: int = 0
var hp: float = HP
var max_hp: float = HP
var damage: float = DAMAGE
var x: float = 0.0
var y: float = 0.0
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var personality

func _init(p_id: int = 0, p_x: float = 0.0, p_y: float = 0.0):
	id = p_id
	x = p_x
	y = p_y
	var PersonalityClass = load("res://src/ai/personality.gd")
	if PersonalityClass:
		personality = PersonalityClass.new("relentless")

func get_hp_percent() -> float:
	return hp / max_hp if max_hp > 0 else 0.0

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
	return "%s#%d HP=%.1f/%.1f [%s]" % [BALL_TYPE, id, hp, max_hp, current_action]
