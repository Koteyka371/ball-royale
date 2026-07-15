extends RefCounted

const BALL_TYPE = "void_mage"
const HP = 100
const SPEED = 2.0
const DAMAGE = 10
const RADIUS = 10
const PERCEPTION_RADIUS = 300
const AGGRESSION = 0.5
const COLOR = "purple"
const SKILL = "black_hole_summon"
const SKILL_COOLDOWN = 10.0
const ATTACK_RANGE = 50.0

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
    var PersonalityClass = load("res://src/ai/personality.gd")
    self.id = ball_id
    self.hp = float(HP)
    self.max_hp = float(HP)
    self.x = start_x
    self.y = start_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.attack_timer = 0.0
    self.attack_range = float(ATTACK_RANGE)
    self.personality = PersonalityClass.new("strategic")

func get_hp_percent() -> float:
    return self.hp / self.max_hp if self.max_hp > 0 else 0.0

func flee(delta: float, target = null) -> void:
    self.current_action = "flee"

func attack(delta: float, target = null) -> void:
    self.current_action = "attack"
    if target == null:
        return

    var target_x = target.x if "x" in target else target.get("position").x if target.get("position") != null else 0.0
    var target_y = target.y if "y" in target else target.get("position").y if target.get("position") != null else 0.0

    var dx = target_x - self.x
    var dy = target_y - self.y
    var dist_sq = dx * dx + dy * dy
    if dist_sq > 0.0001:
        var dist = sqrt(dist_sq)
        var nx = dx / dist
        var ny = dy / dist
        var step = SPEED * delta * 60.0

        self.x += nx * min(step, dist)
        self.y += ny * min(step, dist)

        var t_radius = 10.0
        if "radius" in target:
            t_radius = target.radius
        elif target.has_method("get_meta") and target.has_meta("radius"):
            t_radius = target.get_meta("radius")
        elif typeof(target) == TYPE_DICTIONARY and target.has("radius"):
            t_radius = target["radius"]

        var range_val = RADIUS + t_radius + 5.0

        var new_dx = target_x - self.x
        var new_dy = target_y - self.y
        var new_dist_sq = new_dx * new_dx + new_dy * new_dy
        var new_dist = sqrt(new_dist_sq) if new_dist_sq > 0.0001 else 0.0

        if new_dist <= range_val:
            if self.attack_timer <= 0:
                self.attack_timer = max(0.2, 2.0 / SPEED if SPEED > 0 else 1.0)

func defend(delta: float) -> void:
    self.current_action = "defend"

func collect_booster(delta: float) -> void:
    self.current_action = "opportunistic"

func idle(delta: float) -> void:
    self.current_action = "idle"

func take_damage(amount: float) -> void:
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

    if self.hp == self.max_hp and amount > 0:
        self.first_hit_taken = true
    self.hp -= amount
    if self.hp <= 0:
        self.alive = false

func use_skill() -> bool:
    if self.skill_timer <= 0:
        self.skill_timer = SKILL_COOLDOWN
        return true
    return false

func _to_string() -> String:
    return str(BALL_TYPE) + "#" + str(self.id) + " HP=" + str(self.hp) + "/" + str(self.max_hp) + " [" + str(self.current_action) + "]"
