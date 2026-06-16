class_name ActionLayer
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func execute(strategy: String, delta: float):
    if "current_action" in self.ball:
        self.ball.current_action = strategy

    if strategy == "flee":
        _flee(delta)
    elif strategy == "attack" or strategy == "chase":
        _attack(delta)
    elif strategy == "defend":
        _defend(delta)
    elif strategy == "opportunistic" or strategy == "collect booster":
        _collect_booster(delta)
    elif strategy == "use skill":
        _use_skill()
    else:
        _idle(delta)

    _clamp_position()
    _update_skill_timer(delta)

func _get_enemies() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("enemies"):
            return entities["enemies"]
        elif typeof(entities) == TYPE_ARRAY:
            var enemies = []
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type != b_type:
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            enemies.append(e)
            return enemies
    return []

func _get_boosters() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("boosters"):
            return entities["boosters"]

    var boosters = []
    if self.world != null and "boosters" in self.world:
        for b in self.world.boosters:
            if "active" in b and b.active:
                var dx = b.x - self.ball.x
                var dy = b.y - self.ball.y
                if sqrt(dx*dx + dy*dy) <= perception_radius:
                    boosters.append(b)
    return boosters

func _apply_obstacle_avoidance(nx: float, ny: float) -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    var entities = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var nearby = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(nearby) == TYPE_DICTIONARY:
            if nearby.has("enemies"): entities.append_array(nearby["enemies"])
            if nearby.has("allies"): entities.append_array(nearby["allies"])
        elif typeof(nearby) == TYPE_ARRAY:
            entities = nearby

    var rx = 0.0
    var ry = 0.0
    var ball_radius = 10.0
    if "radius" in self.ball: ball_radius = self.ball.radius

    for e in entities:
        var alive = true
        if "alive" in e:
            alive = e.alive
        elif e.has_method("is_alive"):
            alive = e.is_alive()

        if alive:
            var e_radius = 10.0
            if "radius" in e: e_radius = e.radius
            var safety_threshold = ball_radius + e_radius + 5.0
            var dx = self.ball.x - e.x
            var dy = self.ball.y - e.y
            var dist = sqrt(dx*dx + dy*dy)

            if dist > 0.01 and dist < safety_threshold:
                var force = (safety_threshold - dist) / safety_threshold
                rx += (dx / dist) * force
                ry += (dy / dist) * force

    var fx = nx + rx
    var fy = ny + ry
    var mag = sqrt(fx*fx + fy*fy)

    if mag > 0:
        return [fx / mag, fy / mag]
    return [nx, ny]

func _flee(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var nearest = null
        var min_dist_sq = INF
        for e in enemies:
            var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = e

        var dx = self.ball.x - nearest.x
        var dy = self.ball.y - nearest.y
        var dist = sqrt(dx*dx + dy*dy)
        if dist > 0.01:
            var dir = _apply_obstacle_avoidance(dx / dist, dy / dist)
            var nx = dir[0]
            var ny = dir[1]
            var speed = 2.0
            if "speed" in self.ball: speed = self.ball.speed
            var step = speed * delta * 60
            self.ball.x += nx * step
            self.ball.y += ny * step
    else:
        _idle(delta)

func _attack(delta: float):
    var enemies = _get_enemies()
    if enemies.size() > 0:
        var target = null
        var min_dist_sq = INF
        for e in enemies:
            var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                target = e

        var dx = target.x - self.ball.x
        var dy = target.y - self.ball.y
        var dist = sqrt(dx*dx + dy*dy)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist > 0.01:
            var dir = _apply_obstacle_avoidance(dx / dist, dy / dist)
            var nx = dir[0]
            var ny = dir[1]
            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = target.x - self.ball.x
        dy = target.y - self.ball.y
        var dist_new = sqrt(dx*dx + dy*dy)

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist_new <= ball_radius + target_radius + 5.01:
            if self.world != null and self.world.has_method("_deal_damage"):
                self.world._deal_damage(self.ball, target)
    else:
        _idle(delta)

func _defend(delta: float):
    _idle(delta * 0.5)

func _collect_booster(delta: float):
    var boosters = _get_boosters()
    if boosters.size() > 0:
        var nearest = null
        var min_dist_sq = INF
        for b in boosters:
            var dist_sq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = b

        var dx = nearest.x - self.ball.x
        var dy = nearest.y - self.ball.y
        var dist = sqrt(dx*dx + dy*dy)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist > 0.01:
            var dir = _apply_obstacle_avoidance(dx / dist, dy / dist)
            var nx = dir[0]
            var ny = dir[1]
            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = nearest.x - self.ball.x
        dy = nearest.y - self.ball.y
        var dist_new = sqrt(dx*dx + dy*dy)

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist_new <= ball_radius + 10.01:
            if self.world != null and self.world.has_method("_collect_booster"):
                self.world._collect_booster(self.ball, nearest)
    else:
        _idle(delta)

func _use_skill():
    var skill_timer = 0.0
    if "skill_timer" in self.ball: skill_timer = self.ball.skill_timer

    if skill_timer <= 0:
        if self.ball.has_method("use_skill"):
            self.ball.use_skill()
        if "skill_cooldown" in self.ball:
            self.ball.skill_timer = self.ball.skill_cooldown

func _idle(delta: float):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    self.ball.x += randf_range(-1.0, 1.0) * speed * 0.3
    self.ball.y += randf_range(-1.0, 1.0) * speed * 0.3

func _clamp_position():
    if self.world != null and "width" in self.world and "height" in self.world:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius
        self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
        self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta
