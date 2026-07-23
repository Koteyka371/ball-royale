# Auto-generated ball type: Retaliator
# A ball that passively reflects a percentage of damage taken back to the attacker.

extends Object

const BALL_TYPE = "retaliator"

var id: int
var hp: float = 120.0
var max_hp: float = 120.0
var x: float
var y: float
var alive: bool = true
var kills: int = 0
var first_hit_taken: bool = false
var current_action: String = "idle"
var skill_timer: float = 0.0
var attack_timer: float = 0.0
var attack_range: float = 20.0

var personality = {"type": "aggressive"}

var speed: float = 3.5
var damage: float = 10.0
var radius: float = 12.0
var perception_radius: float = 300.0
var aggression: float = 0.6
var color: String = "dark_red"
var skill: String = "taunt"
var skill_cooldown: float = 10.0

var passive_reflect_percent: float = 0.5
var taunt_timer: float = 0.0

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
	self.id = ball_id
	self.x = start_x
	self.y = start_y
	self.hp = 120.0
	self.max_hp = 120.0
	self.alive = true
	self.kills = 0
	self.first_hit_taken = false
	self.current_action = "idle"
	self.skill_timer = 0.0
	self.attack_timer = 0.0
	self.attack_range = 20.0
	self.personality = {"type": "aggressive"}
	self.speed = 3.5
	self.damage = 10.0
	self.radius = 12.0
	self.perception_radius = 300.0
	self.aggression = 0.6
	self.color = "dark_red"
	self.skill = "taunt"
	self.skill_cooldown = 10.0
	self.passive_reflect_percent = 0.5
	self.taunt_timer = 0.0

func get_hp_percent() -> float:
	if self.max_hp > 0:
		return self.hp / self.max_hp
	return 0.0

func flee(delta: float, target = null) -> void:
	self.current_action = "flee"

func attack(delta: float, target = null) -> void:
	self.current_action = "attack"
	if target == null:
		return

	var dx = target.x - self.x
	var dy = target.y - self.y
	var dist_sq = dx * dx + dy * dy
	if dist_sq > 0.0001:
		var dist = sqrt(dist_sq)
		var nx = dx / dist
		var ny = dy / dist
		var step = self.speed * delta * 60.0

		self.x += nx * min(step, dist)
		self.y += ny * min(step, dist)

		var target_radius = 10.0
		if typeof(target) == TYPE_DICTIONARY and target.has("radius"):
			target_radius = target.radius
		elif typeof(target) != TYPE_DICTIONARY and target.has_method("has_meta") and target.has_meta("radius"):
			target_radius = target.get_meta("radius")
		elif "radius" in target:
			target_radius = target.radius

		var attack_range_limit = self.radius + target_radius + 5.0

		var new_dx = target.x - self.x
		var new_dy = target.y - self.y
		var new_dist_sq = new_dx * new_dx + new_dy * new_dy
		var new_dist = 0.0
		if new_dist_sq > 0.0001:
			new_dist = sqrt(new_dist_sq)

		if new_dist <= attack_range_limit:
			if self.attack_timer <= 0:
				var max_val = 0.2
				if self.speed > 0:
					max_val = max(0.2, 2.0 / self.speed)
				self.attack_timer = max_val

func defend(delta: float) -> void:
	self.current_action = "defend"

func collect_booster(delta: float) -> void:
	self.current_action = "opportunistic"

func idle(delta: float) -> void:
	self.current_action = "idle"

func take_damage(amount: float) -> void:
	var radiation_duration = 0.0
	if self.has_meta("radiation_duration"): radiation_duration = float(self.get_meta("radiation_duration"))
	if radiation_duration > 0:
		var rad_mult = 1.5
		if self.has_meta("radiation_multiplier"): rad_mult = float(self.get_meta("radiation_multiplier"))
		amount *= rad_mult

	if self.hp == self.max_hp and amount > 0:
		self.first_hit_taken = true
	self.hp -= amount
	if self.hp <= 0:
		self.alive = false

func tick(delta: float) -> void:
	if not self.alive:
		return
	if self.taunt_timer > 0:
		self.taunt_timer -= delta
		if self.taunt_timer < 0:
			self.taunt_timer = 0.0

func use_skill() -> bool:
	if self.skill_timer <= 0:
		self.skill_timer = self.skill_cooldown
		self.taunt_timer = 3.0
		return true
	return false

func _to_string() -> String:
	return "%s#%d HP=%.1f/%.1f [%s]" % [BALL_TYPE, self.id, self.hp, self.max_hp, self.current_action]
