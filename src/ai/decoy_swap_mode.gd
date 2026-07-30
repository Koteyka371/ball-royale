extends "res://src/ai/game_modes.gd".GameMode

var swap_timer = 0.0
var swap_interval = 10.0

func _init():
    self.name = "Decoy Swap Survival"
    self.description = "A chaotic new game mode where periodically every player on the map is instantly swapped in position with their nearest active decoy or clone. If they do not have a decoy active, one is spawned for them at their location moments before the swap."

func tick(world, balls, delta):
    self.swap_timer += delta

    if self.swap_timer >= self.swap_interval:
        self.swap_timer = 0.0

        if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
            world.add_event("decoy_swap_event", {"message": "Position Swap Initiated!"})
        elif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
            world.add_event.call("decoy_swap_event", {"message": "Position Swap Initiated!"})

        var new_decoys = []

        var players = []
        for b in balls:
            var alive = false
            if typeof(b) == TYPE_OBJECT and "alive" in b: alive = b.alive
            elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): alive = b.alive

            var b_type = null
            if typeof(b) == TYPE_OBJECT and "ball_type" in b: b_type = b.ball_type
            elif typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b.ball_type

            var is_decoy = false
            if typeof(b) == TYPE_OBJECT and "is_decoy" in b: is_decoy = b.is_decoy
            elif typeof(b) == TYPE_DICTIONARY and b.has("is_decoy"): is_decoy = b.is_decoy

            if alive and b_type != "spectator" and not is_decoy:
                players.append(b)

        for p in players:
            var p_id = null
            if typeof(p) == TYPE_OBJECT and "id" in p: p_id = p.id
            elif typeof(p) == TYPE_DICTIONARY and p.has("id"): p_id = p.id

            var p_team = null
            if typeof(p) == TYPE_OBJECT and "team" in p: p_team = p.team
            elif typeof(p) == TYPE_DICTIONARY and p.has("team"): p_team = p.team

            var p_x = 0.0
            var p_y = 0.0
            if typeof(p) == TYPE_OBJECT:
                if "x" in p: p_x = p.x
                if "y" in p: p_y = p.y
            elif typeof(p) == TYPE_DICTIONARY:
                if p.has("x"): p_x = p.x
                if p.has("y"): p_y = p.y

            var nearest_decoy = null
            var nearest_dist = 9999999.0

            for d in balls:
                var d_alive = false
                if typeof(d) == TYPE_OBJECT and "alive" in d: d_alive = d.alive
                elif typeof(d) == TYPE_DICTIONARY and d.has("alive"): d_alive = d.alive

                var d_is_decoy = false
                if typeof(d) == TYPE_OBJECT and "is_decoy" in d: d_is_decoy = d.is_decoy
                elif typeof(d) == TYPE_DICTIONARY and d.has("is_decoy"): d_is_decoy = d.is_decoy

                if d_alive and d_is_decoy:
                    var d_owner_id = null
                    if typeof(d) == TYPE_OBJECT and "owner_id" in d: d_owner_id = d.owner_id
                    elif typeof(d) == TYPE_DICTIONARY and d.has("owner_id"): d_owner_id = d.owner_id

                    var d_team = null
                    if typeof(d) == TYPE_OBJECT and "team" in d: d_team = d.team
                    elif typeof(d) == TYPE_DICTIONARY and d.has("team"): d_team = d.team

                    var is_owned = false
                    if d_owner_id != null and p_id != null and d_owner_id == p_id:
                        is_owned = true
                    elif d_team != null and p_team != null and d_team == p_team:
                        is_owned = true

                    if is_owned:
                        var d_x = 0.0
                        var d_y = 0.0
                        if typeof(d) == TYPE_OBJECT:
                            if "x" in d: d_x = d.x
                            if "y" in d: d_y = d.y
                        elif typeof(d) == TYPE_DICTIONARY:
                            if d.has("x"): d_x = d.x
                            if d.has("y"): d_y = d.y

                        var dist = sqrt((d_x - p_x)*(d_x - p_x) + (d_y - p_y)*(d_y - p_y))
                        if dist < nearest_dist:
                            nearest_dist = dist
                            nearest_decoy = d

            if nearest_decoy == null:
                var decoy = null
                if typeof(p) == TYPE_OBJECT and p.has_method("duplicate"):
                    decoy = p.duplicate()
                elif typeof(p) == TYPE_DICTIONARY:
                    decoy = p.duplicate()

                if decoy:
                    var new_id = randi() % 900000 + 100000
                    if typeof(world) == TYPE_OBJECT and "next_id" in world:
                        new_id = world.next_id
                        world.next_id += 1
                    elif typeof(world) == TYPE_DICTIONARY and world.has("next_id"):
                        new_id = world.next_id
                        world.next_id += 1

                    if typeof(decoy) == TYPE_OBJECT:
                        if "id" in decoy: decoy.id = new_id
                        if "is_decoy" in decoy: decoy.is_decoy = true
                        if "ball_type" in decoy: decoy.ball_type = "mimic_decoy"
                        if "owner_id" in decoy: decoy.owner_id = p_id
                        else:
                            if decoy.has_method("set_meta"): decoy.set_meta("owner_id", p_id)
                        if "speed" in decoy: decoy.speed = 0.0
                        if "damage" in decoy: decoy.damage = 0.0
                        if decoy.has_method("set_meta"):
                            decoy.set_meta("base_speed", 0.0)
                        if "x" in decoy: decoy.x = p_x
                        if "y" in decoy: decoy.y = p_y
                    elif typeof(decoy) == TYPE_DICTIONARY:
                        decoy["id"] = new_id
                        decoy["is_decoy"] = true
                        decoy["ball_type"] = "mimic_decoy"
                        decoy["owner_id"] = p_id
                        decoy["speed"] = 0.0
                        decoy["damage"] = 0.0
                        decoy["base_speed"] = 0.0
                        decoy["x"] = p_x
                        decoy["y"] = p_y

                    new_decoys.append(decoy)
                    nearest_decoy = decoy

            if nearest_decoy != null:
                var d_x = 0.0
                var d_y = 0.0
                if typeof(nearest_decoy) == TYPE_OBJECT:
                    if "x" in nearest_decoy: d_x = nearest_decoy.x
                    if "y" in nearest_decoy: d_y = nearest_decoy.y
                elif typeof(nearest_decoy) == TYPE_DICTIONARY:
                    if nearest_decoy.has("x"): d_x = nearest_decoy.x
                    if nearest_decoy.has("y"): d_y = nearest_decoy.y

                if typeof(p) == TYPE_OBJECT:
                    if "x" in p: p.x = d_x
                    if "y" in p: p.y = d_y
                elif typeof(p) == TYPE_DICTIONARY:
                    if p.has("x"): p.x = d_x
                    if p.has("y"): p.y = d_y

                if typeof(nearest_decoy) == TYPE_OBJECT:
                    if "x" in nearest_decoy: nearest_decoy.x = p_x
                    if "y" in nearest_decoy: nearest_decoy.y = p_y
                elif typeof(nearest_decoy) == TYPE_DICTIONARY:
                    if nearest_decoy.has("x"): nearest_decoy.x = p_x
                    if nearest_decoy.has("y"): nearest_decoy.y = p_y

                if typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
                    world.add_event("visual_effect", {"type": "teleport", "x": d_x, "y": d_y})
                    world.add_event("visual_effect", {"type": "teleport", "x": p_x, "y": p_y})
                elif typeof(world) == TYPE_DICTIONARY and world.has("add_event"):
                    world.add_event.call("visual_effect", {"type": "teleport", "x": d_x, "y": d_y})
                    world.add_event.call("visual_effect", {"type": "teleport", "x": p_x, "y": p_y})

        for d in new_decoys:
            if typeof(world) == TYPE_OBJECT and "balls" in world:
                world.balls.append(d)
            elif typeof(world) == TYPE_DICTIONARY and world.has("balls"):
                world.balls.append(d)
