extends RefCounted

const BALL_TYPE = "glitch_v2"
const HP = 80.0
const SPEED = 4.5
const DAMAGE = 12.0
const RADIUS = 10.0
const PERCEPTION_RADIUS = 250.0
const AGGRESSION = 0.7
const COLOR = "purple"
const SKILL_COOLDOWN = 3.0

var id: int = 0
var hp: float = 80.0
var max_hp: float = 80.0
var x: float = 0.0
var y: float = 0.0
var vx: float = 0.0
var vy: float = 0.0
var base_speed: float = SPEED
var speed: float = SPEED
var damage: float = DAMAGE
var radius: float = RADIUS
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var active_skill: String = "glitch_teleport_v2"

func _init(ball_id: int = 0, p_x: float = 0.0, p_y: float = 0.0):
    id = ball_id
    x = p_x
    y = p_y
    hp = HP
    max_hp = HP
    base_speed = SPEED
    speed = SPEED
    damage = DAMAGE
    radius = RADIUS

func get_hp_percent() -> float:
    if max_hp > 0:
        return hp / max_hp
    return 0.0

func flee(delta: float, target = null) -> void:
    current_action = "flee"

func attack(delta: float, target = null) -> void:
    current_action = "attack"

func defend(delta: float) -> void:
    current_action = "defend"

func collect_booster(delta: float) -> void:
    current_action = "opportunistic"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
    var dmg = amount
    var rad_dur = 0.0
    if "radiation_duration" in self:
        rad_dur = self.get("radiation_duration")
    if rad_dur > 0:
        var mult = 1.5
        if "radiation_multiplier" in self:
            mult = self.get("radiation_multiplier")
        dmg *= mult

    if hp == max_hp and dmg > 0:
        first_hit_taken = true
    hp -= dmg

    if dmg > 0:
        var angle = randf_range(0.0, 2.0 * PI)
        var dist = randf_range(20.0, 50.0)
        x += cos(angle) * dist
        y += sin(angle) * dist

    if hp <= 0:
        alive = false
        hp = 0

func use_skill() -> bool:
    if skill_timer <= 0:
        skill_timer = SKILL_COOLDOWN
        return true
    return false
