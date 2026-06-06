class_name Perception
extends RefCounted

# Perception system for balls.
# Scans the world, finds nearby entities, and calculates threat/opportunity scores.

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func scan() -> Dictionary:
    # Scans environment for entities (enemies, allies, boosters).
    # Calculates danger and opportunity levels based on distances and stats.

    var radius = 300.0
    if "PERCEPTION_RADIUS" in self.ball:
        radius = self.ball.PERCEPTION_RADIUS

    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "closest_enemy_dist": INF,
        "closest_ally_dist": INF,
        "closest_booster_dist": INF,
        "closest_trap_dist": INF
    }

    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, radius)
        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    # Process enemies to calculate danger
    var danger = 0.0
    for enemy in data["enemies"]:
        var dist = _calculate_distance(self.ball, enemy)
        data["closest_enemy_dist"] = min(data["closest_enemy_dist"], dist)

        var threat = 0.2
        if dist < radius:
            threat += 0.2 * (1.0 - (dist / radius))

        var damage = 10.0
        if "DAMAGE" in enemy:
            damage = enemy.DAMAGE

        threat *= (damage / 10.0)
        danger += threat

    # Process traps to calculate danger
    for trap in data["traps"]:
        if typeof(trap) == TYPE_INT or typeof(trap) == TYPE_FLOAT:
            danger += 0.5
            continue

        var dist = _calculate_distance(self.ball, trap)
        data["closest_trap_dist"] = min(data["closest_trap_dist"], dist)

        var threat = 0.5
        if dist < radius:
            threat += 0.5 * (1.0 - (dist / radius))

        var damage = 20.0
        if "DAMAGE" in trap:
            damage = trap.DAMAGE

        threat *= (damage / 10.0)
        danger += threat

    data["danger_level"] = danger

    # Process boosters to calculate opportunity
    var opportunity = 0.0
    for booster in data["boosters"]:
        # Simple mocking check, if it's not an object (dictionary or node)
        if typeof(booster) == TYPE_INT or typeof(booster) == TYPE_FLOAT:
            opportunity += 0.3
            continue

        var dist = _calculate_distance(self.ball, booster)
        data["closest_booster_dist"] = min(data["closest_booster_dist"], dist)

        var opp = 0.3
        if dist < radius:
            opp += 0.2 * (1.0 - (dist / radius))
        opportunity += opp

    # Process allies to calculate opportunity
    for ally in data["allies"]:
        var dist = _calculate_distance(self.ball, ally)
        data["closest_ally_dist"] = min(data["closest_ally_dist"], dist)

        var opp = 0.1
        if dist < radius:
            opp += 0.1 * (1.0 - (dist / radius))
        opportunity += opp

    data["opportunity_level"] = opportunity

    return data

func _calculate_distance(entity1, entity2) -> float:
    # Calculates distance between two entities using position if available.
    # Checks for global_position first (Godot nodes), then falls back to x/y.
    if "global_position" in entity1 and "global_position" in entity2:
        return entity1.global_position.distance_to(entity2.global_position)
    elif "position" in entity1 and "position" in entity2:
        return entity1.position.distance_to(entity2.position)
    elif "x" in entity1 and "y" in entity1 and "x" in entity2 and "y" in entity2:
        var dx = entity1.x - entity2.x
        var dy = entity1.y - entity2.y
        return sqrt(dx*dx + dy*dy)

    return INF
