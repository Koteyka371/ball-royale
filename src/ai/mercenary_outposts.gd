class_name MercenaryOutpostsMode
extends "res://src/ai/game_modes.gd".GameMode

var outposts = []
var rng = RandomNumberGenerator.new()

func _init():
    id = "Mercenary Outposts"
    name = "Mercenary Outposts"
    description = "Players can capture mercenary outposts across the map. Once fully captured, friendly AI balls spawn periodically and help defend the capturing player."

func setup(world, balls):
    super.setup(world, balls)
    rng.randomize()
    outposts.clear()

    var arena_width = 1000
    var arena_height = 1000

    if typeof(world) == TYPE_DICTIONARY:
        if typeof(world.get("arena")) == TYPE_DICTIONARY:
            arena_width = world["arena"].get("width", 1000)
            arena_height = world["arena"].get("height", 1000)
    elif typeof(world) == TYPE_OBJECT and "arena" in world:
        if typeof(world.arena) == TYPE_DICTIONARY:
            arena_width = world.arena.get("width", 1000)
            arena_height = world.arena.get("height", 1000)
        elif typeof(world.arena) == TYPE_OBJECT:
            arena_width = world.arena.width if "width" in world.arena else 1000
            arena_height = world.arena.height if "height" in world.arena else 1000

    for i in range(3):
        var out_x = rng.randf_range(200, arena_width - 200)
        var out_y = rng.randf_range(200, arena_height - 200)

        var outpost = {
            "id": "outpost_" + str(rng.randi_range(1000, 9999)),
            "x": out_x,
            "y": out_y,
            "radius": 80.0,
            "kind": "mercenary_outpost",
            "capturing_team": null,
            "capture_progress": 0.0,
            "controlling_team": null,
            "spawn_timer": 0.0,
            "spawn_interval": 10.0,
            "active": true
        }
        outposts.append(outpost)

        var hazards_list = null
        if typeof(world) == TYPE_DICTIONARY:
            if typeof(world.get("arena")) == TYPE_DICTIONARY and world["arena"].has("hazards"):
                hazards_list = world["arena"]["hazards"]
        elif typeof(world) == TYPE_OBJECT and "arena" in world:
            if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
                hazards_list = world.arena["hazards"]
            elif typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
                hazards_list = world.arena.hazards

        if hazards_list != null:
            # We add a dict acting as a hazard
            var h = {
                "id": outpost["id"],
                "x": out_x,
                "y": out_y,
                "radius": 80.0,
                "kind": "mercenary_outpost",
                "damage": 0.0,
                "capture_progress": 0.0,
                "controlling_team": null,
                "active": true
            }
            hazards_list.append(h)

