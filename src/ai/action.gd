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

func _get_allies() -> Array:
    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities) == TYPE_DICTIONARY and entities.has("allies"):
            return entities["allies"]
        elif typeof(entities) == TYPE_ARRAY:
            var allies = []
            for e in entities:
                if e.has_method("get_ball_type") or "ball_type" in e:
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type == b_type and e != self.ball:
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            allies.append(e)
            return allies
    return []

func _apply_boids(dx: float, dy: float) -> Array:
    var allies = _get_allies()
    if allies.size() == 0:
        return [dx, dy]

    var sep_x = 0.0
    var sep_y = 0.0
    var align_x = 0.0
    var align_y = 0.0
    var coh_x = 0.0
    var coh_y = 0.0

    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    var radius = 10.0
    if "radius" in self.ball:
        radius = self.ball.radius
    var separation_dist = radius * 3.0

    var count = 0
    for ally in allies:
        var adx = self.ball.x - ally.x
        var ady = self.ball.y - ally.y
        var dist_sq = adx * adx + ady * ady

        if dist_sq < 0.0001:
            continue

        var dist = sqrt(dist_sq)

        if dist < perception_radius:
            # Separation
            if dist < separation_dist:
                sep_x += adx / dist
                sep_y += ady / dist

            # Alignment
            if "velocity_x" in ally: align_x += ally.velocity_x
            if "velocity_y" in ally: align_y += ally.velocity_y

            # Cohesion
            coh_x += ally.x
            coh_y += ally.y

            count += 1

    if count > 0:
        # Alignment
        align_x /= count
        align_y /= count
        var align_len = sqrt(align_x * align_x + align_y * align_y)
        if align_len > 0.01:
            align_x /= align_len
            align_y /= align_len

        # Cohesion
        coh_x /= count
        coh_y /= count
        var coh_dx = coh_x - self.ball.x
        var coh_dy = coh_y - self.ball.y
        var coh_len = sqrt(coh_dx * coh_dx + coh_dy * coh_dy)
        if coh_len > 0.01:
            coh_dx /= coh_len
            coh_dy /= coh_len

        var boid_dx = dx + sep_x * 1.5 + align_x * 0.5 + coh_dx * 0.5
        var boid_dy = dy + sep_y * 1.5 + align_y * 0.5 + coh_dy * 0.5

        var boid_len = sqrt(boid_dx * boid_dx + boid_dy * boid_dy)
        if boid_len > 0.01:
            return [boid_dx / boid_len, boid_dy / boid_len]

    return [dx, dy]

func _apply_movement(delta: float, nx: float, ny: float, dist: float, clamp_to_target: bool = true):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var step = speed * delta * 60.0

    var move_dist = min(step, dist) if clamp_to_target else step

    var b_type = ""
    if "ball_type" in self.ball:
        b_type = self.ball.ball_type
    elif self.ball.has_method("get_ball_type"):
        b_type = self.ball.get_ball_type()

    if b_type == "swarm":
        var boids = _apply_boids(nx, ny)
        nx = boids[0]
        ny = boids[1]

    self.ball.x += nx * move_dist
    self.ball.y += ny * move_dist

    self.ball.velocity_x = nx * speed
    self.ball.velocity_y = ny * speed

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
            var nx = dx / dist
            var ny = dy / dist
            _apply_movement(delta, nx, ny, dist, false)
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

        if dist > 0.01:
            var nx = dx / dist
            var ny = dy / dist
            _apply_movement(delta, nx, ny, dist, true)

        var dx_new = target.x - self.ball.x
        var dy_new = target.y - self.ball.y
        var dist_new = sqrt(dx_new*dx_new + dy_new*dy_new)

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

        if dist > 0.01:
            var nx = dx / dist
            var ny = dy / dist
            _apply_movement(delta, nx, ny, dist, true)

        var dx_new = nearest.x - self.ball.x
        var dy_new = nearest.y - self.ball.y
        var dist_new = sqrt(dx_new*dx_new + dy_new*dy_new)

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist_new <= ball_radius + 10.01:
            if self.world != null and self.world.has_method("_collect_booster"):
                self.world._collect_booster(self.ball, nearest)
    else:
        _idle(delta)

func _use_skill():
    if self.ball.has_method("use_skill"):
        self.ball.use_skill()

func _idle(delta: float):
    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    var nx = randf_range(-1.0, 1.0)
    var ny = randf_range(-1.0, 1.0)
    var length = sqrt(nx * nx + ny * ny)
    if length > 0.01:
        nx /= length
        ny /= length

    var dist = speed * 0.3 * delta * 60.0
    _apply_movement(delta, nx, ny, dist, true)

func _clamp_position():
    if self.world != null and "width" in self.world and "height" in self.world:
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius
        self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
        self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta
