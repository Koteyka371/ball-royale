extends RefCounted

const Personality = preload("res://src/ai/personality.gd")

const BALL_TYPE = "magnet"
const HP = 150.0
const SPEED = 2.5
const DAMAGE = 10.0
const RADIUS = 15.0
const PERCEPTION_RADIUS = 250.0
const AGGRESSION = 0.6
const COLOR = "purple"
const SKILL = "repel_burst"
const SKILL_COOLDOWN = 10.0

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
var personality

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
    self.personality = Personality.new("greedy")

func get_hp_percent() -> float:
    return self.hp / self.max_hp if self.max_hp > 0.0 else 0.0

func flee(_delta: float):
    self.current_action = "flee"

func attack(_delta: float):
    self.current_action = "attack"

func defend(_delta: float):
    self.current_action = "defend"

func collect_booster(_delta: float):
    self.current_action = "opportunistic"

func idle(_delta: float):
    self.current_action = "idle"

func take_damage(amount: float):
    if self.hp == self.max_hp and amount > 0.0:
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
    if self.skill_timer <= 0.0:
        self.skill_timer = SKILL_COOLDOWN
        return true
    return false
