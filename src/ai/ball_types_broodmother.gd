class_name Broodmother
extends RefCounted

const BALL_TYPE = "broodmother"
const HP = 150.0
const SPEED = 1.5
const DAMAGE = 2.0
const RADIUS = 15.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.1
const COLOR = "purple"
const SKILL = "summon_broodlings"
const SKILL_COOLDOWN = 10.0

var id: int
var team: String
var ball_type: String
var hp: float
var max_hp: float
var x: float
var y: float
var alive: bool
var kills: int
var first_hit_taken: bool
var current_action: String
var skill_timer: float
var personality: Personality
var attack_timer: float
var attack_range: float

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.hp = HP
    self.max_hp = HP
    self.x = start_x
    self.y = start_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.attack_timer = 0.0
    self.attack_range = 20.0
    self.personality = Personality.new("defender")

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func flee(_delta: float) -> void:
    self.current_action = "flee"

func attack(_delta: float) -> void:
    self.current_action = "attack"

func defend(_delta: float) -> void:
    self.current_action = "defend"

func collect_booster(_delta: float) -> void:
    self.current_action = "opportunistic"

func idle(_delta: float) -> void:
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
