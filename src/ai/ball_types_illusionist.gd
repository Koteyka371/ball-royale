# Auto-generated ball type: Illusionist
extends Reference

const BALL_TYPE = "illusionist"
const HP = 85.0
const SPEED = 3.5
const DAMAGE = 15.0
const RADIUS = 9.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.6
const COLOR = Color(0.5, 0.0, 0.5) # purple
const SKILL = "illusion"
const SKILL_COOLDOWN = 4.0
const ATTACK_RANGE = 25.0

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
