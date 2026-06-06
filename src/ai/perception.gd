class_name Perception
extends RefCounted

# Perception system for balls.
# Scans the world to find nearby enemies, allies, boosters, and traps.
# Calculates distances, threat levels, and opportunity scores.

var ball
var world

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func scan() -> Dictionary:
    var radius = 300.0
    if "perception_radius" in self.ball:
        radius = float(self.ball.perception_radius)

    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    var danger_level = 0.0
    var opportunity_level = 0.0

    var bx = 0.0
    var by = 0.0
    if "x" in self.ball: bx = float(self.ball.x)
    if "y" in self.ball: by = float(self.ball.y)

    for enemy in data["enemies"]:
        var ex = 0.0
        var ey = 0.0
        if "x" in enemy: ex = float(enemy.x)
        if "y" in enemy: ey = float(enemy.y)
        var dist = sqrt(pow(bx - ex, 2) + pow(by - ey, 2))
        var dist_factor = 0.0
        if radius > 0:
            dist_factor = max(0.0, 1.0 - (dist / radius))

        var base_threat = 0.1
        if "damage" in enemy:
            base_threat = float(enemy.damage) / 100.0
        danger_level += base_threat * dist_factor + 0.1

    for trap in data["traps"]:
        var tx = 0.0
        var ty = 0.0
        if "x" in trap: tx = float(trap.x)
        if "y" in trap: ty = float(trap.y)
        var dist = sqrt(pow(bx - tx, 2) + pow(by - ty, 2))
        var dist_factor = 0.0
        if radius > 0:
            dist_factor = max(0.0, 1.0 - (dist / radius))
        danger_level += 0.5 * dist_factor

    for booster in data["boosters"]:
        var boox = 0.0
        var booy = 0.0
        if "x" in booster: boox = float(booster.x)
        if "y" in booster: booy = float(booster.y)
        var dist = sqrt(pow(bx - boox, 2) + pow(by - booy, 2))
        var dist_factor = 0.0
        if radius > 0:
            dist_factor = max(0.0, 1.0 - (dist / radius))
        opportunity_level += 0.3 * dist_factor + 0.1

    for ally in data["allies"]:
        var ax = 0.0
        var ay = 0.0
        if "x" in ally: ax = float(ally.x)
        if "y" in ally: ay = float(ally.y)
        var dist = sqrt(pow(bx - ax, 2) + pow(by - ay, 2))
        var dist_factor = 0.0
        if radius > 0:
            dist_factor = max(0.0, 1.0 - (dist / radius))
        opportunity_level += 0.1 * dist_factor

    data["danger_level"] = danger_level
    data["opportunity_level"] = opportunity_level

    return data