func tick(world, balls: Array, delta: float):
    for outpost in outposts:
        if not outpost["active"]: continue

        var balls_inside = []
        for b in balls:
            var is_alive = false
            var ball_type = ""
            var bx = 0.0
            var by = 0.0

            if typeof(b) == TYPE_DICTIONARY:
                is_alive = b.get("alive", false)
                ball_type = b.get("ball_type", "")
                bx = b.get("x", 0.0)
                by = b.get("y", 0.0)
            elif typeof(b) == TYPE_OBJECT:
                is_alive = b.get("alive") if "alive" in b else false
                ball_type = b.get("ball_type") if "ball_type" in b else ""
                bx = b.get("x") if "x" in b else 0.0
                by = b.get("y") if "y" in b else 0.0

            if not is_alive or ball_type == "spectator" or ball_type == "mercenary":
                continue

            var dist = sqrt(pow(bx - outpost["x"], 2) + pow(by - outpost["y"], 2))
            if dist < outpost["radius"]:
                balls_inside.append(b)

        if balls_inside.size() > 0:
            var teams_inside = []
            for b in balls_inside:
                var team = ""
                if typeof(b) == TYPE_DICTIONARY:
                    team = b.get("team", b.get("ball_type", ""))
                elif typeof(b) == TYPE_OBJECT:
                    team = b.get("team") if "team" in b else (b.get("ball_type") if "ball_type" in b else "")

                if not teams_inside.has(team):
                    teams_inside.append(team)
                                if teams_inside.size() == 1:
                var team = teams_inside[0]
                if outpost["capturing_team"] == team or outpost["capturing_team"] == null:
                    outpost["capturing_team"] = team
                    if outpost["controlling_team"] != team:
                        outpost["capture_progress"] += 15.0 * delta
                        if outpost["capture_progress"] >= 100.0:
                            outpost["controlling_team"] = team
                            outpost["capture_progress"] = 100.0
                            outpost["spawn_timer"] = outpost["spawn_interval"]

                            if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
                                world.add_event("outpost_captured", {"team": team, "outpost_id": outpost["id"]})                else:
                    outpost["capture_progress"] -= 15.0 * delta
                    if outpost["capture_progress"] <= 0.0:
                        var remainder = -outpost["capture_progress"]
                        outpost["capturing_team"] = team
                        outpost["controlling_team"] = null
                        outpost["capture_progress"] = remainder
                        if outpost["capture_progress"] >= 100.0:
                            outpost["controlling_team"] = team
                            outpost["capture_progress"] = 100.0
            else:
                pass # Contested
        else:
            if outpost["controlling_team"] != outpost["capturing_team"] and outpost["capturing_team"] != null:
                outpost["capture_progress"] = max(0.0, outpost["capture_progress"] - 5.0 * delta)
                if outpost["capture_progress"] == 0:
                    outpost["capturing_team"] = null

        var hazards_list = null
        if typeof(world) == TYPE_DICTIONARY:
            if typeof(world.get("arena")) == TYPE_DICTIONARY and world["arena"].has("hazards"):
                hazards_list = world["arena"]["hazards"]
        elif typeof(world) == TYPE_OBJECT and "arena" in world:
            if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
                hazards_list = world.arena["hazards"]
            elif typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
                hazards_list = world.arena.hazards

        if hazards_list != null:
            for h in hazards_list:
                var h_id = ""
                if typeof(h) == TYPE_DICTIONARY: h_id = h.get("id", "")
                elif typeof(h) == TYPE_OBJECT: h_id = h.get("id") if "id" in h else ""

                if h_id == outpost["id"]:
                    if typeof(h) == TYPE_DICTIONARY:
                        h["capture_progress"] = outpost["capture_progress"]
                        h["controlling_team"] = outpost["controlling_team"]
                    else:
                        h.capture_progress = outpost["capture_progress"]
                        h.controlling_team = outpost["controlling_team"]

        if outpost["controlling_team"] != null:
            outpost["spawn_timer"] += delta
            if outpost["spawn_timer"] >= outpost["spawn_interval"]:
                outpost["spawn_timer"] = 0.0
                spawn_mercenary(world, balls, outpost)

func spawn_mercenary(world, balls: Array, outpost: Dictionary):
    var team = outpost["controlling_team"]

    var merc = {
        "id": "merc_" + str(rng.randi_range(1000, 9999)) + "_" + outpost["id"],
        "x": outpost["x"],
        "y": outpost["y"],
        "vx": 0.0,
        "vy": 0.0,
        "radius": 20.0,
        "mass": 1.0,
        "hp": 50.0,
        "max_hp": 50.0,
        "team": team,
        "ball_type": "mercenary",
        "alive": true,
        "speed_multiplier": 1.0,
        "damage_multiplier": 1.0,
        "speed": 200.0,
        "base_speed": 200.0,
        "shield": 0.0,
        "damage": 10.0,
        "ai_target": null,
        "is_intangible": false
    }

    balls.append(merc)

    if typeof(world) == TYPE_OBJECT:
        if "entities" in world:
            world.entities.append(merc)
        if "balls" in world:
            if not world.balls.has(merc):
                world.balls.append(merc)
    elif typeof(world) == TYPE_DICTIONARY:
        if world.has("entities"):
            world["entities"].append(merc)
        if world.has("balls"):
            if not world["balls"].has(merc):
                world["balls"].append(merc)

func check_winner(world, balls: Array):
    return null
