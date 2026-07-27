extends Node

var id: int = -1
var ball_type: String = "avenger"
var hp: float = 120.0
var max_hp: float = 120.0
var damage: float = 10.0
var speed: float = 2.0
var radius: float = 10.0
var perception_radius: float = 250.0
var aggression: float = 0.8
var x: float = 0.0
var y: float = 0.0
var vx: float = 0.0
var vy: float = 0.0
var alive: bool = true
var team: String = ""
var kills: int = 0
var first_hit_taken: bool = false
var skill_timer: float = 0.0
var current_action: String = "idle"
var skill: String = "nemesis_pull"
var skill_cooldown: float = 8.0

func get_hp_percent() -> float:
    if max_hp > 0: return hp / max_hp
    return 0.0

func flee(_delta: float) -> void:
    current_action = "flee"

func attack(_delta: float) -> void:
    current_action = "attack"

func defend(_delta: float) -> void:
    current_action = "defend"

func collect_booster(_delta: float) -> void:
    current_action = "collect_booster"

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
        skill_timer = skill_cooldown
        return true
    return false
