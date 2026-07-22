extends Reference
class_name SolarBot

var BALL_TYPE = "solar_bot"
var HP = 120.0
var SPEED = 4.5
var DAMAGE = 12.0
var RADIUS = 12.0
var PERCEPTION_RADIUS = 250.0
var AGGRESSION = 0.6
var COLOR = "gold"
var SKILL = "solar_flare"
var SKILL_COOLDOWN = 6.0

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
var personality = null # Replaced/handled natively via action layer
var difficulty: String

func _init(ball_id: int = 0, initial_x: float = 0.0, initial_y: float = 0.0):
    self.id = ball_id
    self.hp = self.HP
    self.max_hp = self.HP
    self.x = initial_x
    self.y = initial_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.difficulty = "hard"

func get_hp_percent() -> float:
    if self.max_hp > 0.0:
        return self.hp / self.max_hp
    return 0.0

func flee(delta: float) -> void:
    self.current_action = "flee"

func attack(delta: float) -> void:
    self.current_action = "attack"

func defend(delta: float) -> void:
    self.current_action = "defend"

func collect_booster(delta: float) -> void:
    self.current_action = "collect_booster"

func idle(delta: float) -> void:
    self.current_action = "idle"

func take_damage(amount: float) -> void:
    var radiation_duration = 0.0
    if "radiation_duration" in self: radiation_duration = self.get("radiation_duration")
    if radiation_duration > 0.0:
        var rad_mult = 1.5
        if "radiation_multiplier" in self: rad_mult = self.get("radiation_multiplier")
        amount *= rad_mult

    self.hp -= amount

    if self.hp <= 0 and self.get("quantum_relay_timer") != null and self.get("quantum_relay_timer") > 0.0:
        self.hp = self.max_hp * 0.2
        self.x = self.get("quantum_relay_x") if self.get("quantum_relay_x") != null else self.x
        self.y = self.get("quantum_relay_y") if self.get("quantum_relay_y") != null else self.y
        self.set("quantum_relay_timer", 0.0)
        return

    if self.hp <= 0:
        self.hp = 0
        self.alive = false

func use_skill() -> bool:
    if self.skill_timer <= 0:
        self.skill_timer = self.SKILL_COOLDOWN
        return true
    return false
