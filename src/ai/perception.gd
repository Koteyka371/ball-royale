class_name Perception
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func scan() -> Dictionary:
    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "nearest_enemy": null,
        "nearest_booster": null,
        "nearest_ally": null
    }

    var radius = 300.0
    if "perception_radius" in self.ball:
        radius = self.ball.perception_radius

    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    # Sort and find nearest
    var ball_x = 0.0
    var ball_y = 0.0

    if "position" in self.ball:
        ball_x = self.ball.position.x
        ball_y = self.ball.position.y
    elif "x" in self.ball and "y" in self.ball:
        ball_x = self.ball.x
        ball_y = self.ball.y

    # Custom sorter class because Godot 4.x sort_custom uses Callables
    # Since we can't easily inline lambda for arrays, we use a simple loop approach

    # Sort enemies
    if data["enemies"].size() > 0:
        var nearest = null
        var min_dist = INF
        for e in data["enemies"]:
            var ex = e.position.x if "position" in e else e.x if "x" in e else 0.0
            var ey = e.position.y if "position" in e else e.y if "y" in e else 0.0
            var dist_sq = (ex - ball_x) * (ex - ball_x) + (ey - ball_y) * (ey - ball_y)
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest = e
        data["nearest_enemy"] = nearest

    # Sort boosters
    if data["boosters"].size() > 0:
        var nearest = null
        var min_dist = INF
        for b in data["boosters"]:
            var bx = b.position.x if "position" in b else b.x if "x" in b else 0.0
            var by = b.position.y if "position" in b else b.y if "y" in b else 0.0
            var dist_sq = (bx - ball_x) * (bx - ball_x) + (by - ball_y) * (by - ball_y)
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest = b
        data["nearest_booster"] = nearest

    # Sort allies
    if data["allies"].size() > 0:
        var nearest = null
        var min_dist = INF
        for a in data["allies"]:
            var ax = a.position.x if "position" in a else a.x if "x" in a else 0.0
            var ay = a.position.y if "position" in a else a.y if "y" in a else 0.0
            var dist_sq = (ax - ball_x) * (ax - ball_x) + (ay - ball_y) * (ay - ball_y)
            if dist_sq < min_dist:
                min_dist = dist_sq
                nearest = a
        data["nearest_ally"] = nearest

    data["danger_level"] = data["enemies"].size() * 0.2
    data["opportunity_level"] = data["boosters"].size() * 0.3 + data["allies"].size() * 0.1

    return data
