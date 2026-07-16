extends Node

class_name Spy

var BALL_TYPE = "spy"
var HP = 80
var SPEED = 5.0
var DAMAGE = 20
var RADIUS = 10
var PERCEPTION_RADIUS = 300
var AGGRESSION = 0.5
var COLOR = "black"
var SKILL = "disguise"
var SKILL_COOLDOWN = 12.0

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
var personality

var is_disguised: bool = false
var disguise_timer: float = 0.0
var original_color: String = "black"
var original_ball_type: String = "spy"
var original_team: String = "spy"

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.hp = float(self.HP)
    self.max_hp = float(self.HP)
    self.x = start_x
    self.y = start_y
    self.personality = {"trait": "cunning"}

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
    if self.hp <= 0:
        self.alive = false

func use_skill() -> bool:
    if self.skill_timer <= 0:
        self.skill_timer = self.SKILL_COOLDOWN
        return true
    return false
