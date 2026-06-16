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

func _calculate_steering(target_x: float, target_y: float, target_ent = null, flee: bool = false) -> Vector2:
    var dx = target_x - self.ball.x
    var dy = target_y - self.ball.y
    var dist = sqrt(dx * dx + dy * dy)

    var nx = 0.0
    var ny = 0.0
    if dist > 0.0:
        nx = dx / dist
        ny = dy / dist
        if flee:
            nx = -nx
            ny = -ny

    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    var entities = []
    if self.world != null and self.world.has_method("get_nearby_entities"):
        var entities_dict = self.world.get_nearby_entities(self.ball, perception_radius)
        if typeof(entities_dict) == TYPE_DICTIONARY:
            if entities_dict.has("enemies"):
                entities.append_array(entities_dict["enemies"])
            if entities_dict.has("allies"):
                entities.append_array(entities_dict["allies"])
            if entities_dict.has("boosters"):
                entities.append_array(entities_dict["boosters"])
            if entities_dict.has("traps"):
                entities.append_array(entities_dict["traps"])
        elif typeof(entities_dict) == TYPE_ARRAY:
            entities.append_array(entities_dict)

    var repulse_x = 0.0
    var repulse_y = 0.0

    for e in entities:
        if e == target_ent or e == self.ball:
            continue

        if not ("x" in e and "y" in e):
            continue

        var ex = e.x
        var ey = e.y
        if is_nan(ex) or is_nan(ey):
            continue

        var edx = self.ball.x - ex
        var edy = self.ball.y - ey
        var edist = sqrt(edx * edx + edy * edy)

        var avoid_radius = 10.0 + 10.0 + 10.0
        if "radius" in self.ball:
            avoid_radius = self.ball.radius + 10.0
        if "radius" in e:
            avoid_radius += e.radius

        if edist > 0.0 and edist < avoid_radius:
            repulse_x += (edx / edist) * (avoid_radius - edist)
            repulse_y += (edy / edist) * (avoid_radius - edist)
        elif edist == 0.0:
            repulse_x += randf_range(-1.0, 1.0)
            repulse_y += randf_range(-1.0, 1.0)

    var combined_x = nx + repulse_x * 0.5
    var combined_y = ny + repulse_y * 0.5

    var cdist = sqrt(combined_x * combined_x + combined_y * combined_y)
    if cdist > 0.0:
        combined_x /= cdist
        combined_y /= cdist
    else:
        combined_x = 0.0
        combined_y = 0.0

    if is_nan(combined_x) or is_inf(combined_x):
        combined_x = 0.0
    if is_nan(combined_y) or is_inf(combined_y):
        combined_y = 0.0

    return Vector2(combined_x, combined_y)

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

        var dir = _calculate_steering(nearest.x, nearest.y, nearest, true)
        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        self.ball.x += dir.x * speed * delta * 60
        self.ball.y += dir.y * speed * delta * 60
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
            var dir = _calculate_steering(target.x, target.y, target, false)
            var step = speed * delta * 60

            var move_dist = min(step, dist - attack_range)
            self.ball.x += dir.x * move_dist
            self.ball.y += dir.y * move_dist

        if dist <= attack_range:
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

        if dist > 0.01:
            var dir = _calculate_steering(nearest.x, nearest.y, nearest, false)
            var step = speed * delta * 60
            self.ball.x += dir.x * min(step, dist)
            self.ball.y += dir.y * min(step, dist)

        if dist <= collect_range:
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
    self.ball.x += randf_range(-1.0, 1.0) * speed * 0.3
    self.ball.y += randf_range(-1.0, 1.0) * speed * 0.3

func _clamp_position():
    if self.world != null and "width" in self.world and "height" in self.world:
        if is_nan(self.ball.x) or is_inf(self.ball.x):
            self.ball.x = self.world.width / 2.0
        if is_nan(self.ball.y) or is_inf(self.ball.y):
            self.ball.y = self.world.height / 2.0

        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius
        self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
        self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta
