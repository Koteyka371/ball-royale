class_name GhostCompanionManager
extends RefCounted

var ghosts = []
var processed_deaths = {}

class GhostCompanion:
    var owner_id: int
    var team: String
    var x: float
    var y: float
    var target_id = null
    var speed: float = 150.0
    var attach_radius: float = 30.0
    var heal_rate: float = 5.0
    var damage_rate: float = 5.0

    func _init(p_owner_id: int, p_team: String, p_x: float, p_y: float):
        owner_id = p_owner_id
        team = p_team
        x = p_x
        y = p_y

    func update(delta: float, world):
        var balls = []
        if "balls" in world:
            balls = world.balls

        if target_id != null:
            var target = null
            for b in balls:
                var b_id = -1
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("id"): b_id = b["id"]
                elif "id" in b:
                    b_id = b.id

                var b_alive = false
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("alive"): b_alive = b["alive"]
                elif "alive" in b:
                    b_alive = b.alive

                if b_id == target_id and b_alive:
                    target = b
                    break

            if target != null:
                if typeof(target) == TYPE_DICTIONARY:
                    if target.has("x"): x = target["x"]
                    if target.has("y"): y = target["y"]
                else:
                    if "x" in target: x = target.x
                    if "y" in target: y = target.y

                var target_team = ""
                if typeof(target) == TYPE_DICTIONARY:
                    if target.has("team"): target_team = target["team"]
                    elif target.has("ball_type"): target_team = target["ball_type"]
                else:
                    if "team" in target: target_team = target.team
                    elif "ball_type" in target: target_team = target.ball_type

                if target_team == team:
                    if typeof(target) == TYPE_DICTIONARY:
                        if target.has("hp") and target.has("max_hp"):
                            target["hp"] = min(target["max_hp"], target["hp"] + heal_rate * delta)
                    else:
                        if "hp" in target and "max_hp" in target:
                            target.hp = min(target.max_hp, target.hp + heal_rate * delta)
                else:
                    if typeof(target) == TYPE_DICTIONARY:
                        if target.has("hp"):
                            target["hp"] -= damage_rate * delta
                    else:
                        if "hp" in target:
                            target.hp -= damage_rate * delta
            else:
                target_id = null
        else:
            var closest_dist = 999999.0
            var closest_ball = null

            for b in balls:
                var b_alive = false
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("alive"): b_alive = b["alive"]
                elif "alive" in b:
                    b_alive = b.alive

                if not b_alive:
                    continue

                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b["x"]
                    if b.has("y"): by = b["y"]
                else:
                    if "x" in b: bx = b.x
                    if "y" in b: by = b.y

                var dx = bx - x
                var dy = by - y
                var dist = sqrt(dx * dx + dy * dy)

                if dist < closest_dist:
                    closest_dist = dist
                    closest_ball = b

            if closest_ball != null:
                var bx = 0.0
                var by = 0.0
                if typeof(closest_ball) == TYPE_DICTIONARY:
                    if closest_ball.has("x"): bx = closest_ball["x"]
                    if closest_ball.has("y"): by = closest_ball["y"]
                else:
                    if "x" in closest_ball: bx = closest_ball.x
                    if "y" in closest_ball: by = closest_ball.y

                if closest_dist <= attach_radius:
                    if typeof(closest_ball) == TYPE_DICTIONARY:
                        if closest_ball.has("id"): target_id = closest_ball["id"]
                    else:
                        if "id" in closest_ball: target_id = closest_ball.id
                else:
                    var dx = bx - x
                    var dy = by - y
                    var length = sqrt(dx * dx + dy * dy)
                    if length > 0:
                        x += (dx / length) * speed * delta
                        y += (dy / length) * speed * delta

func update(delta: float, world):
    var balls = []
    if "balls" in world:
        balls = world.balls

    for b in balls:
        var b_id = -1
        if typeof(b) == TYPE_DICTIONARY:
            if b.has("id"): b_id = b["id"]
        elif "id" in b:
            b_id = b.id

        var b_alive = true
        if typeof(b) == TYPE_DICTIONARY:
            if b.has("alive"): b_alive = b["alive"]
        elif "alive" in b:
            b_alive = b.alive

        if not b_alive and not processed_deaths.has(b_id):
            processed_deaths[b_id] = true

            var b_team = ""
            if typeof(b) == TYPE_DICTIONARY:
                if b.has("team"): b_team = b["team"]
                elif b.has("ball_type"): b_team = b["ball_type"]
            else:
                if "team" in b: b_team = b.team
                elif "ball_type" in b: b_team = b.ball_type

            var bx = 0.0
            var by = 0.0
            if typeof(b) == TYPE_DICTIONARY:
                if b.has("x"): bx = b["x"]
                if b.has("y"): by = b["y"]
            else:
                if "x" in b: bx = b.x
                if "y" in b: by = b.y

            ghosts.append(GhostCompanion.new(b_id, b_team, bx, by))

    for ghost in ghosts:
        ghost.update(delta, world)
