class_name Linker
extends RefCounted

const BALL_TYPE = "linker"
const HP = 100.0
const SPEED = 5.0
const DAMAGE = 2.0
const RADIUS = 12.0
const PERCEPTION_RADIUS = 250.0
const AGGRESSION = 0.5
const COLOR = "blue"
const SKILL = "none"
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
var link_target: Object

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
    self.personality = Personality.new("aggressive")
    self.link_target = null

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func take_damage(amount: float) -> void:
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

	if self.link_target != null and (not ("alive" in self.link_target) or self.link_target.alive):
		var shared_amount = amount * 0.5
		if "hp" in self.link_target:
			self.link_target.hp -= shared_amount
			if self.link_target.hp <= 0:
				self.link_target.hp = 0.0
				self.link_target.alive = false
			amount -= shared_amount

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
