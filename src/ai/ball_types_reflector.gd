extends "res://src/ai/ball.gd"

class_name Reflector

const BALL_TYPE_NAME = "reflector"
const HP_VAL = 120
const SPEED_VAL = 4.0
const DAMAGE_VAL = 10
const RADIUS_VAL = 12
const PERCEPTION_RADIUS_VAL = 300
const AGGRESSION_VAL = 0.2
const COLOR_VAL = "silver"
const SKILL_NAME = "reflective_shield"
const SKILL_COOLDOWN_VAL = 12.0
const ATTACK_RANGE_VAL = 20.0

var reflective_timer: float = 0.0
var is_reflective: bool = false
var skill_timer_val: float = 0.0
var attack_timer_val: float = 0.0
var current_action_state: String = "idle"

func _init():
    self.set_meta("ball_type", BALL_TYPE_NAME)
    self.set_meta("hp", HP_VAL)
    self.set_meta("max_hp", HP_VAL)
    self.set_meta("speed", SPEED_VAL)
    self.set_meta("damage", DAMAGE_VAL)
    self.set_meta("radius", RADIUS_VAL)
    self.set_meta("perception_radius", PERCEPTION_RADIUS_VAL)
    self.set_meta("color", COLOR_VAL)
    self.set_meta("skill", SKILL_NAME)
    self.set_meta("skill_cooldown", SKILL_COOLDOWN_VAL)
    self.set_meta("reflective_timer", 0.0)
    self.set_meta("is_reflective", false)

func tick(delta: float) -> void:
    if not self.get_meta("alive", true):
        return

    var r_timer = self.get_meta("reflective_timer", 0.0)
    if r_timer > 0:
        r_timer -= delta
        self.set_meta("is_reflective", true)
        if r_timer <= 0:
            self.set_meta("is_reflective", false)
            r_timer = 0.0
        self.set_meta("reflective_timer", r_timer)

func use_skill() -> bool:
    var s_timer = self.get_meta("skill_timer", 0.0)
    if s_timer <= 0:
        self.set_meta("skill_timer", SKILL_COOLDOWN_VAL)
        self.set_meta("reflective_timer", 4.0)
        self.set_meta("is_reflective", true)
        return true
    return false
