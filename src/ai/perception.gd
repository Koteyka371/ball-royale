class_name Perception
extends Node

# Perception system for balls
# Scans the world to find nearby enemies, allies, boosters, traps.
# Calculates distances, threat levels, and opportunity scores.

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
        "distances": {},
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    var danger_score = 0.0
    var opportunity_score = 0.0

    var ball_pos = Vector2.ZERO
    if "global_position" in self.ball:
        ball_pos = self.ball.global_position
    elif "position" in self.ball:
        ball_pos = self.ball.position
    elif "x" in self.ball and "y" in self.ball:
        ball_pos = Vector2(self.ball.x, self.ball.y)

    for enemy in data["enemies"]:
        var e_pos = Vector2.ZERO
        if "global_position" in enemy:
            e_pos = enemy.global_position
        elif "position" in enemy:
            e_pos = enemy.position
        elif "x" in enemy and "y" in enemy:
            e_pos = Vector2(enemy.x, enemy.y)

        var dist = ball_pos.distance_to(e_pos)
        data["distances"][enemy.get_instance_id() if enemy is Object else hash(enemy)] = dist

        var dist_factor = 1.0 - min(dist / perception_radius, 1.0) if perception_radius > 0 else 0.0
        var damage = 10.0
        if "damage" in enemy:
            damage = enemy.damage

        danger_score += dist_factor * (damage / 10.0) * 0.2
        danger_score += 0.2

    for trap in data["traps"]:
        var t_pos = Vector2.ZERO
        if "global_position" in trap:
            t_pos = trap.global_position
        elif "position" in trap:
            t_pos = trap.position
        elif "x" in trap and "y" in trap:
            t_pos = Vector2(trap.x, trap.y)

        var dist = ball_pos.distance_to(t_pos)
        data["distances"][trap.get_instance_id() if trap is Object else hash(trap)] = dist
        var dist_factor = 1.0 - min(dist / perception_radius, 1.0) if perception_radius > 0 else 0.0
        danger_score += dist_factor * 0.5

    for booster in data["boosters"]:
        var b_pos = Vector2.ZERO
        if "global_position" in booster:
            b_pos = booster.global_position
        elif "position" in booster:
            b_pos = booster.position
        elif "x" in booster and "y" in booster:
            b_pos = Vector2(booster.x, booster.y)

        var dist = ball_pos.distance_to(b_pos)
        data["distances"][booster.get_instance_id() if booster is Object else hash(booster)] = dist
        var dist_factor = 1.0 - min(dist / perception_radius, 1.0) if perception_radius > 0 else 0.0
        opportunity_score += dist_factor * 0.3
        opportunity_score += 0.3

    for ally in data["allies"]:
        var a_pos = Vector2.ZERO
        if "global_position" in ally:
            a_pos = ally.global_position
        elif "position" in ally:
            a_pos = ally.position
        elif "x" in ally and "y" in ally:
            a_pos = Vector2(ally.x, ally.y)

        var dist = ball_pos.distance_to(a_pos)
        data["distances"][ally.get_instance_id() if ally is Object else hash(ally)] = dist
        var dist_factor = 1.0 - min(dist / perception_radius, 1.0) if perception_radius > 0 else 0.0
        opportunity_score += dist_factor * 0.1
        opportunity_score += 0.1

    data["danger_level"] = danger_score
    data["opportunity_level"] = opportunity_score

    return data
