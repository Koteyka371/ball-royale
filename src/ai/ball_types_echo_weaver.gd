extends RefCounted

const SKILL = "echo_rewind"
const SKILL_COOLDOWN = 12.0

var id: int
var x: float
var y: float
var base_speed: float
var max_hp: float
var hp: float
var damage: float
var radius: float

var team: String
var kind: String
var alive: bool

var color: String
var skill: String
var skill_timer: float

var is_echo_recording: bool
var echo_rewind_timer: float
var echo_rewind_state: Dictionary

func _init(_id: int, _x: float, _y: float) -> void:
    self.id = _id
    self.x = _x
    self.y = _y
    self.base_speed = 3.5
    self.max_hp = 100.0
    self.hp = self.max_hp
    self.damage = 10.0
    self.radius = 15.0

    self.team = "echo_weaver"
    self.kind = "player"
    self.alive = true

    self.color = "light_blue"
    self.skill = SKILL
    self.skill_timer = 0.0

    self.is_echo_recording = false
    self.echo_rewind_timer = 0.0
    self.echo_rewind_state = {}

func tick(world: Object, balls: Array, delta: float = 0.016) -> void:
    if self.skill_timer > 0:
        self.skill_timer -= delta

func use_skill() -> bool:
    if self.skill_timer <= 0:
        if not self.is_echo_recording:
            self.skill_timer = 0.5
        else:
            self.skill_timer = SKILL_COOLDOWN
        return true
    return false
