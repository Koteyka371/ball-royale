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

func _apply_movement(nx: float, ny: float, step: float, dist: float, is_fleeing: bool = false, target = null):
    if is_nan(nx) or is_nan(ny) or is_inf(nx) or is_inf(ny):
        return

    var final_nx = nx
    var final_ny = ny

    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        var all_entities = []
        if typeof(entities) == TYPE_DICTIONARY:
            if entities.has("enemies"): all_entities.append_array(entities["enemies"])
            if entities.has("allies"): all_entities.append_array(entities["allies"])

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var repulsive_x = 0.0
        var repulsive_y = 0.0

        for ent in all_entities:
            if ent == self.ball or ent == target:
                continue

            var ex = 0.0
            if "x" in ent: ex = ent.x
            var ey = 0.0
            if "y" in ent: ey = ent.y
            var eradius = 10.0
            if "radius" in ent: eradius = ent.radius

            var dx = self.ball.x - ex
            var dy = self.ball.y - ey
            var d = sqrt(dx*dx + dy*dy)

            var safety_threshold = ball_radius + eradius + 5.0

            if d > 0.01 and d < safety_threshold:
                var force = (safety_threshold - d) / safety_threshold
                repulsive_x += (dx / d) * force
                repulsive_y += (dy / d) * force

        if abs(repulsive_x) > 0.01 or abs(repulsive_y) > 0.01:
            final_nx += repulsive_x
            final_ny += repulsive_y

            var m = sqrt(final_nx*final_nx + final_ny*final_ny)
            if m > 0.01:
                final_nx /= m
                final_ny /= m

    if is_nan(final_nx) or is_nan(final_ny) or is_inf(final_nx) or is_inf(final_ny):
        return

    if is_fleeing:
        self.ball.x += final_nx * step
        self.ball.y += final_ny * step
    else:
        self.ball.x += final_nx * min(step, dist)
        self.ball.y += final_ny * min(step, dist)

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
            var speed = 2.0
            if "speed" in self.ball: speed = self.ball.speed
            var nx = dx / dist
            var ny = dy / dist
            var step = speed * delta * 60
            _apply_movement(nx, ny, step, dist, true, nearest)
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

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var attack_range = ball_radius + target_radius + 5.0

        if dist > attack_range:
            var nx = dx / dist
            var ny = dy / dist
            var step = speed * delta * 60
            _apply_movement(nx, ny, step, dist, false, target)

            dx = target.x - self.ball.x
            dy = target.y - self.ball.y
            dist = sqrt(dx*dx + dy*dy)

        if dist <= attack_range + 0.01:
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

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var collect_range = ball_radius + 10.0

        if dist > collect_range:
            var nx = dx / dist
            var ny = dy / dist
            var step = speed * delta * 60
            _apply_movement(nx, ny, step, dist, false, nearest)

            dx = nearest.x - self.ball.x
            dy = nearest.y - self.ball.y
            dist = sqrt(dx*dx + dy*dy)

        if dist <= collect_range + 0.01:
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
            var skill_cooldown = 5.0
            if "skill_cooldown" in self.ball: skill_cooldown = self.ball.skill_cooldown
            self.ball.skill_timer = skill_cooldown

func _idle(delta: float):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var nx = randf_range(-1.0, 1.0)
    var ny = randf_range(-1.0, 1.0)
    var m = sqrt(nx*nx + ny*ny)
    if m > 0.01:
        nx /= m
        ny /= m
    else:
        nx = 0.0
        ny = 0.0
    var step = speed * 0.3
    _apply_movement(nx, ny, step, step, true)

func _clamp_position():
    if is_nan(self.ball.x) or is_inf(self.ball.x): self.ball.x = 0.0
    if is_nan(self.ball.y) or is_inf(self.ball.y): self.ball.y = 0.0

    if self.world != null and "width" in self.world and "height" in self.world:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius
        self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
        self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta
