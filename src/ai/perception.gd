class_name Perception
extends RefCounted

# Perception system for balls.
# Scans the world to find nearby enemies, allies, boosters, and traps.
# Calculates distances, threat levels, and opportunity scores.

var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

func scan() -> Dictionary:
    # Scans the environment within the ball's perception radius.
    # Returns a dictionary with parsed data.
    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    if not self.world or not self.world.has_method("get_nearby_entities"):
        return data

    var radius = 300.0
    if "perception_radius" in self.ball:
        radius = self.ball.perception_radius

    var entities = self.world.get_nearby_entities(self.ball, radius)

    # Parse entities and calculate distances
    data["enemies"] = _process_entities(entities.get("enemies", []), true)
    data["allies"] = _process_entities(entities.get("allies", []), false)
    data["boosters"] = _process_entities(entities.get("boosters", []), false)
    data["traps"] = _process_entities(entities.get("traps", []), true)

    # Calculate danger and opportunity levels
    data["danger_level"] = _calculate_danger(data["enemies"], data["traps"])
    data["opportunity_level"] = _calculate_opportunity(data["boosters"], data["allies"])

    return data

func _process_entities(entities: Array, is_threat: bool) -> Array:
    # Processes a list of entities, calculating distances and returning enriched dicts.
    var processed = []

    var bx = 0.0
    var by = 0.0
    if "x" in self.ball and "y" in self.ball:
        bx = self.ball.x
        by = self.ball.y
    elif "global_position" in self.ball:
        bx = self.ball.global_position.x
        by = self.ball.global_position.y

    for entity in entities:
        var ex = 0.0
        var ey = 0.0

        if typeof(entity) == TYPE_DICTIONARY:
            ex = entity.get("x", 0)
            ey = entity.get("y", 0)
        elif "x" in entity and "y" in entity:
            ex = entity.x
            ey = entity.y
        elif "global_position" in entity:
            ex = entity.global_position.x
            ey = entity.global_position.y

        var dx = ex - bx
        var dy = ey - by
        var dist = sqrt(dx*dx + dy*dy)

        processed.append({
            "entity": entity,
            "distance": dist,
            "direction": Vector2(dx, dy)
        })

    # Sort by distance (closest first)
    processed.sort_custom(Callable(self, "_sort_by_distance"))
    return processed

func _sort_by_distance(a: Dictionary, b: Dictionary) -> bool:
    return a["distance"] < b["distance"]

func _calculate_danger(enemies: Array, traps: Array) -> float:
    # Calculates danger level based on nearby threats.
    var danger = 0.0

    # Enemies are dangerous, especially if close
    for e in enemies:
        var dist = max(e["distance"], 1.0) # Prevent div by 0
        danger += min(1.0, 50.0 / dist)

    # Traps are very dangerous if very close
    for t in traps:
        var dist = max(t["distance"], 1.0)
        if dist < 50.0:
            danger += min(1.0, 50.0 / dist)

    return danger

func _calculate_opportunity(boosters: Array, allies: Array) -> float:
    # Calculates opportunity level based on nearby resources and support.
    var opportunity = 0.0

    # Boosters are good opportunities, especially if close
    for b in boosters:
        var dist = max(b["distance"], 1.0)
        opportunity += min(1.0, 100.0 / dist)

    # Allies provide small opportunity/safety
    opportunity += allies.size() * 0.1

    return opportunity
