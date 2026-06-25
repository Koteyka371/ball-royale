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

    if self.world != null and "arena" in self.world and "is_night" in self.world.arena:
        if self.world.arena.is_night:
            perception_radius = min(perception_radius, 100.0)
        else:
            perception_radius = max(perception_radius, 2000.0)

    var data = {
        "enemies": [],
        "allies": [],
        "boosters": [],
        "traps": [],
        "distances": {}, # Need custom handling to map objects to distances
        "threat_level": 0.0,
        "opportunity_score": 0.0,
        "coach_strategy": "",
        "danger_level": 0.0,
        "opportunity_level": 0.0,
        "rival_spotted": false
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

    var calc_dist = func(ent):
        if "x" in ent and "y" in ent:
            var dx = ent.x - bx
            var dy = ent.y - by
            return sqrt(dx*dx + dy*dy)
        return 0.0

    var threat = 0.0
    var opp = 0.0

    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
        for h in self.world.arena.hazards:
            var dist = calc_dist.call(h)

            if dist <= perception_radius:
                var found = false
                for t in data["traps"]:
                    if "id" in t and "id" in h and t.id == h.id:
                        found = true
                        break
                if not found:
                    data["traps"].append(h)

    var my_memory = {}
    if self.ball.has_method("get_meta") and self.ball.has_meta("memory"):
        my_memory = self.ball.get_meta("memory")
    elif "memory" in self.ball:
        my_memory = self.ball.memory

    for enemy in data["enemies"]:
        var dist = calc_dist.call(enemy)
        if "id" in enemy:
            data["distances"][enemy.id] = dist
            # Ball Relationships - Balls remember each other
            # Rivalry skill: attacked me before -> attack on sight
            if my_memory.has(enemy.id):
                var rel_data = my_memory[enemy.id]
                if typeof(rel_data) == TYPE_DICTIONARY and rel_data.get("relation") == "rival":
                    data["rival_spotted"] = true
        threat += max(0.0, 1.0 - (dist / perception_radius)) * 1.5

    for trap in data["traps"]:
        var dist = calc_dist.call(trap)
        if "id" in trap:
            data["distances"][trap.id] = dist
        threat += max(0.0, 1.0 - (dist / perception_radius)) * 2.0

    for booster in data["boosters"]:
        var dist = calc_dist.call(booster)
        if "id" in booster:
            data["distances"][booster.id] = dist
        opp += max(0.0, 1.0 - (dist / perception_radius)) * 1.0

    var team_messages = []

    for ally in data["allies"]:
        var dist = calc_dist.call(ally)
        if "id" in ally:
            data["distances"][ally.id] = dist
        opp += max(0.0, 1.0 - (dist / perception_radius)) * 0.5
        if ally.has_method("has_meta") and ally.has_meta("team_message"):
            var msg = ally.get_meta("team_message")
            if msg != null:
                team_messages.append(msg)

    data["threat_level"] = threat
    data["opportunity_score"] = opp

    # Coach Mode
    if self.world != null and "coach_strategy" in self.world and self.world.coach_strategy:
        var strat = self.world.coach_strategy
        if typeof(strat) == TYPE_DICTIONARY:
            var team = ""
            if "team" in self.ball:
                team = str(self.ball.team)
            elif "ball_type" in self.ball:
                team = str(self.ball.ball_type)
            elif self.ball.has_method("get_ball_type"):
                team = str(self.ball.get_ball_type())

            if strat.has(team):
                data["coach_strategy"] = str(strat[team])
        elif typeof(strat) == TYPE_STRING:
            data["coach_strategy"] = strat


    data["danger_level"] = data["enemies"].size() * 0.2
    data["opportunity_level"] = data["boosters"].size() * 0.3 + data["allies"].size() * 0.1
    data["team_messages"] = team_messages

    return data
