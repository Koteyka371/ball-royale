extends RefCounted

const BALL_TYPE = "chain_caster"
const HP = 80
const SPEED = 3.5
const DAMAGE = 20
const RADIUS = 10
const PERCEPTION_RADIUS = 400
const AGGRESSION = 0.6
const COLOR = "cyan"
const SKILL = "chain_bounce_attack"
const SKILL_COOLDOWN = 6.0

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

func _init(ball_id: int, p_x: float = 0.0, p_y: float = 0.0):
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

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func flee(delta: float) -> void:
    self.current_action = "flee"

func attack(delta: float) -> void:
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
