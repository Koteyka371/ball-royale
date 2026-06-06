class_name Perception
extends RefCounted

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func scan() -> Dictionary:
    var radius = 300.0
    if "perception_radius" in self.ball:
        radius = self.ball.perception_radius

    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "distances": {},
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    if not self.world or not self.world.has_method("get_nearby_entities"):
        return data

    var entities = self.world.get_nearby_entities(self.ball, radius)

    var enemies = entities.get("enemies", [])
    var allies = entities.get("allies", [])
    var boosters = entities.get("boosters", [])
    var traps = entities.get("traps", [])

    data["enemies"] = enemies
    data["allies"] = allies
    data["boosters"] = boosters
    data["traps"] = traps

    var danger = 0.0
    var opportunity = 0.0

    var ball_pos = null
    if "position" in self.ball:
        ball_pos = self.ball.position

    for e in enemies:
        var dist = -1.0
        if ball_pos != null and "position" in e:
            dist = ball_pos.distance_to(e.position)
        data["distances"][e.get_instance_id()] = dist

        var threat = 0.2
        if dist > 0:
            threat += 100.0 / max(dist, 1.0)
        danger += threat

    for t in traps:
        var dist = -1.0
        if ball_pos != null and "position" in t:
            dist = ball_pos.distance_to(t.position)
        data["distances"][t.get_instance_id()] = dist

        var threat = 0.5
        if dist > 0:
            threat += 50.0 / max(dist, 1.0)
        danger += threat

    for b in boosters:
        var dist = -1.0
        if ball_pos != null and "position" in b:
            dist = ball_pos.distance_to(b.position)
        data["distances"][b.get_instance_id()] = dist

        var opp = 0.3
        if dist > 0:
            opp += 100.0 / max(dist, 1.0)
        opportunity += opp

    for a in allies:
        var dist = -1.0
        if ball_pos != null and "position" in a:
            dist = ball_pos.distance_to(a.position)
        data["distances"][a.get_instance_id()] = dist
        opportunity += 0.1

    data["danger_level"] = danger
    data["opportunity_level"] = opportunity

    return data
