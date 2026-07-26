extends RefCounted

var BALL_TYPE = "windcaller"
var HP = 100
var SPEED = 8.0
var DAMAGE = 12
var RADIUS = 10
var PERCEPTION_RADIUS = 200
var AGGRESSION = 0.5
var COLOR = "teal"
var SKILL = "local_tornado"
var SKILL_COOLDOWN = 12.0

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
var gravity_well_immunity: bool
var hazard_push_pull_immunity: bool
var _metadata = {}

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
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
    self.gravity_well_immunity = true
    self.hazard_push_pull_immunity = true

func get_hp_percent() -> float:
    if max_hp > 0:
        return hp / max_hp
    return 0.0

func flee(delta: float) -> void:
    current_action = "flee"

func attack(delta: float) -> void:
    current_action = "attack"

func defend(delta: float) -> void:
    current_action = "defend"

func collect_booster(delta: float) -> void:
    current_action = "collect_booster"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
    var radiation_duration = get_meta("radiation_duration")
    if radiation_duration != null and typeof(radiation_duration) in [TYPE_INT, TYPE_FLOAT] and radiation_duration > 0:
        var radiation_multiplier = get_meta("radiation_multiplier")
        if radiation_multiplier == null:
            radiation_multiplier = 1.5
        amount *= float(radiation_multiplier)

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

func _to_string() -> String:
    return str(BALL_TYPE, "#", id, " HP=", hp, "/", max_hp, " [", current_action, "]")

func set_meta(key: String, value):
    _metadata[key] = value

func get_meta(key: String, default_value = null):
    if _metadata.has(key):
        return _metadata[key]
    return default_value

func has_meta(key: String) -> bool:
    return _metadata.has(key)
