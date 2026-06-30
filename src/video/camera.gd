extends RefCounted
class_name CameraSystem

var width: int
var height: int
var x: float
var y: float
var zoom: float = 1.0
var target_id = null
var activity_scores: Dictionary = {}
var smoothing: float = 0.1
var shake_intensity: float = 0.0

func _init(_width: int = 800, _height: int = 600):
    width = _width
    height = _height
    x = width / 2.0
    y = height / 2.0

func update(balls: Array, events: Array) -> void:
    # Decay previous scores
    for b_id in activity_scores.keys():
        activity_scores[b_id] *= 0.9

    for ball in balls:
        var b_id = null
        if typeof(ball) == TYPE_DICTIONARY:
            b_id = ball.get("id", null)
        else:
            b_id = ball.id if "id" in ball else null

        if b_id == null:
            continue

        if not activity_scores.has(b_id):
            activity_scores[b_id] = 0.0

        var hp = 0
        var max_hp = 100
        if typeof(ball) == TYPE_DICTIONARY:
            hp = ball.get("hp", 0)
            max_hp = ball.get("max_hp", 100)
        else:
            hp = ball.hp if "hp" in ball else 0
            max_hp = ball.max_hp if "max_hp" in ball else 100

        if hp <= 0:
            activity_scores[b_id] = 0.0
            continue

        var score_increase = 0.1
        if hp / float(max_hp) < 0.2:
            score_increase += 2.0

        activity_scores[b_id] += score_increase

    for event in events:
        if event.get("type", "") == "kill":
            var killer_id = event.get("killer_id")
            if killer_id != null and activity_scores.has(killer_id):
                activity_scores[killer_id] += 50.0
        elif event.get("type", "") == "damage":
            var victim_id = event.get("victim_id")
            var attacker_id = event.get("attacker_id")
            if victim_id != null and activity_scores.has(victim_id):
                activity_scores[victim_id] += 5.0
            if attacker_id != null and activity_scores.has(attacker_id):
                activity_scores[attacker_id] += 5.0
        elif event.get("type", "") == "skill":
            var actor_id = event.get("ball_id")
            if actor_id != null and activity_scores.has(actor_id):
                activity_scores[actor_id] += 10.0
        elif event.get("type", "") == "earthquake":
            var intensity = event.get("intensity", 1.0)
            shake_intensity += intensity * 50.0

    shake_intensity = max(0.0, shake_intensity - 2.0)

    var best_score = -1.0
    var best_id = null
    for ball in balls:
        var b_id = null
        var hp = 0
        if typeof(ball) == TYPE_DICTIONARY:
            b_id = ball.get("id", null)
            hp = ball.get("hp", 0)
        else:
            b_id = ball.id if "id" in ball else null
            hp = ball.hp if "hp" in ball else 0

        if b_id != null and hp > 0:
            var score = activity_scores.get(b_id, 0.0)
            if score > best_score:
                best_score = score
                best_id = b_id

    if best_id != null:
        target_id = best_id

    if target_id != null:
        var target_ball = null
        for ball in balls:
            var b_id = null
            if typeof(ball) == TYPE_DICTIONARY:
                b_id = ball.get("id", null)
            else:
                b_id = ball.id if "id" in ball else null

            if b_id == target_id:
                target_ball = ball
                break

        if target_ball != null:
            var tx = x
            var ty = y
            if typeof(target_ball) == TYPE_DICTIONARY:
                tx = target_ball.get("x", x)
                ty = target_ball.get("y", y)
            else:
                tx = target_ball.x if "x" in target_ball else x
                ty = target_ball.y if "y" in target_ball else y

            x += (tx - x) * smoothing
            y += (ty - y) * smoothing

            var target_zoom = 1.0 + min(1.0, best_score / 100.0)
            zoom += (target_zoom - zoom) * smoothing

func get_state() -> Dictionary:
    var ox = 0.0
    var oy = 0.0
    if shake_intensity > 0:
        ox = randf_range(-shake_intensity, shake_intensity)
        oy = randf_range(-shake_intensity, shake_intensity)
    return {
        "x": x + ox,
        "y": y + oy,
        "zoom": zoom,
        "target_id": target_id
    }
