class_name Perception
extends RefCounted

# Reference to the ball this perception belongs to
var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

# Scans environment for entities
# Calculates danger and opportunity levels
func scan() -> Dictionary:
    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    # Determine perception radius
    var radius = 300.0
    if "perception_radius" in self.ball:
        radius = float(self.ball.perception_radius)
    elif "PERCEPTION_RADIUS" in self.ball:
        radius = float(self.ball.PERCEPTION_RADIUS)

    # In a real implementation, we would query the world
    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    var danger_level = 0.0
    for e in data["enemies"]:
        var dist = 0.0
        if "position" in self.ball and "position" in e:
            dist = self.ball.position.distance_to(e.position)
        elif "x" in self.ball and "y" in self.ball and "x" in e and "y" in e:
            var dx = self.ball.x - e.x
            var dy = self.ball.y - e.y
            dist = sqrt(dx * dx + dy * dy)

        if dist <= radius:
            var threat = 1.0 - (dist / max(1.0, radius))
            danger_level += threat * 0.5

    for t in data["traps"]:
        var dist = 0.0
        if "position" in self.ball and "position" in t:
            dist = self.ball.position.distance_to(t.position)
        elif "x" in self.ball and "y" in self.ball and "x" in t and "y" in t:
            var dx = self.ball.x - t.x
            var dy = self.ball.y - t.y
            dist = sqrt(dx * dx + dy * dy)

        if dist <= radius:
            var threat = 1.0 - (dist / max(1.0, radius))
            danger_level += threat * 0.8

    if data["enemies"].size() > 0 and danger_level == 0.0:
        danger_level = data["enemies"].size() * 0.2

    var opportunity_level = 0.0
    for b in data["boosters"]:
        var dist = 0.0
        if "position" in self.ball and "position" in b:
            dist = self.ball.position.distance_to(b.position)
        elif "x" in self.ball and "y" in self.ball and "x" in b and "y" in b:
            var dx = self.ball.x - b.x
            var dy = self.ball.y - b.y
            dist = sqrt(dx * dx + dy * dy)

        if dist <= radius:
            var opp = 1.0 - (dist / max(1.0, radius))
            opportunity_level += opp * 0.5

    for a in data["allies"]:
        var dist = 0.0
        if "position" in self.ball and "position" in a:
            dist = self.ball.position.distance_to(a.position)
        elif "x" in self.ball and "y" in self.ball and "x" in a and "y" in a:
            var dx = self.ball.x - a.x
            var dy = self.ball.y - a.y
            dist = sqrt(dx * dx + dy * dy)

        if dist <= radius:
            var opp = 1.0 - (dist / max(1.0, radius))
            opportunity_level += opp * 0.2

    if (data["boosters"].size() > 0 or data["allies"].size() > 0) and opportunity_level == 0.0:
        opportunity_level = data["boosters"].size() * 0.3 + (data["allies"].size() * 0.1)

    data["danger_level"] = danger_level
    data["opportunity_level"] = opportunity_level

    return data
