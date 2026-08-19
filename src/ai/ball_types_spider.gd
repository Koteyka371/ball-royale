# Auto-generated ball type: Spider
extends Reference

const BALL_TYPE = "spider"
const HP = 80
const SPEED = 4.0
const DAMAGE = 20
const RADIUS = 9
const PERCEPTION_RADIUS = 300
const AGGRESSION = 0.5
const COLOR = "black"

var id: int
var hp: float
var max_hp: float
var x: float
var y: float
var alive: bool = true
var kills: int = 0
var current_action: String = "idle"
var web_drop_timer: float = 0.0
var first_hit_taken: bool = false
var personality = "cautious"
var radiation_duration: float = 0.0
var radiation_multiplier: float = 1.5

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	self.id = ball_id
	self.hp = float(HP)
	self.max_hp = float(HP)
	self.x = start_x
	self.y = start_y

func get_hp_percent() -> float:
	return hp / max_hp if max_hp > 0 else 0.0

func flee(delta: float) -> void:
	current_action = "wall_crawl"

func attack(delta: float) -> void:
	current_action = "wall_crawl"

func defend(delta: float) -> void:
	current_action = "wall_crawl"

func collect_booster(delta: float) -> void:
	current_action = "opportunistic"

func idle(delta: float) -> void:
	current_action = "idle"

func take_damage(amount: float) -> void:
	if radiation_duration > 0:
		amount *= radiation_multiplier

	if hp == max_hp and amount > 0:
		first_hit_taken = true
	hp -= amount
	if hp <= 0:
		alive = false
