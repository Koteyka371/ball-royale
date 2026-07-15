extends RefCounted
class_name Missileer

const BALL_TYPE = "missileer"
const HP = 90.0
const SPEED = 4.0
const DAMAGE = 15.0
const RADIUS = 12.0
const PERCEPTION_RADIUS = 250.0
const AGGRESSION = 0.7
const COLOR = "darkred"
const SKILL = "fire_homing_missile"
const SKILL_COOLDOWN = 4.0

var id: int
var hp: float = HP
var max_hp: float = HP
var x: float = 0.0
var y: float = 0.0
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var difficulty: String = "hard"
var personality = null

func _init(p_id: int, p_x: float = 0.0, p_y: float = 0.0):
    id = p_id
    x = p_x
    y = p_y
    if ResourceLoader.exists("res://ai/personality.gd"):
        var PersonalityScript = load("res://ai/personality.gd")
        personality = PersonalityScript.new("aggressive")

func get_hp_percent() -> float:
    if max_hp > 0:
        return hp / max_hp
    return 0.0

func flee(delta: float) -> void:
    current_action = "flee"

func attack(delta: float) -> void:
    current_action = "attack"

func defend(delta: float) -> void:
    current_action = "defend"

func collect_booster(delta: float) -> void:
    current_action = "collect_booster"

func idle(delta: float) -> void:
    current_action = "idle"

func take_damage(amount: float) -> void:
	if has_meta("radiation_duration") and get_meta("radiation_duration") > 0.0:
		amount *= get_meta("radiation_multiplier") if has_meta("radiation_multiplier") else 1.5
	elif "radiation_duration" in self and self.radiation_duration > 0.0:
		amount *= self.radiation_multiplier if "radiation_multiplier" in self else 1.5

    if hp == max_hp and amount > 0:
        first_hit_taken = true
    hp -= amount
    if hp <= 0:
        alive = false

func use_skill() -> bool:
    if skill_timer <= 0:
        skill_timer = SKILL_COOLDOWN
        return true
    return false

func _to_string() -> String:
    return str(BALL_TYPE) + "#" + str(id) + " HP=" + str(hp) + "/" + str(max_hp) + " [" + current_action + "]"
