class_name Perception
extends RefCounted

# Scans the world: finds nearby enemies, allies, boosters, traps.
# Calculates distances, threat levels, opportunity scores.
# Each ball has perception radius based on type.

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func get_perception_radius() -> float:
    if "perception_radius" in self.ball:
        return float(self.ball.perception_radius)
    return 300.0 # default radius

func scan() -> Dictionary:
    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    var radius = get_perception_radius()

    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    var enemies = data["enemies"]
    var boosters = data["boosters"]
    var allies = data["allies"]
    var traps = data["traps"]

    var danger_score = 0.0
    for e in enemies:
        var dist = _calc_distance(e, radius)
        danger_score += 1.0 * (1.0 - min(dist / radius, 1.0))

    for t in traps:
        var dist = _calc_distance(t, radius)
        danger_score += 1.5 * (1.0 - min(dist / radius, 1.0))

    var opp_score = 0.0
    for b in boosters:
        var dist = _calc_distance(b, radius)
        opp_score += 1.5 * (1.0 - min(dist / radius, 1.0))

    for a in allies:
        var dist = _calc_distance(a, radius)
        opp_score += 0.5 * (1.0 - min(dist / radius, 1.0))

    # Fallback to simple calculation if distances couldn't be calculated (or scores are exactly 0 but entities exist)
    if danger_score == 0.0 and enemies.size() > 0:
        danger_score = enemies.size() * 0.2

    if opp_score == 0.0 and (boosters.size() > 0 or allies.size() > 0):
        opp_score = boosters.size() * 0.3 + allies.size() * 0.1

    data["danger_level"] = danger_score
    data["opportunity_level"] = opp_score

    return data

func _calc_distance(entity, default_dist: float) -> float:
    if "position" in self.ball and "position" in entity:
        if typeof(self.ball.position) == TYPE_VECTOR2 and typeof(entity.position) == TYPE_VECTOR2:
            return self.ball.position.distance_to(entity.position)
    return default_dist
