const Personality = preload("res://src/ai/personality.gd")

const BALL_TYPE = "shuffler"
const HP = 75.0
const SPEED = 5.5
const DAMAGE = 15.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.5
const COLOR = "yellow"
const SKILL = "shuffler_clone"
const SKILL_COOLDOWN = 0.0

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
var shuffler_clone_timer: float
var personality

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	id = ball_id
	hp = HP
	max_hp = HP
	x = start_x
	y = start_y
	alive = true
	kills = 0
	first_hit_taken = false
	current_action = "idle"
	skill_timer = 0.0
	shuffler_clone_timer = 2.0
	personality = Personality.new("cunning")

func get_hp_percent() -> float:
	if max_hp > 0:
		return hp / max_hp
	return 0.0

func flee(delta: float, target=null) -> void:
	current_action = "flee"

func attack(delta: float, target=null) -> void:
	current_action = "attack"

func defend(delta: float) -> void:
	current_action = "defend"

func collect_booster(delta: float) -> void:
	current_action = "opportunistic"

func idle(delta: float) -> void:
	current_action = "idle"

func take_damage(amount: float) -> void:
	if "radiation_duration" in self and self.get("radiation_duration") > 0:
		amount *= self.get("radiation_multiplier", 1.5)

	if hp == max_hp and amount > 0:
		first_hit_taken = true
	hp -= amount
	if hp <= 0:
		alive = false

func use_skill() -> bool:
	return false
