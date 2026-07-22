extends RefCounted

const BALL_TYPE = "illusionist"
const HP = 90
const SPEED = 6.0
const DAMAGE = 20
const RADIUS = 10
const PERCEPTION_RADIUS = 300
const AGGRESSION = 0.5
const COLOR = "purple"
const SKILL = "mass_illusion"
const SKILL_COOLDOWN = 12.0
const ATTACK_RANGE = 25.0

var id: int
var hp: float
var max_hp: float
var damage: float
var x: float
var y: float
var alive: bool
var kills: int
var first_hit_taken: bool
var current_action: String
var skill_timer: float
var attack_timer: float
var attack_range: float
var personality

const Personality = preload("res://ai/personality.gd")

func _init(ball_id: int = 0, initial_x: float = 0.0, initial_y: float = 0.0):
    self.id = ball_id
    self.hp = float(HP)
    self.max_hp = float(HP)
    self.damage = float(DAMAGE)
    self.x = initial_x
    self.y = initial_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.attack_timer = 0.0
    self.attack_range = float(ATTACK_RANGE)
    self.personality = Personality.new("cunning")

func get_hp_percent() -> float:
    return self.hp / self.max_hp if self.max_hp > 0 else 0.0

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
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

    if self.hp == self.max_hp and amount > 0:
        self.first_hit_taken = true
    self.hp -= amount

    if self.hp <= 0 and self.get("quantum_relay_timer") != null and self.get("quantum_relay_timer") > 0.0:
        self.hp = self.max_hp * 0.2
        self.x = self.get("quantum_relay_x") if self.get("quantum_relay_x") != null else self.x
        self.y = self.get("quantum_relay_y") if self.get("quantum_relay_y") != null else self.y
        self.set("quantum_relay_timer", 0.0)
        return

    if self.hp <= 0:
        self.alive = false

func use_skill() -> bool:
    if self.skill_timer <= 0:
        self.skill_timer = SKILL_COOLDOWN
        return true
    return false

func get_class_name() -> String:
    return "Illusionist"
