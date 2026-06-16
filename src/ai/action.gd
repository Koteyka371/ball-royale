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
                if e != self.ball and (e.has_method("get_ball_type") or "ball_type" in e):
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type != b_type:
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            enemies.append(e)
            return enemies
    return []

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
                if e != self.ball and (e.has_method("get_ball_type") or "ball_type" in e):
                    var e_type = e.ball_type if "ball_type" in e else e.get_ball_type()
                    var b_type = self.ball.ball_type if "ball_type" in self.ball else self.ball.get_ball_type()
                    if e_type == b_type:
                        if ("alive" in e and e.alive) or (e.has_method("is_alive") and e.is_alive()):
                            allies.append(e)
            return allies
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

func _flee(delta: float):
    var enemies = _get_enemies()
    if enemies.size() == 0:
        _idle(delta)
        return

    var nearest_enemy = null
    var min_dist_sq = INF
    for e in enemies:
        var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            nearest_enemy = e

    var dx = self.ball.x - nearest_enemy.x
    var dy = self.ball.y - nearest_enemy.y
    var dist = sqrt(dx*dx + dy*dy)

    var perception_radius = 250.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius
    var safe_distance = perception_radius * 0.8

    if dist > safe_distance:
        _idle(delta * 0.5)
        return

    var ex = 0.0
    var ey = 0.0
    if dist > 0.01:
        ex = dx / dist
        ey = dy / dist

    var allies = _get_allies()
    var ax = 0.0
    var ay = 0.0
    if allies.size() > 0:
        var nearest_ally = null
        var ally_min_dist_sq = INF
        for a in allies:
            var adist_sq = pow(a.x - self.ball.x, 2) + pow(a.y - self.ball.y, 2)
            if adist_sq < ally_min_dist_sq:
                ally_min_dist_sq = adist_sq
                nearest_ally = a

        var adx = nearest_ally.x - self.ball.x
        var ady = nearest_ally.y - self.ball.y
        var adist = sqrt(adx*adx + ady*ady)
        if adist > 0.01:
            ax = adx / adist
            ay = ady / adist

    var cx = 0.0
    var cy = 0.0
    if self.world != null and "width" in self.world and "height" in self.world:
        var center_x = self.world.width / 2.0
        var center_y = self.world.height / 2.0
        var cdx = center_x - self.ball.x
        var cdy = center_y - self.ball.y
        var cdist = sqrt(cdx*cdx + cdy*cdy)
        if cdist > 0.01:
            cx = cdx / cdist
            cy = cdy / cdist

    var vx = ex * 1.0 + ax * 0.5 + cx * 0.2
    var vy = ey * 1.0 + ay * 0.5 + cy * 0.2

    if is_nan(vx) or is_inf(vx): vx = 0.0
    if is_nan(vy) or is_inf(vy): vy = 0.0

    var v_dist = sqrt(vx*vx + vy*vy)
    if v_dist > 0.01:
        vx = vx / v_dist
        vy = vy / v_dist
    else:
        vx = ex
        vy = ey

    var speed = 2.0
    if "speed" in self.ball: speed = self.ball.speed
    speed *= 1.5

    self.ball.x += vx * speed * delta * 60
    self.ball.y += vy * speed * delta * 60

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
            var nx = dx / dist
            var ny = dy / dist
            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        var target_radius = 10.0
        if "radius" in target: target_radius = target.radius
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + target_radius + 5:
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
            var nx = dx / dist
            var ny = dy / dist
            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + 10:
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
        var radius = 10.0
        if "radius" in self.ball: radius = self.ball.radius
        self.ball.x = max(radius, min(self.world.width - radius, self.ball.x))
        self.ball.y = max(radius, min(self.world.height - radius, self.ball.y))

func _update_skill_timer(delta: float):
    if "skill_timer" in self.ball and self.ball.skill_timer > 0:
        self.ball.skill_timer -= delta
