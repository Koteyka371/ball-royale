extends RefCounted

const BALL_TYPE = "lightning_tether"
const HP = 80.0
const SPEED = 3.5
const DAMAGE = 2.0
const RADIUS = 12.0
const PERCEPTION_RADIUS = 250.0
const AGGRESSION = 0.8
const COLOR = 'yellow'
const SKILL = 'lightning_tether'
const SKILL_COOLDOWN = 8.0
const ATTACK_RANGE = 25.0

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
var personality = null
var lightning_tether_timer: float
var lightning_tether_target = null

func _init(ball_id: int, init_x: float = 0.0, init_y: float = 0.0):
    self.id = ball_id
    self.hp = HP
    self.max_hp = HP
    self.x = init_x
    self.y = init_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.attack_timer = 0.0
    self.attack_range = ATTACK_RANGE
    self.lightning_tether_timer = 0.0
    self.lightning_tether_target = null

    # We load Personality dynamically to avoid circular dependencies if it's not a global class
    if ResourceLoader.exists("res://src/ai/personality.gd"):
        var PersonalityScript = load("res://src/ai/personality.gd")
        if PersonalityScript:
            self.personality = PersonalityScript.new("aggressive")

func get_hp_percent() -> float:
    if max_hp > 0:
        return hp / max_hp
    return 0.0

func flee(delta: float, target = null) -> void:
    current_action = "flee"

func attack(delta: float, target = null) -> void:
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
            target_radius = float(target.radius)
        var a_range = RADIUS + target_radius + 5.0

        var new_dx = target.x - self.x
        var new_dy = target.y - self.y
        var new_dist_sq = new_dx * new_dx + new_dy * new_dy
        var new_dist = sqrt(new_dist_sq) if new_dist_sq > 0.0001 else 0.0

        if new_dist <= a_range:
            if attack_timer <= 0:
                attack_timer = max(0.2, 2.0 / SPEED if SPEED > 0 else 1.0)

func defend(delta: float) -> void:
    current_action = "defend"

func collect_booster(delta: float) -> void:
    current_action = "opportunistic"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

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
