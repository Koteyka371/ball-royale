extends RefCounted

var BALL_TYPE = "soul_linker"
var HP = 100.0
var SPEED = 3.5
var DAMAGE = 5.0
var RADIUS = 10.0
var PERCEPTION_RADIUS = 250.0
var AGGRESSION = 0.5
var COLOR = "magenta"
var SKILL = "soul_bond"
var SKILL_COOLDOWN = 10.0

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
var personality: Object

var base_speed: float
var speed: float
var damage: float
var attack_range: float

var linked_enemy = null
var has_linked = false
var attack_timer = 0.0

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    var PersonalityClass = load("res://src/ai/personality.gd")

    self.id = ball_id
    self.hp = float(self.HP)
    self.max_hp = float(self.HP)
    self.x = start_x
    self.y = start_y
    self.alive = true
    self.kills = 0
    self.first_hit_taken = false
    self.current_action = "idle"
    self.skill_timer = 0.0
    self.personality = PersonalityClass.new("strategic")

    self.base_speed = float(self.SPEED)
    self.speed = float(self.SPEED)
    self.damage = float(self.DAMAGE)
    self.attack_range = 15.0

    self.linked_enemy = null
    self.has_linked = false
    self.attack_timer = 0.0

func get_hp_percent() -> float:
    if self.max_hp > 0:
        return self.hp / self.max_hp
    return 0.0

func _link_to(target) -> void:
    self.linked_enemy = target
    self.has_linked = true

    var t_max_hp = 100.0
    if typeof(target) == TYPE_DICTIONARY and target.has("max_hp"):
        t_max_hp = float(target.max_hp)
    elif typeof(target) == TYPE_OBJECT and "max_hp" in target:
        t_max_hp = float(target.max_hp)

    var t_hp = 100.0
    if typeof(target) == TYPE_DICTIONARY and target.has("hp"):
        t_hp = float(target.hp)
    elif typeof(target) == TYPE_OBJECT and "hp" in target:
        t_hp = float(target.hp)

    var t_base_speed = 100.0
    if typeof(target) == TYPE_DICTIONARY and target.has("base_speed"):
        t_base_speed = float(target.base_speed)
    elif typeof(target) == TYPE_OBJECT and "base_speed" in target:
        t_base_speed = float(target.base_speed)
    elif typeof(target) == TYPE_DICTIONARY and target.has("speed"):
        t_base_speed = float(target.speed)
    elif typeof(target) == TYPE_OBJECT and "speed" in target:
        t_base_speed = float(target.speed)

    var t_speed = 100.0
    if typeof(target) == TYPE_DICTIONARY and target.has("speed"):
        t_speed = float(target.speed)
    elif typeof(target) == TYPE_OBJECT and "speed" in target:
        t_speed = float(target.speed)

    self.max_hp = t_max_hp
    self.hp = t_hp
    self.base_speed = t_base_speed
    self.speed = t_speed

func flee(delta: float, target=null) -> void:
    self.current_action = "flee"
    if not self.has_linked and target != null:
        var t_alive = false
        if typeof(target) == TYPE_DICTIONARY and target.has("alive"):
            t_alive = target.alive
        elif typeof(target) == TYPE_OBJECT and "alive" in target:
            t_alive = target.alive
        if t_alive:
            _link_to(target)

func attack(delta: float, target=null) -> void:
    self.current_action = "attack"
    if not self.has_linked and target != null:
        var t_alive = false
        if typeof(target) == TYPE_DICTIONARY and target.has("alive"):
            t_alive = target.alive
        elif typeof(target) == TYPE_OBJECT and "alive" in target:
            t_alive = target.alive
        if t_alive:
            _link_to(target)

    if target == null:
        return

    var t_x = 0.0
    var t_y = 0.0
    if typeof(target) == TYPE_DICTIONARY:
        t_x = float(target.x)
        t_y = float(target.y)
    elif typeof(target) == TYPE_OBJECT:
        t_x = float(target.x)
        t_y = float(target.y)

    var dx = t_x - self.x
    var dy = t_y - self.y
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
            target_radius = float(target.radius)
        elif typeof(target) == TYPE_OBJECT and "radius" in target:
            target_radius = float(target.radius)

        var attack_range_dist = self.RADIUS + target_radius + 5.0

        if dist <= attack_range_dist:
            if self.attack_timer <= 0:
                var speed_factor = 1.0
                if self.speed > 0:
                    speed_factor = 2.0 / self.speed
                self.attack_timer = float(max(0.2, speed_factor))

func defend(delta: float) -> void:
    self.current_action = "defend"

func collect_booster(delta: float) -> void:
    self.current_action = "collect_booster"

func idle(delta: float) -> void:
    self.current_action = "idle"

func take_damage(amount: float) -> void:
    var radiation = 0.0
    if "radiation_duration" in self:
        radiation = float(self.radiation_duration)
    if radiation > 0:
        var mult = 1.5
        if "radiation_multiplier" in self:
            mult = float(self.radiation_multiplier)
        amount *= mult

    var distributed_amount = 0.0

    if self.linked_enemy != null:
        var t_alive = false
        if typeof(self.linked_enemy) == TYPE_DICTIONARY and self.linked_enemy.has("alive"):
            t_alive = self.linked_enemy.alive
        elif typeof(self.linked_enemy) == TYPE_OBJECT and "alive" in self.linked_enemy:
            t_alive = self.linked_enemy.alive

        if t_alive:
            distributed_amount = amount * 0.5
            amount = amount * 0.5

            var t_type = ""
            if typeof(self.linked_enemy) == TYPE_DICTIONARY and self.linked_enemy.has("ball_type"):
                t_type = str(self.linked_enemy.ball_type)
            elif typeof(self.linked_enemy) == TYPE_OBJECT and "ball_type" in self.linked_enemy:
                t_type = str(self.linked_enemy.ball_type)

            if typeof(self.linked_enemy) == TYPE_OBJECT and self.linked_enemy.has_method("take_damage") and t_type != "soul_linker":
                self.linked_enemy.take_damage(distributed_amount)
            else:
                var current_hp = 0.0
                if typeof(self.linked_enemy) == TYPE_DICTIONARY and self.linked_enemy.has("hp"):
                    current_hp = float(self.linked_enemy.hp)
                    self.linked_enemy.hp = current_hp - distributed_amount
                    if self.linked_enemy.hp <= 0:
                        self.linked_enemy.alive = false
                elif typeof(self.linked_enemy) == TYPE_OBJECT and "hp" in self.linked_enemy:
                    current_hp = float(self.linked_enemy.hp)
                    self.linked_enemy.hp = current_hp - distributed_amount
                    if self.linked_enemy.hp <= 0:
                        self.linked_enemy.alive = false

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

func _to_string() -> String:
    return str(self.BALL_TYPE) + "#" + str(self.id) + " HP=" + str(self.hp) + "/" + str(self.max_hp) + " [" + str(self.current_action) + "]"
