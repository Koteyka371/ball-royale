class_name QuantumTangler

var BALL_TYPE = "quantum_tangler"
var HP = 100
var SPEED = 2.5
var DAMAGE = 10
var RADIUS = 10
var PERCEPTION_RADIUS = 300
var AGGRESSION = 0.5
var COLOR = Color("#9000ff")
var SKILL = "quantum_tangle_dash"
var SKILL_COOLDOWN = 6.0
var ATTACK_RANGE = 20.0

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
var attack_timer: float = 0.0
var attack_range: float
var dash_range_mult: float = 1.2
var leave_tangle_chance: float = 0.33
var vx: float = 0.0
var vy: float = 0.0
var speed: float = 2.5
var damage: float = 10.0
var radius: float = 10.0

func _init(ball_id: int, start_x: float = 0.0, start_y: float = 0.0):
    self.id = ball_id
    self.hp = float(self.HP)
    self.max_hp = float(self.HP)
    self.x = start_x
    self.y = start_y
    self.attack_range = float(self.ATTACK_RANGE)
