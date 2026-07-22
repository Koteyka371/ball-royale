# Auto-generated ball type: Conjurer
extends Reference

const BALL_TYPE = "conjurer"
const HP = 85.0
const SPEED = 2.1
const DAMAGE = 12.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.4
const COLOR = Color(0.5, 0.0, 0.5) # purple
const SKILL = "summon_minions"
const SKILL_COOLDOWN = 10.0
const ATTACK_RANGE = 40.0

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
var personality: Object

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.hp = HP
    self.max_hp = HP
    self.x = start_x
    self.y = start_y
    # Personality could be loaded if there's a global/resource for it, but keeping it simple for data

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func flee(delta: float, target=null) -> void:
    self.current_action = "flee"

func attack(delta: float, target=null) -> void:
    self.current_action = "attack"

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
