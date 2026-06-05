class_name Perception
extends Node

# Reference to the ball and world
var ball = null
var world = null

func _init(ball_ref, world_ref):
    self.ball = ball_ref
    self.world = world_ref

# Scans the environment within the ball's perception_radius.
# Returns a dictionary containing discovered entities and calculated scores.
func scan() -> Dictionary:
    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "distances": {},
        "danger_level": 0.0,
        "opportunity_level": 0.0
    }

    # Default perception radius if not explicitly set on ball
    var perception_radius = 300.0
    if "perception_radius" in self.ball:
        perception_radius = self.ball.perception_radius

    if self.world and self.world.has_method("get_nearby_entities"):
        var entities = self.world.get_nearby_entities(self.ball, perception_radius)

        data["enemies"] = entities.get("enemies", [])
        data["allies"] = entities.get("allies", [])
        data["boosters"] = entities.get("boosters", [])
        data["traps"] = entities.get("traps", [])

    # Calculate distances and normalize scores based on proximity

    # Danger level
    var danger = 0.0
    for enemy in data["enemies"]:
        var dist = _calculate_distance(self.ball, enemy)
        if enemy:
            var enemy_id = enemy.get_instance_id() if enemy is Object else enemy.id
            data["distances"][enemy_id] = dist
        if dist <= perception_radius:
            # Closer enemies contribute more to danger
            danger += max(0.0, 1.0 - (dist / perception_radius)) * 0.5

    # Traps also add to danger
    for trap in data["traps"]:
        var dist = _calculate_distance(self.ball, trap)
        if trap:
            var trap_id = trap.get_instance_id() if trap is Object else trap.id
            data["distances"][trap_id] = dist
        if dist <= perception_radius:
            danger += max(0.0, 1.0 - (dist / perception_radius)) * 0.8

    data["danger_level"] = min(1.0, danger)

    # Opportunity level
    var opportunity = 0.0
    for booster in data["boosters"]:
        var dist = _calculate_distance(self.ball, booster)
        if booster:
            var booster_id = booster.get_instance_id() if booster is Object else booster.id
            data["distances"][booster_id] = dist
        if dist <= perception_radius:
            # Closer boosters contribute more to opportunity
            opportunity += max(0.0, 1.0 - (dist / perception_radius)) * 0.6

    for ally in data["allies"]:
        var dist = _calculate_distance(self.ball, ally)
        if ally:
            var ally_id = ally.get_instance_id() if ally is Object else ally.id
            data["distances"][ally_id] = dist
        if dist <= perception_radius:
            opportunity += max(0.0, 1.0 - (dist / perception_radius)) * 0.2

    data["opportunity_level"] = min(1.0, opportunity)

    return data

# Helper to calculate distance between two entities
func _calculate_distance(entity1, entity2) -> float:
    var x1 = 0.0
    var y1 = 0.0
    if "x" in entity1:
        x1 = entity1.x
    elif "position" in entity1:
        x1 = entity1.position.x

    if "y" in entity1:
        y1 = entity1.y
    elif "position" in entity1:
        y1 = entity1.position.y

    var x2 = 0.0
    var y2 = 0.0
    if "x" in entity2:
        x2 = entity2.x
    elif "position" in entity2:
        x2 = entity2.position.x

    if "y" in entity2:
        y2 = entity2.y
    elif "position" in entity2:
        y2 = entity2.position.y

    return sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))
