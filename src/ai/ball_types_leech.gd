class_name Leech
const BALL_TYPE = "leech"
const HP = 100
const SPEED = 2.0
const DAMAGE = 5
const RADIUS = 12
const PERCEPTION_RADIUS = 200
const AGGRESSION = 0.9
const COLOR = Color(0.5, 0.0, 0.5)
const SKILL = "tether"
const SKILL_COOLDOWN = 10.0
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
var attack_timer: float = 0.0
var leech_tether_target_id = null
var personality

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    id = ball_id
    hp = float(HP)
    max_hp = float(HP)
    x = start_x
    y = start_y

func get_hp_percent() -> float:
    if max_hp > 0: return hp / max_hp
    return 0.0

func flee(delta: float, target = null) -> void:
    current_action = "flee"

func attack(delta: float, target = null) -> void:
    current_action = "attack"

func defend(delta: float) -> void:
    current_action = "defend"

func collect_booster(delta: float) -> void:
    current_action = "collect_booster"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
    if hp == max_hp and amount > 0: first_hit_taken = true
    hp -= amount
    if hp <= 0: alive = false

func use_skill() -> bool:
    if skill_timer <= 0: return true
    return false
