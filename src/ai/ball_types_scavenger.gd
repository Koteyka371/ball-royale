extends RefCounted

const BALL_TYPE = "scavenger"
const HP = 90
const SPEED = 2.0
const DAMAGE = 8
const RADIUS = 10
const PERCEPTION_RADIUS = 150
const AGGRESSION = 0.5
const COLOR = "orange"
const SKILL = "dash"
const SKILL_COOLDOWN = 6.0

var id: int = 0
var hp: float = 90.0
var max_hp: float = 90.0
var x: float = 0.0
var y: float = 0.0
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var materials_collected: int = 0
var damage: float = 8.0
var speed: float = 2.0
var ball_type: String = "scavenger"

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.x = start_x
    self.y = start_y
    self.hp = HP
    self.max_hp = HP
    self.damage = DAMAGE
    self.speed = SPEED

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func flee(delta: float, target = null) -> void:
    self.current_action = "flee"
