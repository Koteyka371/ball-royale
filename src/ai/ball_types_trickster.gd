extends RefCounted

const BALL_TYPE = "trickster"
const HP = 85.0
const SPEED = 4.0
const DAMAGE = 14.0
const RADIUS = 9.0
const PERCEPTION_RADIUS = 270.0
const AGGRESSION = 0.6
const COLOR = "pink"
const SKILL = "deploy_decoy"
const SKILL_COOLDOWN = 4.0
const ATTACK_RANGE = 20.0

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
var attack_range: float = ATTACK_RANGE
var is_decoy: bool = false

var personality = null

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.hp = HP
    self.max_hp = HP
    self.x = start_x
    self.y = start_y

    var PersonalityClass = load("res://src/ai/personality.gd")
    if PersonalityClass:
        self.personality = PersonalityClass.new("aggressive")

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

    var dx = target.x - self.x
    var dy = target.y - self.y
    var dist_sq = dx * dx + dy * dy
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist
        var step = SPEED * delta * 60.0

        self.x += nx * min(step, dist)
        self.y += ny * min(step, dist)

        var target_radius = 10.0
        if "radius" in target:
            target_radius = target.radius
        var max_attack_range = RADIUS + target_radius + 5.0

        var new_dx = target.x - self.x
        var new_dy = target.y - self.y
        var new_dist_sq = new_dx * new_dx + new_dy * new_dy
        var new_dist = 0.0
        if new_dist_sq > 0.0001:
            new_dist = sqrt(new_dist_sq)

        if new_dist <= max_attack_range:
            if attack_timer <= 0:
                if SPEED > 0:
                    attack_timer = max(0.2, 2.0 / SPEED)
                else:
                    attack_timer = max(0.2, 1.0)

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

func get_class() -> String:
    return "Trickster"
