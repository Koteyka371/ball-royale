extends Node

class_name Mimic

var BALL_TYPE = "mimic"
var HP = 100
var SPEED = 2.0
var DAMAGE = 10
var RADIUS = 10
var PERCEPTION_RADIUS = 250
var AGGRESSION = 0.5
var COLOR = "magenta"
var SKILL = "none"
var SKILL_COOLDOWN = 5.0

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

var base_speed: float
var speed: float
var damage: float
var attack_range: float = 15.0
var copied_skill = null
var mimic_targets = {}
var copy_duration_required: float = 3.0

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.hp = float(self.HP)
    self.max_hp = float(self.HP)
    self.x = start_x
    self.y = start_y
    # Personality could be a dict or object in GDScript
    self.personality = {"trait": "opportunist"}

    self.base_speed = float(self.SPEED)
    self.speed = float(self.SPEED)
    self.damage = float(self.DAMAGE)

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func _copy_stats_from(enemy):
    var target_max_hp = 100.0
    if "max_hp" in enemy:
        target_max_hp = float(enemy.max_hp)

    var target_speed = 2.0
    if "SPEED" in enemy:
        target_speed = float(enemy.SPEED)
    elif "speed" in enemy:
        target_speed = float(enemy.speed)

    var target_damage = 10.0
    if "DAMAGE" in enemy:
        target_damage = float(enemy.DAMAGE)
    elif "damage" in enemy:
        target_damage = float(enemy.damage)

    self.max_hp = self.max_hp * 0.5 + target_max_hp * 0.5

    var enemy_hp = target_max_hp
    if "hp" in enemy:
        enemy_hp = float(enemy.hp)
    self.hp = self.hp * 0.5 + enemy_hp * 0.5

    self.base_speed = self.base_speed * 0.5 + target_speed * 0.5
    self.speed = self.base_speed
    self.damage = self.damage * 0.5 + target_damage * 0.5

    if "SKILL" in enemy:
        self.copied_skill = enemy.SKILL
        self.SKILL = self.copied_skill
    elif "skill" in enemy:
        self.copied_skill = enemy.skill
        self.SKILL = self.copied_skill

func process_mimicry(enemies: Array, delta: float):
    if self.copied_skill != null:
        return

    for e in enemies:
        var dx = e.x - self.x
        var dy = e.y - self.y
        var dist_sq = dx * dx + dy * dy
        if dist_sq < 2500:
            if not self.mimic_targets.has(e.id):
                self.mimic_targets[e.id] = 0.0
            self.mimic_targets[e.id] += delta

            if self.mimic_targets[e.id] >= self.copy_duration_required:
                self._copy_stats_from(e)
                break
        elif self.mimic_targets.has(e.id):
            self.mimic_targets[e.id] = max(0.0, self.mimic_targets[e.id] - delta * 0.5)

func notify_kill(victim):
    if self.copied_skill == null:
        self._copy_stats_from(victim)

func flee(delta: float) -> void:
    self.current_action = "flee"

func attack(delta: float) -> void:
    if self.copied_skill == null:
        self.current_action = "chase"
    else:
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

    if self.hp <= 0 and self.get("quantum_relay_timer") != null and self.get("quantum_relay_timer") > 0.0:
        self.hp = self.max_hp * 0.2
        self.x = self.get("quantum_relay_x") if self.get("quantum_relay_x") != null else self.x
        self.y = self.get("quantum_relay_y") if self.get("quantum_relay_y") != null else self.y
        self.set("quantum_relay_timer", 0.0)
        return

    if self.hp <= 0:
        self.alive = false

func use_skill() -> bool:
    if self.skill_timer <= 0 and self.copied_skill != null:
        self.skill_timer = self.SKILL_COOLDOWN
        return true
    return false
