# Auto-generated ball type: SnowYeti
extends Reference

const BALL_TYPE = "snow_yeti"
const HP = 120
const SPEED = 2.0
const DAMAGE = 18
const RADIUS = 12
const PERCEPTION_RADIUS = 200
const AGGRESSION = 0.6
const COLOR = 'white'
const SKILL = 'yeti_roar'
const SKILL_COOLDOWN = 8.0
const ATTACK_RANGE = 20.0

var id: int = 0
var hp: float = 120.0
var max_hp: float = 120.0
var x: float = 0.0
var y: float = 0.0
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var attack_timer: float = 0.0
var attack_range: float = 20.0
var personality_type: String = "aggressive"

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
    personality_type = "aggressive"

func get_hp_percent() -> float:
    return hp / max_hp if max_hp > 0 else 0.0

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
                if spd <= 0: spd = 1.0
                attack_timer = max(0.2, 2.0 / spd)

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
