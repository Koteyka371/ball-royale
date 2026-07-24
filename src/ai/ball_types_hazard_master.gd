extends RefCounted

const BALL_TYPE = "hazard_master"
const HP = 100
const SPEED = 8.0
const DAMAGE = 10
const RADIUS = 10
const PERCEPTION_RADIUS = 200
const AGGRESSION = 0.5
const COLOR = "orange"
const SKILL = "spawn_tornado"
const SKILL_COOLDOWN = 15.0

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
var personality = null
var hazard_immunity: bool

func _init(ball_id: int, p_x: float = 0.0, p_y: float = 0.0) -> void:
    self.id = ball_id
    self.hp = float(HP)
    self.max_hp = float(HP)
    self.x = p_x
    self.y = p_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.hazard_immunity = true

    var PersonalityClass = null
    var script = load("res://src/ai/personality.gd")
    if script:
        for key in script.get_script_constant_map().keys():
            var val = script.get_script_constant_map()[key]
            if typeof(val) == TYPE_OBJECT and val.has_method("new"):
                PersonalityClass = val
                break
    if PersonalityClass:
        self.personality = PersonalityClass.new("cautious")

func get_hp_percent() -> float:
    return hp / max_hp if max_hp > 0 else 0.0

func flee(delta: float) -> void:
    current_action = "flee"

func attack(delta: float) -> void:
    current_action = "attack"

func defend(delta: float) -> void:
    current_action = "defend"

func collect_booster(delta: float) -> void:
    current_action = "opportunistic"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
    var mult = 1.0
    if has_meta("radiation_duration") and get_meta("radiation_duration") > 0:
        mult = get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
    amount *= mult

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
