with open("src/ai/action.gd", "r") as f:
    content = f.read()

search = """func execute(strategy: String, delta: float):"""

replace = """func execute(strategy: String, delta: float):
    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
        var i = self.world.arena.hazards.size() - 1
        while i >= 0:
            var h = self.world.arena.hazards[i]
            var h_kind = h.get("kind") if typeof(h) == TYPE_DICTIONARY and h.has("kind") else (h.kind if typeof(h) == TYPE_OBJECT and "kind" in h else "")
            if h_kind == "mirage_decoy":
                var dur = h.get("duration") if typeof(h) == TYPE_DICTIONARY and h.has("duration") else (h.duration if typeof(h) == TYPE_OBJECT and "duration" in h else 0.0)
                dur -= delta
                if dur <= 0:
                    self.world.arena.hazards.remove_at(i)
                else:
                    if typeof(h) == TYPE_DICTIONARY: h["duration"] = dur
                    else: h.duration = dur

                    var owner_id = h.get("owner_id") if typeof(h) == TYPE_DICTIONARY and h.has("owner_id") else (h.owner_id if typeof(h) == TYPE_OBJECT and "owner_id" in h else null)
                    var team = h.get("team") if typeof(h) == TYPE_DICTIONARY and h.has("team") else (h.team if typeof(h) == TYPE_OBJECT and "team" in h else null)
                    var h_rad = h.get("radius") if typeof(h) == TYPE_DICTIONARY and h.has("radius") else (h.radius if typeof(h) == TYPE_OBJECT and "radius" in h else 10.0)
                    var h_x = h.get("x") if typeof(h) == TYPE_DICTIONARY and h.has("x") else (h.x if typeof(h) == TYPE_OBJECT and "x" in h else 0.0)
                    var h_y = h.get("y") if typeof(h) == TYPE_DICTIONARY and h.has("y") else (h.y if typeof(h) == TYPE_OBJECT and "y" in h else 0.0)

                    if self.world != null and "balls" in self.world:
                        for b in self.world.balls:
                            var b_id = b.get_meta("id") if b.has_method("get_meta") and b.has_meta("id") else (b["id"] if typeof(b) == TYPE_DICTIONARY and b.has("id") else (b.id if "id" in b else null))
                            var b_team = b.get_meta("team") if b.has_method("get_meta") and b.has_meta("team") else (b["team"] if typeof(b) == TYPE_DICTIONARY and b.has("team") else (b.team if "team" in b else null))
                            var b_alive = b.get_meta("alive") if b.has_method("get_meta") and b.has_meta("alive") else (b["alive"] if typeof(b) == TYPE_DICTIONARY and b.has("alive") else (b.alive if "alive" in b else true))

                            if b_id != owner_id and b_team != team and b_alive:
                                var b_x = b.get_meta("x") if b.has_method("get_meta") and b.has_meta("x") else (b["x"] if typeof(b) == TYPE_DICTIONARY and b.has("x") else (b.x if "x" in b else 0.0))
                                var b_y = b.get_meta("y") if b.has_method("get_meta") and b.has_meta("y") else (b["y"] if typeof(b) == TYPE_DICTIONARY and b.has("y") else (b.y if "y" in b else 0.0))
                                var dx = b_x - h_x
                                var dy = b_y - h_y
                                var dist_sq = dx * dx + dy * dy
                                var b_rad = b.get_meta("radius") if b.has_method("get_meta") and b.has_meta("radius") else (b["radius"] if typeof(b) == TYPE_DICTIONARY and b.has("radius") else (b.radius if "radius" in b else 10.0))
                                var r = h_rad + b_rad
                                if dist_sq <= r * r:
                                    var emp = {
                                        "id": 21000 + self.world.arena.hazards.size(),
                                        "x": h_x,
                                        "y": h_y,
                                        "radius": 40.0,
                                        "kind": "emp_burst",
                                        "damage": 20.0,
                                        "duration": 0.5,
                                        "owner_id": owner_id,
                                        "team": team
                                    }
                                    self.world.arena.hazards.append(emp)
                                    self.world.arena.hazards.remove_at(i)
                                    break
            i -= 1"""

if search in content:
    content = content.replace(search, replace, 1)
    with open("src/ai/action.gd", "w") as f:
        f.write(content)
    print("Action.gd execute patched successfully")
else:
    print("Search string not found in action.gd execute")
