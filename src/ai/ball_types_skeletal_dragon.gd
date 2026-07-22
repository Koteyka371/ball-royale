extends RefCounted

const BALL_TYPE = "skeletal_dragon"

var id: int
var hp: float = 150.0
var max_hp: float = 150.0
var x: float = 0.0
var y: float = 0.0
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var attack_timer: float = 0.0
var attack_range: float = 150.0
var has_ranged_breath: bool = true
var is_enraged: bool = true
var enrage_timer: float = 99999.0
var speed: float = 3.5
var damage: float = 25.0
var radius: float = 15.0

func _init(ball_id: int = 0, p_x: float = 0.0, p_y: float = 0.0):
    id = ball_id
    x = p_x
    y = p_y

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
    current_action = "opportunistic"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
    if hp == max_hp and amount > 0:
        first_hit_taken = true
    hp -= amount
    if hp <= 0:
        alive = false

func tick(delta: float) -> void:
    if not alive:
        return
    if attack_timer > 0:
        attack_timer -= delta
