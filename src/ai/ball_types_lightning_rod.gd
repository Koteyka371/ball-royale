extends Node

const BALL_TYPE = "lightning_rod"
const HP = 120
const SPEED = 2.4
const DAMAGE = 20
const RADIUS = 10
const PERCEPTION_RADIUS = 300
const AGGRESSION = 0.4
const COLOR = 'yellow'
const SKILL = 'lightning_strike'
const SKILL_COOLDOWN = 6.0
const ATTACK_RANGE = 30.0

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
var attack_range: float
var personality: Object

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    id = ball_id
    hp = float(HP)
    max_hp = float(HP)
    x = start_x
    y = start_y
    alive = true
    kills = 0
    first_hit_taken = false
    current_action = "idle"
    skill_timer = 0.0
    attack_timer = 0.0
    attack_range = float(ATTACK_RANGE)

    var PersonalityClass = load("res://src/ai/personality.gd")
    if PersonalityClass:
        personality = PersonalityClass.new("defender")

func get_hp_percent() -> float:
    if max_hp > 0:
        return hp / max_hp
    return 0.0

func flee(delta: float, target=null) -> void:
    current_action = "flee"

func attack(delta: float, target=null) -> void:
    current_action = "attack"
    if target == null:
        return

    var dx = target.x - x
    var dy = target.y - y
    var dist_sq = dx * dx + dy * dy
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist
        var step = SPEED * delta * 60.0

        x += nx * min(step, dist)
        y += ny * min(step, dist)

        var target_radius = 10.0
        if "radius" in target:
            target_radius = target.radius
        var a_range = RADIUS + target_radius + 5

        var new_dx = target.x - x
        var new_dy = target.y - y
        var new_dist_sq = new_dx * new_dx + new_dy * new_dy
        var new_dist = sqrt(new_dist_sq) if new_dist_sq > 0.0001 else 0.0

        if new_dist <= a_range:
            if attack_timer <= 0:
                var spd = SPEED
                if spd <= 0:
                    spd = 1.0
                var atk_time = 2.0 / spd
                if atk_time < 0.2:
                    atk_time = 0.2
                attack_timer = atk_time

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
        skill_timer = float(SKILL_COOLDOWN)
        return true
    return false

func get_class_name() -> String:
    return "LightningRod"
