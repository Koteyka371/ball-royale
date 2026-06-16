class_name Perception
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func scan() -> Dictionary:
    var perception_radius = 300.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "distances": {}, # Need custom handling to map objects to distances
        "threat_level": 0.0,
        "opportunity_score": 0.0,
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    if not self.world or not self.world.has_method("get_nearby_entities"):
        return data

    var entities = self.world.get_nearby_entities(self.ball, perception_radius)
    data["enemies"] = entities.get("enemies", [])
    data["allies"] = entities.get("allies", [])
    data["boosters"] = entities.get("boosters", [])
    data["traps"] = entities.get("traps", [])

    var bx = 0.0
    var by = 0.0
    if "x" in self.ball and "y" in self.ball:
        bx = self.ball.x
        by = self.ball.y

    var threat = 0.0
    var opp = 0.0

    for enemy in data["enemies"]:
        var dist = 0.0
        if "x" in enemy and "y" in enemy:
            var dx = enemy.x - bx
            var dy = enemy.y - by
            dist = sqrt(dx*dx + dy*dy)
            if "id" in enemy:
                data["distances"][enemy.id] = dist
        threat += max(0.0, 1.0 - (dist / perception_radius)) * 1.5

    for trap in data["traps"]:
        var dist = 0.0
        if "x" in trap and "y" in trap:
            var dx = trap.x - bx
            var dy = trap.y - by
            dist = sqrt(dx*dx + dy*dy)
            if "id" in trap:
                data["distances"][trap.id] = dist
        threat += max(0.0, 1.0 - (dist / perception_radius)) * 2.0

    for booster in data["boosters"]:
        var dist = 0.0
        if "x" in booster and "y" in booster:
            var dx = booster.x - bx
            var dy = booster.y - by
            dist = sqrt(dx*dx + dy*dy)
            if "id" in booster:
                data["distances"][booster.id] = dist
        opp += max(0.0, 1.0 - (dist / perception_radius)) * 1.0

    for ally in data["allies"]:
        var dist = 0.0
        if "x" in ally and "y" in ally:
            var dx = ally.x - bx
            var dy = ally.y - by
            dist = sqrt(dx*dx + dy*dy)
            if "id" in ally:
                data["distances"][ally.id] = dist
        opp += max(0.0, 1.0 - (dist / perception_radius)) * 0.5

    data["threat_level"] = threat
    data["opportunity_score"] = opp

    data["team_messages"] = []
    for ally in data["allies"]:
        if ally.has_method("has_meta") and ally.has_meta("team_message"):
            var msg = ally.get_meta("team_message")
            if msg != null:
                data["team_messages"].append(msg)

    data["danger_level"] = data["enemies"].size() * 0.2

    data["opportunity_level"] = data["boosters"].size() * 0.3 + data["allies"].size() * 0.1

    return data
