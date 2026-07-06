extends RefCounted

const BALL_TYPE = "chaos_lord"
const HP = 120.0
const SPEED = 5.0
const DAMAGE = 15.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 300.0
const AGGRESSION = 0.5
const COLOR = "black"
const SKILL = "global_confusion"
const SKILL_COOLDOWN = 20.0
const ATTACK_RANGE = 20.0

var id: int
var hp: float
var max_hp: float
var damage: float
var speed: float
var x: float
var y: float
var alive: bool
var kills: int
var first_hit_taken: bool
var current_action: String
var skill_timer: float
var attack_timer: float
var attack_range: float

func _init(ball_id: int, p_x: float = 0.0, p_y: float = 0.0):
    self.id = ball_id
    self.hp = float(HP)
    self.max_hp = float(HP)
    self.damage = float(DAMAGE)
    self.speed = float(SPEED)
    self.x = p_x
    self.y = p_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.attack_timer = 0.0
    self.attack_range = float(ATTACK_RANGE)

func get_hp_percent() -> float:
    if max_hp > 0:
        return hp / max_hp
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
