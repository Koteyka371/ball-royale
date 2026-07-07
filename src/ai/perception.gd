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

    var has_sonar = false
    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("sonar_ping_timer"):
        has_sonar = float(self.ball.get_meta("sonar_ping_timer")) > 0
    elif typeof(self.ball) == TYPE_DICTIONARY and "sonar_ping_timer" in self.ball:
        has_sonar = float(self.ball["sonar_ping_timer"]) > 0
    elif "sonar_ping_timer" in self.ball and self.ball.sonar_ping_timer != null:
        has_sonar = float(self.ball.sonar_ping_timer) > 0

    if has_sonar:
        perception_radius = max(perception_radius, 1500.0)

    var is_lunar = false
    if self.world != null and "arena" in self.world and "is_lunar_eclipse" in self.world.arena:
        is_lunar = self.world.arena.is_lunar_eclipse
        if is_lunar:
            perception_radius = 999999.0

    if self.world != null and "arena" in self.world and "is_night" in self.world.arena:
        var has_night_vision = false
        if "traits" in self.ball and typeof(self.ball.traits) == TYPE_ARRAY and self.ball.traits.has("night_vision"):
            has_night_vision = true
        if "ball_type" in self.ball and self.ball.ball_type == "vampire":
            has_night_vision = true
        if "cosmetic" in self.ball:
            var c_val = str(self.ball.cosmetic).to_lower().replace(" ", "_")
            if c_val == "night_vision_goggles" or c_val == "lantern":
                has_night_vision = true
        if "light_source_booster_timer" in self.ball and float(self.ball.light_source_booster_timer) > 0.0:
            has_night_vision = true
        elif typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("get_meta") and self.ball.has_meta("light_source_booster_timer") and float(self.ball.get_meta("light_source_booster_timer")) > 0.0:
            has_night_vision = true

        if "is_lunar_eclipse" in self.world.arena and self.world.arena.is_lunar_eclipse:
            perception_radius = max(perception_radius, 2000.0)
        elif "is_eclipse" in self.world.arena and self.world.arena.is_eclipse:
            perception_radius = min(perception_radius, 20.0)
        elif self.world.arena.is_night:
            if not has_night_vision:
                var night_ratio = 1.0
                if "night_ratio" in self.world.arena:
                    night_ratio = float(self.world.arena.night_ratio)
                elif typeof(self.world.arena) != TYPE_DICTIONARY and self.world.arena.has_method("get_meta") and self.world.arena.has_meta("night_ratio"):
                    night_ratio = float(self.world.arena.get_meta("night_ratio"))
                perception_radius = max(100.0, perception_radius * (1.0 - night_ratio * 0.8))
        else:
            perception_radius = max(perception_radius, 2000.0)


    var cosmetic = ""
    if "cosmetic" in self.ball:
        cosmetic = str(self.ball.cosmetic).to_lower().replace(" ", "_")
    var ignores_fog = cosmetic == "thermal_goggles"
    var ignores_sandstorm = cosmetic in ["desert_goggles", "sand_goggles"]
    var ignores_snow = cosmetic in ["snow_goggles", "ski_goggles"]
    var ignores_rain = cosmetic in ["rain_goggles", "waterproof_goggles"]

    if self.world != null and "arena" in self.world and "is_foggy" in self.world.arena:
        if self.world.arena.is_foggy and not ignores_fog and not is_lunar:
            perception_radius = min(perception_radius, 80.0)
    if self.world != null and "arena" in self.world and "is_raining" in self.world.arena:
        if self.world.arena.is_raining and not ignores_rain and not is_lunar:
            perception_radius = perception_radius * 0.8
    if self.world != null and "arena" in self.world and "is_windy" in self.world.arena:
        if self.world.arena.is_windy and not is_lunar:
            perception_radius = perception_radius * 0.7
    if self.world != null and "arena" in self.world and "is_sandstorming" in self.world.arena:
        if self.world.arena.is_sandstorming and not ignores_sandstorm and ("ball_type" in self.ball and self.ball.ball_type != "sand_elemental") and not is_lunar:
            perception_radius = perception_radius * 0.3
    if self.world != null and "arena" in self.world and "is_snowing" in self.world.arena:
        if self.world.arena.is_snowing and not ignores_snow and ("ball_type" in self.ball and self.ball.ball_type != "snow_yeti") and not is_lunar:
            perception_radius = perception_radius * 0.6

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

    var bx_curr = 0.0
    var by_curr = 0.0
    if "x" in self.ball and "y" in self.ball:
        bx_curr = self.ball.x
        by_curr = self.ball.y

    var in_smoke = false
    var smoke_hazards = []
    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
        for h in self.world.arena.hazards:
            if "kind" in h and (h.kind == "smokescreen" or h.kind == "breakable_wall"):
                smoke_hazards.append(h)
                var hx = 0.0
                var hy = 0.0
                var hr = 0.0
                if "x" in h: hx = h.x
                if "y" in h: hy = h.y
                if "radius" in h: hr = h.radius
                var dist = sqrt(pow(hx - bx_curr, 2) + pow(hy - by_curr, 2))
                if dist <= hr:
                    in_smoke = true
    if in_smoke:
        perception_radius = min(perception_radius, 50.0)

    var entities = self.world.get_nearby_entities(self.ball, perception_radius)

    var intersects_smoke = func(ent):
        if has_sonar: return false
        var ex = 0.0
        var ey = 0.0
        if "x" in ent: ex = ent.x
        if "y" in ent: ey = ent.y
        for h in smoke_hazards:
            var hx = 0.0
            var hy = 0.0
            var hr = 0.0
            if "x" in h: hx = h.x
            if "y" in h: hy = h.y
            if "radius" in h: hr = h.radius
            var dx = ex - bx_curr
            var dy = ey - by_curr
            var l2 = dx*dx + dy*dy
            var dist = 0.0
            if l2 == 0.0:
                dist = sqrt(pow(hx - bx_curr, 2) + pow(hy - by_curr, 2))
            else:
                var t = max(0.0, min(1.0, ((hx - bx_curr) * dx + (hy - by_curr) * dy) / l2))
                var px = bx_curr + t * dx
                var py = by_curr + t * dy
                dist = sqrt(pow(hx - px, 2) + pow(hy - py, 2))
            if dist <= hr:
                return true
        return false

    var active_flares = []
    if arena != null and "hazards" in arena:
        for h in arena.hazards:
            if "kind" in h and h.kind == "flare":
                var h_active = true
                if "active" in h: h_active = h.active
                elif h.has_method("has_meta") and h.has_meta("active"): h_active = h.get_meta("active")
                if h_active:
                    active_flares.append(h)

    data["enemies"] = []
    for e in entities.get("enemies", []):
        if intersects_smoke.call(e): continue

        var revealed_by_flare = false
        var ex = 0.0
        if "x" in e: ex = e.x
        var ey = 0.0
        if "y" in e: ey = e.y
        for f in active_flares:
            var fx = 0.0
            if "x" in f: fx = f.x
            var fy = 0.0
            if "y" in f: fy = f.y
            var fr = 0.0
            if "radius" in f: fr = f.radius
            if pow(ex - fx, 2) + pow(ey - fy, 2) <= pow(fr, 2):
                revealed_by_flare = true
                break

        if not revealed_by_flare:
            var e_has_stealth = false
            if "has_stealth_drone" in e and e.has_stealth_drone:
                e_has_stealth = true
            elif e.has_method("get_meta") and e.has_meta("has_stealth_drone") and e.get_meta("has_stealth_drone"):
                e_has_stealth = true

            var e_has_shadow = false
            if e.has_method("get_meta") and e.has_meta("shadow_booster_timer"):
                e_has_shadow = e.get_meta("shadow_booster_timer") > 0
            elif "shadow_booster_timer" in e:
                e_has_shadow = float(e.shadow_booster_timer) > 0

            var e_has_stealth_booster = false
            if e.has_method("get_meta") and e.has_meta("stealth_booster_timer"):
                e_has_stealth_booster = e.get_meta("stealth_booster_timer") > 0
            elif "stealth_booster_timer" in e:
                e_has_stealth_booster = float(e.stealth_booster_timer) > 0

            var is_sand_cloaked = false
            if "ball_type" in e and e.ball_type == "sand_elemental" and self.world != null and "arena" in self.world and "is_sandstorming" in self.world.arena and self.world.arena.is_sandstorming:
                is_sand_cloaked = true

            if e_has_stealth or e_has_shadow or is_sand_cloaked or e_has_stealth_booster:
                var dist = sqrt(pow(e.x - bx_curr, 2) + pow(e.y - by_curr, 2))
                if e_has_stealth_booster:
                    continue
                elif is_sand_cloaked and dist > 40.0:
                    continue
                elif e_has_shadow and dist > 30.0:
                    continue
                elif e_has_stealth and dist > 80.0:
                    continue

        data["enemies"].append(e)
    data["allies"] = []
    for e in entities.get("allies", []):
        if not intersects_smoke.call(e): data["allies"].append(e)
    data["boosters"] = []
    for e in entities.get("boosters", []):
        if not intersects_smoke.call(e): data["boosters"].append(e)
    data["traps"] = []
    for e in entities.get("traps", []):
        if not intersects_smoke.call(e): data["traps"].append(e)

    var bx = bx_curr
    var by = by_curr

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
                if "kind" in h and h.kind == "fake_booster":
                    var is_scout = ("ball_type" in self.ball and self.ball.ball_type == "scout")
                    var has_drone = ("has_drone" in self.ball and self.ball.has_drone)
                    var p_score = 0.0
                    if "perception_score" in self.ball:
                        p_score = self.ball.perception_score

                    var identified = false
                    if is_scout:
                        if p_score > 50 or randf() < 0.3:
                            identified = true

                    if has_drone:
                        identified = true

                    if identified:
                        var found = false
                        for t in data["traps"]:
                            if "id" in t and "id" in h and t.id == h.id:
                                found = true
                                break
                        if not found:
                            data["traps"].append(h)
                    else:
                        var found = false
                        for b in data["boosters"]:
                            if "id" in b and "id" in h and b.id == h.id:
                                found = true
                                break
                        if not found:
                            data["boosters"].append(h)
                elif "kind" in h and (h.kind == "drone_item" or h.kind == "stealth_drone_item" or h.kind == "shadow_booster" or h.kind == "stealth_booster"):
                    var found = false
                    for b in data["boosters"]:
                        if "id" in b and "id" in h and b.id == h.id:
                            found = true
                            break
                    if not found:
                        data["boosters"].append(h)
                else:
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
