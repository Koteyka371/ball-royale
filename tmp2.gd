func _collect_booster(delta: float):
    var intangible = false
    if typeof(self.ball) == TYPE_OBJECT and "intangible" in self.ball: intangible = self.ball.intangible
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("intangible"): intangible = self.ball.get_meta("intangible")
    var timer = 0.0
    if typeof(self.ball) == TYPE_OBJECT and "intangible_timer" in self.ball: timer = self.ball.intangible_timer
    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("intangible_timer"): timer = self.ball.get_meta("intangible_timer")
    if intangible or timer > 0.0:
        _idle(delta)
        return
    var boosters = _get_boosters()
    if boosters.size() > 0:

        # Check for blood orb
        for b in boosters:
            var bk = ""
            if typeof(b) == TYPE_DICTIONARY and b.has("kind"): bk = b.kind
            elif typeof(b) == TYPE_OBJECT and "kind" in b: bk = b.kind

            var b_active = true
            if typeof(b) == TYPE_DICTIONARY and b.has("active"): b_active = b.active
            elif typeof(b) == TYPE_OBJECT and "active" in b: b_active = b.active

            if bk == "blood_orb" and b_active:
                var heal_amount = 20.0
                var current_hp = 100.0
                var max_hp = 100.0

                if typeof(self.ball) == TYPE_DICTIONARY:
                    if self.ball.has("hp"): current_hp = self.ball.hp
                    if self.ball.has("max_hp"): max_hp = self.ball.max_hp
                    self.ball.hp = min(current_hp + heal_amount, max_hp)
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "hp" in self.ball: current_hp = self.ball.hp
                    if "max_hp" in self.ball: max_hp = self.ball.max_hp
                    self.ball.hp = min(current_hp + heal_amount, max_hp)

                if typeof(b) == TYPE_DICTIONARY:
                    b.active = false
                elif typeof(b) == TYPE_OBJECT:
                    b.active = false

                if "boosters" in self.world:
                    var idx = self.world.boosters.find(b)
                    if idx >= 0:
                        self.world.boosters.remove(idx)

        # Check for phylactery_item
        var b_id = null
        if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): b_id = self.ball.id
        elif typeof(self.ball) == TYPE_OBJECT and "id" in self.ball: b_id = self.ball.id

        for b in boosters:
            var b_kind = ""
            if typeof(b) == TYPE_DICTIONARY and b.has("kind"): b_kind = b.kind
            elif typeof(b) == TYPE_OBJECT and "kind" in b: b_kind = b.kind
            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("kind"): b_kind = b.get_meta("kind")

            var b_owner = null
            if typeof(b) == TYPE_DICTIONARY and b.has("owner_id"): b_owner = b.owner_id
            elif typeof(b) == TYPE_OBJECT and "owner_id" in b: b_owner = b.owner_id
            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("owner_id"): b_owner = b.get_meta("owner_id")

            if b_kind == "anti_radiation_booster" and (b.get("active", true) if typeof(b) == TYPE_DICTIONARY else (b.get_meta("active") if b.has_meta("active") else true)):
                if typeof(ball) == TYPE_OBJECT:
                    ball.set_meta("mutation_level", 0.0)
                    ball.set_meta("mutant", false)
                    ball.set_meta("max_stamina", 100.0)
                else:
                    ball["mutation_level"] = 0.0
                    ball["mutant"] = false
                    ball["max_stamina"] = 100.0
                if typeof(b) == TYPE_OBJECT:
                    b.set_meta("active", false)
                else:
                    b["active"] = false
                if "boosters" in world and b in world.boosters:
                    world.boosters.erase(b)
                if "arena" in world and "hazards" in world.arena and b in world.arena.hazards:
                    world.arena.hazards.erase(b)
            elif b_kind == "ethereal_tether_booster" and b_active:
                var b_x = 0.0
                var b_y = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    b_x = b.get("x", 0.0)
                    b_y = b.get("y", 0.0)
                elif typeof(b) == TYPE_OBJECT:
                    if "x" in b: b_x = b.x
                    elif b.has_method("get_meta"): b_x = b.get_meta("x")
                    if "y" in b: b_y = b.y
                    elif b.has_method("get_meta"): b_y = b.get_meta("y")

                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b["radius"]
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("radius"): b_radius = b.get_meta("radius")

                var my_radius = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): my_radius = self.ball["radius"]
                elif typeof(self.ball) == TYPE_OBJECT and "radius" in self.ball: my_radius = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("radius"): my_radius = self.ball.get_meta("radius")

                var b_dist = sqrt(pow(b_x - self.ball.x, 2) + pow(b_y - self.ball.y, 2))

                if b_dist <= my_radius + b_radius + 5.0:
                    var allies = _get_allies()
                    var linked_balls = [self.ball]
                    for ally in allies:
                        linked_balls.append(ally)

                    if linked_balls.size() > 1:
                        for ally_ball in linked_balls:
                            var links = []
                            for other in linked_balls:
                                if other != ally_ball:
                                    links.append(other)

                            if typeof(ally_ball) == TYPE_DICTIONARY:
                                ally_ball["ethereal_tether_links"] = links
                                ally_ball["ethereal_tether_timer"] = 15.0
                                ally_ball["ethereal_tether_teleport_charges"] = 1
                            else:
                                if "ethereal_tether_links" in ally_ball: ally_ball.ethereal_tether_links = links
                                elif ally_ball.has_method("set_meta"): ally_ball.set_meta("ethereal_tether_links", links)

                                if "ethereal_tether_timer" in ally_ball: ally_ball.ethereal_tether_timer = 15.0
                                elif ally_ball.has_method("set_meta"): ally_ball.set_meta("ethereal_tether_timer", 15.0)

                                if "ethereal_tether_teleport_charges" in ally_ball: ally_ball.ethereal_tether_teleport_charges = 1
                                elif ally_ball.has_method("set_meta"): ally_ball.set_meta("ethereal_tether_teleport_charges", 1)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)

                    if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                        self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                        self.world.arena.hazards.erase(b)
            if b_kind == "phylactery_item" and b_owner == b_id:
                if typeof(self.ball) == TYPE_DICTIONARY: self.ball["phylactery_active"] = true
                else:
                    if "phylactery_active" in self.ball: self.ball.phylactery_active = true
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("phylactery_active", true)

                if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                else:
                    if "active" in b: b.active = false
                    elif b.has_method("set_meta"): b.set_meta("active", false)

                if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                    self.world.boosters.erase(b)
                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                    self.world.arena.hazards.erase(b)

            elif b_kind == "heroism_booster":
                var dx = get_bx(b) - my_x
                var dy = get_by(b) - my_y
                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_radius = b.radius
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["heroism_booster_timer"] = 10.0
                        self.ball["emotion"] = "heroism"
                        self.ball["is_glowing"] = true
                    else:
                        if "heroism_booster_timer" in self.ball:
                            self.ball.heroism_booster_timer = 10.0
                            if "emotion" in self.ball: self.ball.emotion = "heroism"
                            if "is_glowing" in self.ball: self.ball.is_glowing = true
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("heroism_booster_timer", 10.0)
                            self.ball.set_meta("emotion", "heroism")
                            self.ball.set_meta("is_glowing", true)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)

                    if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                        self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                        self.world.arena.hazards.erase(b)

            elif b_kind == "grave_robber_shovel":
                var dx = get_bx(b) - my_x
                var dy = get_by(b) - my_y
                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_radius = b.radius
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY: self.ball["grave_robber_shovel_active"] = true
                    else:
                        if "grave_robber_shovel_active" in self.ball: self.ball.grave_robber_shovel_active = true
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("grave_robber_shovel_active", true)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)

                    if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                        self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                        self.world.arena.hazards.erase(b)

            elif b_kind == "geyser_boots":
                var dx = get_bx(b) - my_x
                var dy = get_by(b) - my_y
                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_radius = b.radius
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["geyser_boots_timer"] = 15.0
                    else:
                        if "geyser_boots_timer" in self.ball:
                            self.ball.geyser_boots_timer = 15.0
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("geyser_boots_timer", 15.0)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)

                    if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                        self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                        self.world.arena.hazards.erase(b)

            elif b_kind == "wind_shield_booster":
                var dx = get_bx(b) - my_x
                var dy = get_by(b) - my_y
                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_radius = b.radius
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY: self.ball["wind_shield_booster_timer"] = 15.0
                    else:
                        if "wind_shield_booster_timer" in self.ball: self.ball.wind_shield_booster_timer = 15.0
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("wind_shield_booster_timer", 15.0)
                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)
                    if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                        self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                        self.world.arena.hazards.erase(b)
            elif b_kind == "echo_booster":
                var dx = 0.0
                if typeof(b) == TYPE_DICTIONARY and b.has("x"): dx = b.x - self.ball.x
                elif typeof(b) == TYPE_OBJECT and "x" in b: dx = b.x - self.ball.x
                var dy = 0.0
                if typeof(b) == TYPE_DICTIONARY and b.has("y"): dy = b.y - self.ball.y
                elif typeof(b) == TYPE_OBJECT and "y" in b: dy = b.y - self.ball.y
                var dist = sqrt(dx*dx + dy*dy)

                var br = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): br = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: br = b.radius
                var self_r = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): self_r = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT and "radius" in self.ball: self_r = self.ball.radius

                if dist <= self_r + br + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["echo_booster_timer"] = 10.0
                        self.ball["echo_booster_spawn_timer"] = 0.0
                    else:
                        self.ball.echo_booster_timer = 10.0
                        self.ball.echo_booster_spawn_timer = 0.0

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else: b.active = false

                    if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
                        var idx = self.world.boosters.find(b)
                        if idx != -1: self.world.boosters.erase(b)
                    elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                        var idx = self.world.boosters.find(b)
                        if idx != -1: self.world.boosters.erase(b)

                    if typeof(self.world) == TYPE_OBJECT and "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                        var idx = self.world.arena.hazards.find(b)
                        if idx != -1: self.world.arena.hazards.erase(b)
            elif b_kind == "eclipse_booster_item":
                var dx = b_x - ball_x
                var dy = b_y - ball_y
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= ball_rad + b_rad + 5.0:
                    var inv = []
                    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("inventory"): inv = self.ball["inventory"]
                    elif "inventory" in self.ball: inv = self.ball.inventory
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                    inv.append("eclipse_booster_item")
                    if typeof(self.ball) == TYPE_DICTIONARY: self.ball["inventory"] = inv
                    elif "inventory" in self.ball: self.ball.inventory = inv
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else: b.active = false

                    if self.world != null and "boosters" in self.world:
                        var b_idx = self.world.boosters.find(b)
                        if b_idx != -1:
                            self.world.boosters.remove_at(b_idx)
                    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                        var h_idx = self.world.arena.hazards.find(b)
                        if h_idx != -1:
                            self.world.arena.hazards.remove_at(h_idx)
            elif b_kind == "overload_zone_item":
                var dx = b_x - ball_x
                var dy = b_y - ball_y
                var dist = sqrt(dx*dx + dy*dy)
                if dist <= ball_rad + b_rad + 5.0:
                    var inv = []
                    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("inventory"): inv = self.ball["inventory"]
                    elif "inventory" in self.ball: inv = self.ball.inventory
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                    inv.append("overload_zone_item")
                    if typeof(self.ball) == TYPE_DICTIONARY: self.ball["inventory"] = inv
                    elif "inventory" in self.ball: self.ball.inventory = inv
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else: b.active = false

                    if self.world != null and "boosters" in self.world:
                        var b_idx = self.world.boosters.find(b)
                        if b_idx != -1:
                            self.world.boosters.remove_at(b_idx)
                    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                        var h_idx = self.world.arena.hazards.find(b)
                        if h_idx != -1:
                            self.world.arena.hazards.remove_at(h_idx)
            elif b_kind == "silence_immunity_booster":
                var dx_ghost = b_x - self.ball.x
                var dy_ghost = b_y - self.ball.y
                var b_dist = sqrt(dx_ghost * dx_ghost + dy_ghost * dy_ghost)
                var b_rad = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_rad = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_rad = b.radius
                var self_rad = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): self_rad = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT and "radius" in self.ball: self_rad = self.ball.radius
                if b_dist <= self_rad + b_rad + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["silence_immunity_timer"] = 15.0
                    else:
                        if "silence_immunity_timer" in self.ball: self.ball.silence_immunity_timer = 15.0
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("silence_immunity_timer", 15.0)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    elif typeof(b) == TYPE_OBJECT and "active" in b: b.active = false

                    if typeof(self.world) == TYPE_DICTIONARY:
                        if self.world.has("boosters"):
                            var boosters = self.world.boosters
                            var new_boosters = []
                            for x in boosters: if x != b: new_boosters.append(x)
                            self.world.boosters = new_boosters
                        if self.world.has("arena") and typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
                            var hazards = self.world.arena.hazards
                            var new_hazards = []
                            for x in hazards: if x != b: new_hazards.append(x)
                            self.world.arena.hazards = new_hazards
                    elif typeof(self.world) == TYPE_OBJECT:
                        if "boosters" in self.world:
                            var boosters = self.world.boosters
                            var new_boosters = []
                            for x in boosters: if x != b: new_boosters.append(x)
                            self.world.boosters = new_boosters
                        if "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                            var hazards = self.world.arena.hazards
                            var new_hazards = []
                            for x in hazards: if x != b: new_hazards.append(x)
                            self.world.arena.hazards = new_hazards

            elif b_kind == "meteor_fragment":
                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b.x
                    if b.has("y"): by = b.y
                else:
                    if "x" in b: bx = b.x
                    if "y" in b: by = b.y
                var bradius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): bradius = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: bradius = b.radius
                var dist = sqrt(pow(bx - ball_x, 2) + pow(by - ball_y, 2))
                if dist <= ball_radius + bradius + 5.0:
                    var current_t = 0.0
                    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("damage_booster_timer"):
                        current_t = self.ball["damage_booster_timer"]
                    elif typeof(self.ball) == TYPE_OBJECT and "damage_booster_timer" in self.ball:
                        current_t = self.ball.damage_booster_timer

                    if 15.0 > current_t: current_t = 15.0

                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["damage_booster_timer"] = current_t
                    elif typeof(self.ball) == TYPE_OBJECT:
                        if "damage_booster_timer" in self.ball:
                            self.ball.damage_booster_timer = current_t
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("damage_booster_timer", current_t)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    elif typeof(b) == TYPE_OBJECT: b.active = false
                    if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
                        var boosters = self.world.boosters
                        var new_boosters = []
                        for x in boosters: if x != b: new_boosters.append(x)
                        self.world.boosters = new_boosters
                    elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                        var boosters = self.world.boosters
                        var new_boosters = []
                        for x in boosters: if x != b: new_boosters.append(x)
                        self.world.boosters = new_boosters

                    if typeof(self.world) == TYPE_DICTIONARY and self.world.has("arena") and typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
                        var hazards = self.world.arena.hazards
                        var new_hazards = []
                        for x in hazards: if x != b: new_hazards.append(x)
                        self.world.arena.hazards = new_hazards
                    elif typeof(self.world) == TYPE_OBJECT and "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                        var hazards = self.world.arena.hazards
                        var new_hazards = []
                        for x in hazards: if x != b: new_hazards.append(x)
                        self.world.arena.hazards = new_hazards
            elif b_kind == "ghost_booster":

                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b.x
                    if b.has("y"): by = b.y
                else:
                    if "x" in b: bx = b.x
                    elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                    if "y" in b: by = b.y
                    elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT:
                    if "radius" in b: b_radius = b.radius
                    elif b.has_method("get_meta") and b.has_meta("radius"): b_radius = b.get_meta("radius")

                var my_radius = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): my_radius = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "radius" in self.ball: my_radius = self.ball.radius
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("radius"): my_radius = self.ball.get_meta("radius")

                var dist = sqrt(pow(bx - self.ball.x, 2) + pow(by - self.ball.y, 2))
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["ghost_booster_timer"] = 10.0
                        self.ball["ghost_mode_active"] = true
                    elif typeof(self.ball) == TYPE_OBJECT:
                        if "ghost_booster_timer" in self.ball: self.ball.ghost_booster_timer = 10.0
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("ghost_booster_timer", 10.0)

                        if "ghost_mode_active" in self.ball: self.ball.ghost_mode_active = true
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("ghost_mode_active", true)
                        if "is_ghost" in self.ball: self.ball.is_ghost = true
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("is_ghost", true)

                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["intangible"] = true
                        self.ball["intangible_timer"] = 10.0
                    elif typeof(self.ball) == TYPE_OBJECT:
                        if "intangible" in self.ball: self.ball.intangible = true
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("intangible", true)
                        if "intangible_timer" in self.ball: self.ball.intangible_timer = 10.0
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("intangible_timer", 10.0)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else: b.active = false

                    if self.world != null and "boosters" in self.world:
                        var b_idx = self.world.boosters.find(b)
                        if b_idx != -1:
                            self.world.boosters.remove_at(b_idx)
                    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                        var h_idx = self.world.arena.hazards.find(b)
                        if h_idx != -1:
                            self.world.arena.hazards.remove_at(h_idx)
            elif b_kind == "magnetic_aura_booster":
                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b.x
                    if b.has("y"): by = b.y
                else:
                    if "x" in b: bx = b.x
                    elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                    if "y" in b: by = b.y
                    elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT:
                    if "radius" in b: b_radius = b.radius
                    elif b.has_method("get_meta") and b.has_meta("radius"): b_radius = b.get_meta("radius")

                var my_radius = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): my_radius = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "radius" in self.ball: my_radius = self.ball.radius
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("radius"): my_radius = self.ball.get_meta("radius")

                var dist = sqrt(pow(bx - self.ball.x, 2) + pow(by - self.ball.y, 2))
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["magnetic_aura_timer"] = 15.0
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                        self.ball.set_meta("magnetic_aura_timer", 15.0)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else: b.active = false

                    if self.world != null and "boosters" in self.world:
                        var b_idx = self.world.boosters.find(b)
                        if b_idx != -1:
                            self.world.boosters.remove_at(b_idx)
                    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                        var h_idx = self.world.arena.hazards.find(b)
                        if h_idx != -1:
                            self.world.arena.hazards.remove_at(h_idx)
            elif b_kind == "magnetic_field_booster":
                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b.x
                    if b.has("y"): by = b.y
                else:
                    if "x" in b: bx = b.x
                    elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                    if "y" in b: by = b.y
                    elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT:
                    if "radius" in b: b_radius = b.radius
                    elif b.has_method("get_meta") and b.has_meta("radius"): b_radius = b.get_meta("radius")

                var my_radius = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): my_radius = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "radius" in self.ball: my_radius = self.ball.radius
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("radius"): my_radius = self.ball.get_meta("radius")

                var dist = sqrt((bx - ball_x)*(bx - ball_x) + (by - ball_y)*(by - ball_y))
                if dist <= my_radius + b_radius + 5.0:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["magnetic_field_timer"] = 15.0
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                        self.ball.set_meta("magnetic_field_timer", 15.0)

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else: b.active = false

                    if self.world != null and "boosters" in self.world:
                        var b_idx = self.world.boosters.find(b)
                        if b_idx != -1:
                            self.world.boosters.remove_at(b_idx)
                    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                        var h_idx = self.world.arena.hazards.find(b)
                        if h_idx != -1:
                            self.world.arena.hazards.remove_at(h_idx)
            elif b_kind == "anchor_repulsor_booster":
                var dist = sqrt((b_x - self.ball.x)*(b_x - self.ball.x) + (b_y - self.ball.y)*(b_y - self.ball.y))
                var rad1 = 10.0
                if typeof(self.ball) == TYPE_OBJECT and "radius" in self.ball: rad1 = float(self.ball.radius)
                elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): rad1 = float(self.ball["radius"])
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("radius"): rad1 = float(self.ball.get_meta("radius"))
                var rad2 = 15.0
                if typeof(b) == TYPE_OBJECT and "radius" in b: rad2 = float(b.radius)
                elif typeof(b) == TYPE_DICTIONARY and b.has("radius"): rad2 = float(b["radius"])
                elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("radius"): rad2 = float(b.get_meta("radius"))
                if dist <= rad1 + rad2 + 5.0:
                    var cur_anchor = 0.0
                    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("anchor_booster_timer"): cur_anchor = float(self.ball["anchor_booster_timer"])
                    elif typeof(self.ball) == TYPE_OBJECT and "anchor_booster_timer" in self.ball: cur_anchor = float(self.ball.anchor_booster_timer)
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("anchor_booster_timer"): cur_anchor = float(self.ball.get_meta("anchor_booster_timer"))

                    var cur_repulsor = 0.0
                    if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("anchor_repulsor_timer"): cur_repulsor = float(self.ball["anchor_repulsor_timer"])
                    elif typeof(self.ball) == TYPE_OBJECT and "anchor_repulsor_timer" in self.ball: cur_repulsor = float(self.ball.anchor_repulsor_timer)
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("anchor_repulsor_timer"): cur_repulsor = float(self.ball.get_meta("anchor_repulsor_timer"))

                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["anchor_booster_timer"] = max(cur_anchor, 10.0)
                        self.ball["anchor_repulsor_timer"] = max(cur_repulsor, 10.0)
                    else:
                        if "anchor_booster_timer" in self.ball: self.ball.anchor_booster_timer = max(cur_anchor, 10.0)
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("anchor_booster_timer", max(cur_anchor, 10.0))

                        if "anchor_repulsor_timer" in self.ball: self.ball.anchor_repulsor_timer = max(cur_repulsor, 10.0)
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("anchor_repulsor_timer", max(cur_repulsor, 10.0))

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)

                    if self.world != null and "boosters" in self.world:
                        var idx = self.world.boosters.find(b)
                        if idx != -1: self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                        var idx = self.world.arena.hazards.find(b)
                        if idx != -1: self.world.arena.hazards.erase(b)
            elif b_kind == "flashbang_booster":
                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b.x
                    if b.has("y"): by = b.y
                else:
                    if "x" in b: bx = b.x
                    elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                    if "y" in b: by = b.y
                    elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT:
                    if "radius" in b: b_radius = b.radius
                    elif b.has_method("get_meta") and b.has_meta("radius"): b_radius = b.get_meta("radius")

                var my_radius = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): my_radius = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "radius" in self.ball: my_radius = self.ball.radius
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("radius"): my_radius = self.ball.get_meta("radius")

                var dist = sqrt(pow(bx - self.ball.x, 2) + pow(by - self.ball.y, 2))
                if dist <= my_radius + b_radius + 5.0:
                    if self.world != null and "balls" in self.world:
                        for other in self.world.balls:
                            if other != self.ball:
                                var b_alive = other.alive if "alive" in other else (other.get_meta("alive") if typeof(other) == TYPE_OBJECT and other.has_meta("alive") else true)
                                var b_team = other.team if "team" in other else (other.get_meta("team") if typeof(other) == TYPE_OBJECT and other.has_meta("team") else "")
                                var my_team = self.ball.team if "team" in self.ball else (self.ball.get_meta("team") if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("team") else "")

                                var ox = other.x if "x" in other else (other.get_meta("x") if typeof(other) == TYPE_OBJECT and other.has_meta("x") else 0.0)
                                var oy = other.y if "y" in other else (other.get_meta("y") if typeof(other) == TYPE_OBJECT and other.has_meta("y") else 0.0)
                                var odist = sqrt(pow(ox - self.ball.x, 2) + pow(oy - self.ball.y, 2))

                                if b_alive and b_team != my_team and odist <= 500.0:
                                    if typeof(other) == TYPE_OBJECT:
                                        if "is_blinded" in other: other.is_blinded = true
                                        elif other.has_method("set_meta"): other.set_meta("is_blinded", true)

                                        var current_blindness = other.blindness_timer if "blindness_timer" in other else (other.get_meta("blindness_timer") if other.has_method("has_meta") and other.has_meta("blindness_timer") else 0.0)
                                        if current_blindness < 5.0:
                                            if "blindness_timer" in other: other.blindness_timer = 5.0
                                            elif other.has_method("set_meta"): other.set_meta("blindness_timer", 5.0)

                                        if "is_stunned" in other: other.is_stunned = true
                                        elif other.has_method("set_meta"): other.set_meta("is_stunned", true)

                                        var current_stun = other.stun_timer if "stun_timer" in other else (other.get_meta("stun_timer") if other.has_method("has_meta") and other.has_meta("stun_timer") else 0.0)
                                        if current_stun < 3.0:
                                            if "stun_timer" in other: other.stun_timer = 3.0
                                            elif other.has_method("set_meta"): other.set_meta("stun_timer", 3.0)

                                        var has_base_pr = other.has_meta("base_perception_radius") if other.has_method("has_meta") else ("base_perception_radius" in other)
                                        if not has_base_pr:
                                            var pr = other.perception_radius if "perception_radius" in other else (other.get_meta("perception_radius") if other.has_method("has_meta") and other.has_meta("perception_radius") else 100.0)
                                            if "base_perception_radius" in other: other.base_perception_radius = pr
                                            elif other.has_method("set_meta"): other.set_meta("base_perception_radius", pr)

                                        if "perception_radius" in other: other.perception_radius = 0.0
                                        elif other.has_method("set_meta"): other.set_meta("perception_radius", 0.0)
                                    elif typeof(other) == TYPE_DICTIONARY:
                                        other["is_blinded"] = true
                                        var current_blindness = other.get("blindness_timer", 0.0)
                                        if current_blindness < 5.0:
                                            other["blindness_timer"] = 5.0
                                        other["is_stunned"] = true
                                        var current_stun = other.get("stun_timer", 0.0)
                                        if current_stun < 3.0:
                                            other["stun_timer"] = 3.0
                                        if not other.has("base_perception_radius"):
                                            other["base_perception_radius"] = other.get("perception_radius", 100.0)
                                        other["perception_radius"] = 0.0

                    if self.world != null and "events" in self.world:
                        var pbx = self.ball.x if "x" in self.ball else (self.ball.get_meta("x") if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("x") else 0.0)
                        var pby = self.ball.y if "y" in self.ball else (self.ball.get_meta("y") if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("y") else 0.0)
                        self.world.events.append({"type": "visual_effect", "data": {"type": "flashbang_explosion", "x": pbx, "y": pby, "radius": 500.0}})

                    if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                    else:
                        if "active" in b: b.active = false
                        elif b.has_method("set_meta"): b.set_meta("active", false)

                    if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                        self.world.boosters.erase(b)
                    if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                        self.world.arena.hazards.erase(b)
            elif b_kind == "chameleon_item":
                var bx = 0.0
                var by = 0.0
                if typeof(b) == TYPE_DICTIONARY:
                    if b.has("x"): bx = b.x
                    if b.has("y"): by = b.y
                else:
                    if "x" in b: bx = b.x
                    if "y" in b: by = b.y

                var self_x = 0.0
                var self_y = 0.0
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self_x = self.ball.x if self.ball.has("x") else 0.0
                    self_y = self.ball.y if self.ball.has("y") else 0.0
                else:
                    self_x = self.ball.x if "x" in self.ball else 0.0
                    self_y = self.ball.y if "y" in self.ball else 0.0

                var dist = sqrt(pow(bx - self_x, 2) + pow(by - self_y, 2))
                var self_radius = 10.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("radius"): self_radius = self.ball.radius
                elif typeof(self.ball) == TYPE_OBJECT and "radius" in self.ball: self_radius = self.ball.radius
                var b_radius = 15.0
                if typeof(b) == TYPE_DICTIONARY and b.has("radius"): b_radius = b.radius
                elif typeof(b) == TYPE_OBJECT and "radius" in b: b_radius = b.radius

                if dist <= self_radius + b_radius + 5.0:
                    var candidates = []
                    if self.world != null and "arena" in self.world and self.world.arena != null:
                        var ar = self.world.arena
                        var haz = []
                        if typeof(ar) == TYPE_DICTIONARY and ar.has("hazards"): haz = ar.hazards
                        elif typeof(ar) == TYPE_OBJECT and "hazards" in ar: haz = ar.hazards
                        for h in haz:
                            var h_active = true
                            if typeof(h) == TYPE_DICTIONARY and h.has("active"): h_active = h.active
                            elif typeof(h) == TYPE_OBJECT and "active" in h: h_active = h.active
                            if h_active: candidates.append(h)
                    var ens = _get_enemies()
                    for e in ens:
                        candidates.append(e)

                    if candidates.size() > 0:
                        var closest = null
                        var min_dist_sq = 999999999.0
                        for c in candidates:
                            var cx = 0.0
                            var cy = 0.0
                            if typeof(c) == TYPE_DICTIONARY:
                                if c.has("x"): cx = c.x
                                if c.has("y"): cy = c.y
                            else:
                                if "x" in c: cx = c.x
                                if "y" in c: cy = c.y
                            var dsq = pow(cx - self_x, 2) + pow(cy - self_y, 2)
                            if dsq < min_dist_sq:
                                min_dist_sq = dsq
                                closest = c

                        var current_team = ""
                        var current_color = ""
                        var current_name = "Impostor"
                        if typeof(self.ball) == TYPE_DICTIONARY:
                            if self.ball.has("team"): current_team = self.ball.team
                            if self.ball.has("color"): current_color = self.ball.color
                            if self.ball.has("name"): current_name = self.ball.name
                            elif self.ball.has("label"): current_name = self.ball.label
                        else:
                            if "team" in self.ball: current_team = self.ball.team
                            if "color" in self.ball: current_color = self.ball.color
                            if "name" in self.ball: current_name = self.ball.name
                            elif "label" in self.ball: current_name = self.ball.label

                        if typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["original_team"] = current_team
                            self.ball["original_color"] = current_color
                            self.ball["original_name"] = current_name
                        else:
                            if self.ball.has_method("set_meta"):
                                self.ball.set_meta("original_team", current_team)
                                self.ball.set_meta("original_color", current_color)
                                self.ball.set_meta("original_name", current_name)

                        var target_team = ""
                        var target_color = "gray"
                        var target_name = "Hazard"

                        if typeof(closest) == TYPE_DICTIONARY:
                            if closest.has("team"): target_team = closest.team
                            elif closest.has("ball_type"): target_team = closest.ball_type
                            elif closest.has("kind"): target_team = closest.kind
                            elif closest.has("BALL_TYPE"): target_team = closest.BALL_TYPE

                            if closest.has("color"): target_color = closest.color
                            elif closest.has("color_hex"): target_color = closest.color_hex

                            if closest.has("name"): target_name = closest.name
                            elif closest.has("label"): target_name = closest.label
                            elif closest.has("kind"): target_name = closest.kind
                        else:
                            if "team" in closest: target_team = closest.team
                            elif "ball_type" in closest: target_team = closest.ball_type
                            elif "kind" in closest: target_team = closest.kind
                            elif "BALL_TYPE" in closest: target_team = closest.BALL_TYPE

                            if "color" in closest: target_color = closest.color
                            elif "color_hex" in closest: target_color = closest.color_hex

                            if "name" in closest: target_name = closest.name
                            elif "label" in closest: target_name = closest.label
                            elif "kind" in closest: target_name = closest.kind

                        if typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["team"] = target_team
                            self.ball["color"] = target_color
                            self.ball["label"] = target_name
                            self.ball["is_disguised"] = true
                            self.ball["disguise_explode"] = false
                            self.ball["disguise_timer"] = 10.0
                        else:
                            if "team" in self.ball: self.ball.team = target_team
                            if "color" in self.ball: self.ball.color = target_color
                            if "label" in self.ball: self.ball.label = target_name
                            if "is_disguised" in self.ball: self.ball.is_disguised = true
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("is_disguised", true)
                            if "disguise_explode" in self.ball: self.ball.disguise_explode = false
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("disguise_explode", false)
                            if "disguise_timer" in self.ball: self.ball.disguise_timer = 10.0
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("disguise_timer", 10.0)

                        if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                        else:
                            if "active" in b: b.active = false
                            elif b.has_method("set_meta"): b.set_meta("active", false)

                        if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                            self.world.boosters.erase(b)
                        if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                            self.world.arena.hazards.erase(b)
        # Check for phylactery
        var b_id = null
        if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): b_id = self.ball.id
        elif typeof(self.ball) == TYPE_OBJECT and "id" in self.ball: b_id = self.ball.id

        for b in boosters:
            var b_kind = ""
            if typeof(b) == TYPE_DICTIONARY and b.has("kind"): b_kind = b.kind
            elif typeof(b) == TYPE_OBJECT and "kind" in b: b_kind = b.kind
            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("kind"): b_kind = b.get_meta("kind")

            var b_owner = null
            if typeof(b) == TYPE_DICTIONARY and b.has("owner_id"): b_owner = b.owner_id
            elif typeof(b) == TYPE_OBJECT and "owner_id" in b: b_owner = b.owner_id
            elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("owner_id"): b_owner = b.get_meta("owner_id")

            if b_kind == "phylactery" and b_owner == b_id:
                if typeof(self.ball) == TYPE_DICTIONARY: self.ball["phylactery_active"] = true
                else:
                    if "phylactery_active" in self.ball: self.ball.phylactery_active = true
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("phylactery_active", true)

                if typeof(b) == TYPE_DICTIONARY: b["active"] = false
                else:
                    if "active" in b: b.active = false
                    elif b.has_method("set_meta"): b.set_meta("active", false)

                if self.world != null and "boosters" in self.world and typeof(self.world.boosters) == TYPE_ARRAY:
                    self.world.boosters.erase(b)
                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena and typeof(self.world.arena.hazards) == TYPE_ARRAY:
                    self.world.arena.hazards.erase(b)
        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        var enemies = _get_enemies()
        if enemies.size() > 0:
            var nearest_enemy = null
            var min_dist_enemy_sq = INF
            for e in enemies:
                var dist_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                if dist_sq < min_dist_enemy_sq:
                    min_dist_enemy_sq = dist_sq
                    nearest_enemy = e

            var enemy_radius = 10.0
            if "radius" in nearest_enemy: enemy_radius = nearest_enemy.radius

            if min_dist_enemy_sq > 0.0001:
                var dist_enemy = sqrt(min_dist_enemy_sq)
                if dist_enemy < ball_radius + enemy_radius + 30.0:
                    _flee(delta)
                    return

        var nearest = null
        var min_dist_sq = INF
        for b in boosters:
            var dist_sq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = b

        var dx = nearest.x - self.ball.x
        var dy = nearest.y - self.ball.y
        var dist_sq = dx*dx + dy*dy
        var dist = 0.0
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)

        var speed = 2.0
        if "speed" in self.ball: speed = self.ball.speed

        if dist_sq > 0.0001:
            var nx = dx / dist
            var ny = dy / dist
            var avoid_vec = _apply_obstacle_avoidance(nx, ny, nearest, true)
            nx = avoid_vec[0]
            ny = avoid_vec[1]

            var boid_vec = _apply_boid_rules(nx, ny)
            nx = boid_vec[0]
            ny = boid_vec[1]

            var step = speed * delta * 60
            self.ball.x += nx * min(step, dist)
            self.ball.y += ny * min(step, dist)

        # Recalculate distance after movement
        dx = nearest.x - self.ball.x
        dy = nearest.y - self.ball.y
        dist_sq = dx*dx + dy*dy
        if dist_sq > 0.0001:
            dist = sqrt(dist_sq)
        else:
            dist = 0.0

        var ball_radius = 10.0
        if "radius" in self.ball: ball_radius = self.ball.radius

        if dist <= ball_radius + 10:
            if "kind" in nearest and nearest.kind == "grapple_booster":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("grapple_hook")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "bounty_contract":
                var enemies = self._get_enemies()
                var valid_targets = []
                for e in enemies:
                    var e_alive = true
                    if "alive" in e: e_alive = e.alive
                    elif e.has_method("get_meta") and e.has_meta("alive"): e_alive = e.get_meta("alive")
                    if e_alive:
                        valid_targets.append(e)
                if valid_targets.size() > 0:
                    var target = valid_targets[randi() % valid_targets.size()]
                    var b_id = null
                    if "id" in self.ball: b_id = self.ball.id
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): b_id = self.ball.get_meta("id")

                    if typeof(target) == TYPE_DICTIONARY:
                        target["is_bounty_contract_target"] = true
                        target["bounty_contract_timer"] = 60.0
                        target["bounty_contract_hunter_id"] = b_id
                    elif target.has_method("set_meta"):
                        target.set_meta("is_bounty_contract_target", true)
                        target.set_meta("bounty_contract_timer", 60.0)
                        target.set_meta("bounty_contract_hunter_id", b_id)
                        if "is_bounty_contract_target" in target: target.is_bounty_contract_target = true
                        if "bounty_contract_timer" in target: target.bounty_contract_timer = 60.0
                        if "bounty_contract_hunter_id" in target: target.bounty_contract_hunter_id = b_id
                    else:
                        target.is_bounty_contract_target = true
                        target.bounty_contract_timer = 60.0
                        target.bounty_contract_hunter_id = b_id

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "magnetic_boots_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("magnetic_boots_timer", 10.0)
                else:
                    self.ball.magnetic_boots_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif (typeof(nearest) == TYPE_DICTIONARY and nearest.get("kind") == "hazard_jar_item") or (typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "hazard_jar_item"):
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if not self.ball.has("inventory"): self.ball["inventory"] = []
                    self.ball["inventory"].append("hazard_jar_item")
                else:
                    if not "inventory" in self.ball: self.ball.set("inventory", [])
                    self.ball.inventory.append("hazard_jar_item")

                if self.world != null and typeof(self.world) == TYPE_OBJECT and "arena" in self.world and self.world.arena != null:
                    if typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
                        self.world.arena.hazards.erase(nearest)
                    elif typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                    self.world.boosters.erase(nearest)
                elif self.world != null and typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
                    self.world.boosters.erase(nearest)


            elif (typeof(nearest) == TYPE_DICTIONARY and nearest.get("kind") == "hazard_jar_item") or (typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "hazard_jar_item"):
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if not self.ball.has("inventory"): self.ball["inventory"] = []
                    self.ball["inventory"].append({"item": "hazard_jar_item", "stored_hazard": null})
                else:
                    if not "inventory" in self.ball: self.ball.set("inventory", [])
                    self.ball.inventory.append({"item": "hazard_jar_item", "stored_hazard": null})

                if self.world != null and typeof(self.world) == TYPE_OBJECT and "arena" in self.world and self.world.arena != null:
                    if typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
                        self.world.arena.hazards.erase(nearest)
                    elif typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                    self.world.boosters.erase(nearest)
                elif self.world != null and typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
                    self.world.boosters.erase(nearest)

            elif "kind" in nearest and nearest.kind == "holo_decoy_booster":
                var decoy = null
                if typeof(self.ball) == TYPE_DICTIONARY:
                    decoy = self.ball.duplicate()
                elif self.ball.has_method("duplicate"):
                    decoy = self.ball.duplicate()

                if decoy != null:
                    if "id" in decoy:
                        decoy.id = randi() % 90000 + 10000

                    var vx = self.ball.vx if "vx" in self.ball else (self.ball.get("vx", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("vx") if self.ball.has_method("get_meta") and self.ball.has_meta("vx") else 0.0))
                    var vy = self.ball.vy if "vy" in self.ball else (self.ball.get("vy", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("vy") if self.ball.has_method("get_meta") and self.ball.has_meta("vy") else 0.0))
                    var speed = sqrt(vx*vx + vy*vy)

                    if speed < 0.001:
                        var angle = randf() * PI * 2.0
                        var b_speed = self.ball.speed if "speed" in self.ball else (self.ball.get("speed", 100.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("speed") if self.ball.has_method("get_meta") and self.ball.has_meta("speed") else 100.0))
                        vx = cos(angle) * b_speed
                        vy = sin(angle) * b_speed

                    if typeof(decoy) == TYPE_DICTIONARY:
                        decoy["is_decoy"] = true
                        decoy["decoy_type"] = "hologram"
                        decoy["decoy_timer"] = 5.0
                        decoy["hp"] = 1.0
                        decoy["vx"] = vx
                        decoy["vy"] = vy
                        if "id" in self.ball:
                            decoy["owner_id"] = self.ball.id
                    elif decoy.has_method("set_meta"):
                        decoy.set_meta("is_decoy", true)
                        decoy.set_meta("decoy_type", "hologram")
                        decoy.set_meta("decoy_timer", 5.0)
                        if "hp" in decoy:
                            decoy.hp = 1.0
                        else:
                            decoy.set_meta("hp", 1.0)
                        if "vx" in decoy:
                            decoy.vx = vx
                            decoy.vy = vy
                        else:
                            decoy.set_meta("vx", vx)
                            decoy.set_meta("vy", vy)
                        if "id" in self.ball:
                            decoy.set_meta("owner_id", self.ball.id)

                    if self.world != null and "balls" in self.world:
                        self.world.balls.append(decoy)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "decoy_trap_booster":
                var current_timer = 0.0
                if self.ball.has_method("get_meta") and self.ball.has_meta("stealth_drone_timer"):
                    current_timer = float(self.ball.get_meta("stealth_drone_timer"))
                elif "stealth_drone_timer" in self.ball:
                    current_timer = float(self.ball.stealth_drone_timer)

                var new_timer = max(current_timer, 3.0)
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("has_stealth_drone", true)
                    self.ball.set_meta("stealth_drone_timer", new_timer)
                else:
                    self.ball["has_stealth_drone"] = true
                    self.ball["stealth_drone_timer"] = new_timer

                var decoy = null
                if typeof(self.ball) == TYPE_DICTIONARY:
                    decoy = self.ball.duplicate()
                elif self.ball.has_method("duplicate"):
                    decoy = self.ball.duplicate()

                if decoy != null:
                    if "id" in decoy:
                        decoy.id = randi() % 90000 + 10000
                    if typeof(decoy) == TYPE_DICTIONARY:
                        decoy["is_decoy"] = true
                        decoy["decoy_type"] = "siren"
                        decoy["siren_ping_timer"] = 1.0
                        decoy["decoy_timer"] = 5.0
                        if "id" in self.ball:
                            decoy["owner_id"] = self.ball.id
                    elif decoy.has_method("set_meta"):
                        decoy.set_meta("is_decoy", true)
                        decoy.set_meta("decoy_type", "siren")
                        decoy.set_meta("siren_ping_timer", 1.0)
                        decoy.set_meta("decoy_timer", 5.0)
                        if "id" in self.ball:
                            decoy.set_meta("owner_id", self.ball.id)

                    if self.world != null and "balls" in self.world:
                        self.world.balls.append(decoy)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)


            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "safe_zone_teleport_booster":
                self.ball.set_meta("safe_zone_teleport_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "safe_zone_teleport_booster":
                self.ball.set_meta("safe_zone_teleport_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "safe_zone_booster":
                self.ball.set_meta("safe_zone_booster_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "safe_zone_booster":
                self.ball.set_meta("safe_zone_booster_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "time_stop_booster":

                var entities = []
                if self.world != null:
                    if "entities" in self.world: entities = self.world.entities
                    elif "balls" in self.world: entities = self.world.balls
                for e in entities:
                    var e_id = e.get("id") if typeof(e) == TYPE_DICTIONARY else (e.get_meta("id") if e.has_method("has_meta") and e.has_meta("id") else (e.id if "id" in e else null))
                    var b_id = self.ball.get("id") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("id") if self.ball.has_method("has_meta") and self.ball.has_meta("id") else (self.ball.id if "id" in self.ball else null))
                    if e_id != null and b_id != null and e_id != b_id:
                        var is_alive = true
                        if typeof(e) == TYPE_DICTIONARY:
                            if e.has("alive"): is_alive = e.alive
                        else:
                            if "alive" in e: is_alive = e.alive
                        if is_alive:
                            var cur_stun = 0.0
                            if typeof(e) == TYPE_DICTIONARY:
                                cur_stun = float(e.get("stun_timer", 0.0))
                                e["stun_timer"] = max(cur_stun, 3.0)
                            elif e.has_method("set_meta"):
                                cur_stun = float(e.get_meta("stun_timer")) if e.has_meta("stun_timer") else (float(e.stun_timer) if "stun_timer" in e else 0.0)
                                e.set_meta("stun_timer", max(cur_stun, 3.0))
                                if "stun_timer" in e: e.stun_timer = max(cur_stun, 3.0)
                            elif "stun_timer" in e:
                                cur_stun = float(e.stun_timer)
                                e.stun_timer = max(cur_stun, 3.0)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    for h in self.world.arena.hazards:
                        var is_disabled = false
                        if typeof(h) == TYPE_DICTIONARY:
                            if h.has("is_disabled_by_flare"): is_disabled = h.is_disabled_by_flare
                        else:
                            if h.has_method("has_meta") and h.has_meta("is_disabled_by_flare"):
                                is_disabled = h.get_meta("is_disabled_by_flare")
                            elif "is_disabled_by_flare" in h:
                                is_disabled = h.is_disabled_by_flare
                        if not is_disabled:
                            var cur_frozen = 0.0
                            if typeof(h) == TYPE_DICTIONARY:
                                cur_frozen = float(h.get("frozen_timer", 0.0))
                                h["frozen_timer"] = max(cur_frozen, 3.0)
                            elif h.has_method("set_meta"):
                                cur_frozen = float(h.get_meta("frozen_timer")) if h.has_meta("frozen_timer") else (float(h.frozen_timer) if "frozen_timer" in h else 0.0)
                                h.set_meta("frozen_timer", max(cur_frozen, 3.0))
                                if "frozen_timer" in h: h.frozen_timer = max(cur_frozen, 3.0)
                            elif "frozen_timer" in h:
                                cur_frozen = float(h.frozen_timer)
                                h.frozen_timer = max(cur_frozen, 3.0)

                if self.world != null and "events" in self.world:
                    var b_id = self.ball.get("id") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("id") if self.ball.has_method("has_meta") and self.ball.has_meta("id") else (self.ball.id if "id" in self.ball else null))
                    self.world.events.append({"type": "time_stop", "data": {"id": b_id}})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "storm_link_booster":
                var enemies = self._get_enemies_internal()
                if enemies.size() > 0:
                    var min_d = 999999999.0
                    var closest_enemy = null
                    var bx = self.ball.get_meta("x") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("x") else self.ball.x if "x" in self.ball else 0.0
                    var by = self.ball.get_meta("y") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("y") else self.ball.y if "y" in self.ball else 0.0
                    for e in enemies:
                        var ex = e.get_meta("x") if typeof(e) != TYPE_DICTIONARY and e.has_method("has_meta") and e.has_meta("x") else e.x if "x" in e else 0.0
                        var ey = e.get_meta("y") if typeof(e) != TYPE_DICTIONARY and e.has_method("has_meta") and e.has_meta("y") else e.y if "y" in e else 0.0
                        var d = (ex - bx)*(ex - bx) + (ey - by)*(ey - by)
                        if d < min_d:
                            min_d = d
                            closest_enemy = e
                    if closest_enemy != null:
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("storm_link_timer", 5.0)
                            self.ball.set_meta("storm_link_target", closest_enemy)
                        else:
                            self.ball.storm_link_timer = 5.0
                            self.ball.storm_link_target = closest_enemy
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "orbital_link_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("orbital_link_timer", 10.0)
                else:
                    self.ball.orbital_link_timer = 10.0
                if self.world != null and "events" in self.world:
                    var bx = self.ball.get("x") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("x") if self.ball.has_method("has_meta") and self.ball.has_meta("x") else (self.ball.x if "x" in self.ball else 0.0))
                    var by = self.ball.get("y") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("y") if self.ball.has_method("has_meta") and self.ball.has_meta("y") else (self.ball.y if "y" in self.ball else 0.0))
                    self.world.events.append({"type": "orbital_link", "x": bx, "y": by})
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "anchor_point_booster":
                var bx = self.ball.get("x") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("x") if self.ball.has_method("has_meta") and self.ball.has_meta("x") else (self.ball.x if "x" in self.ball else 0.0))
                var by = self.ball.get("y") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("y") if self.ball.has_method("has_meta") and self.ball.has_meta("y") else (self.ball.y if "y" in self.ball else 0.0))
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["anchor_point_timer"] = 10.0
                    self.ball["anchor_point_x"] = bx
                    self.ball["anchor_point_y"] = by
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("anchor_point_timer", 10.0)
                    self.ball.set_meta("anchor_point_x", bx)
                    self.ball.set_meta("anchor_point_y", by)
                else:
                    self.ball.anchor_point_timer = 10.0
                    self.ball.anchor_point_x = bx
                    self.ball.anchor_point_y = by

                if self.world != null and "events" in self.world:
                    self.world.events.append({"type": "anchor_point", "x": bx, "y": by})
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "tether_booster":
                var enemies = self._get_enemies_internal()
                if enemies.size() > 0:
                    var min_d = 999999999.0
                    var closest_enemy = null
                    var bx = self.ball.get_meta("x") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("x") else self.ball.x if "x" in self.ball else 0.0
                    var by = self.ball.get_meta("y") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("y") else self.ball.y if "y" in self.ball else 0.0
                    for e in enemies:
                        var ex = e.get_meta("x") if typeof(e) != TYPE_DICTIONARY and e.has_method("has_meta") and e.has_meta("x") else e.x if "x" in e else 0.0
                        var ey = e.get_meta("y") if typeof(e) != TYPE_DICTIONARY and e.has_method("has_meta") and e.has_meta("y") else e.y if "y" in e else 0.0
                        var d = (ex - bx)*(ex - bx) + (ey - by)*(ey - by)
                        if d < min_d:
                            min_d = d
                            closest_enemy = e
                    if closest_enemy != null:
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("tether_booster_timer", 3.0)
                            self.ball.set_meta("tether_booster_target", closest_enemy)
                        else:
                            self.ball.tether_booster_timer = 3.0
                            self.ball.tether_booster_target = closest_enemy
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "recall_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["recall_timer"] = 5.0
                    self.ball["recall_state"] = {
                        "x": float(self.ball.get("x", 0.0)),
                        "y": float(self.ball.get("y", 0.0)),
                        "hp": float(self.ball.get("hp", self.ball.get("max_hp", 100.0)))
                    }
                else:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("recall_timer", 5.0)
                        self.ball.set_meta("recall_state", {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        })
                    else:
                        self.ball.recall_timer = 5.0
                        self.ball.recall_state = {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        }
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "survival_rewind_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["survival_rewind_timer"] = 5.0
                    self.ball["survival_rewind_state"] = {
                        "x": float(self.ball.get("x", 0.0)),
                        "y": float(self.ball.get("y", 0.0)),
                        "hp": float(self.ball.get("hp", self.ball.get("max_hp", 100.0)))
                    }
                else:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("survival_rewind_timer", 5.0)
                        self.ball.set_meta("survival_rewind_state", {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        })
                    else:
                        self.ball.survival_rewind_timer = 5.0
                        self.ball.survival_rewind_state = {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        }
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "snapback_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["snapback_timer"] = 5.0
                    self.ball["snapback_state"] = {
                        "x": float(self.ball.get("x", 0.0)),
                        "y": float(self.ball.get("y", 0.0))
                    }
                else:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("snapback_timer", 5.0)
                        self.ball.set_meta("snapback_state", {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y)
                        })
                    else:
                        self.ball.snapback_timer = 5.0
                        self.ball.snapback_state = {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y)
                        }
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "time_rewind_booster":
                self.ball.set_meta("time_rewind_booster_active", true)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "instant_rewind_booster":
                var history = []
                if typeof(self.ball) == TYPE_DICTIONARY:
                    history = self.ball.get("state_history", [])
                else:
                    if self.ball.has_method("has_meta") and self.ball.has_meta("state_history"):
                        history = self.ball.get_meta("state_history")
                    elif "state_history" in self.ball:
                        history = self.ball.state_history
                if history.size() > 0:
                    # Retrieve state from ~3 seconds ago for instant rewind
                    var past_state_3s = history[0]
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        # Rewind positional coordinates and health
                        self.ball["x"] = past_state_3s.get("x", self.ball.get("x", 0.0))
                        self.ball["y"] = past_state_3s.get("y", self.ball.get("y", 0.0))
                        self.ball["hp"] = past_state_3s.get("hp", self.ball.get("max_hp", 100.0))
                        if "attack_timer" in past_state_3s: self.ball["attack_timer"] = past_state_3s["attack_timer"]
                        if "skill_timer" in past_state_3s: self.ball["skill_timer"] = past_state_3s["skill_timer"]
                    else:
                        # Rewind positional coordinates and health
                        self.ball.x = past_state_3s.get("x", self.ball.x)
                        self.ball.y = past_state_3s.get("y", self.ball.y)
                        if "hp" in self.ball:
                            self.ball.hp = past_state_3s.get("hp", self.ball.max_hp if "max_hp" in self.ball else 100.0)
                        if "attack_timer" in past_state_3s and "attack_timer" in self.ball:
                            self.ball.attack_timer = past_state_3s["attack_timer"]
                        if "skill_timer" in past_state_3s and "skill_timer" in self.ball:
                            self.ball.skill_timer = past_state_3s["skill_timer"]

                    if self.world != null and "events" in self.world:
                        self.world.events.append({"type": "time_rewind", "data": {"id": self.ball.get("id", -1) if typeof(self.ball) == TYPE_DICTIONARY else self.ball.id}})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "kinetic_shield_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("kinetic_shield_active", true)
                    self.ball.set_meta("kinetic_shield_timer", 10.0)
                    self.ball.set_meta("kinetic_shield_stored_damage", 0.0)
                else:
                    self.ball.kinetic_shield_active = true
                    self.ball.kinetic_shield_timer = 10.0
                    self.ball.kinetic_shield_stored_damage = 0.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "anvil_piece":
                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("mode") and self.world.mode.get("name", "") == "Blacksmith Boss":
                    self.world.mode.anvil_pieces_collected += 1
                    if self.world.has("events"):
                        self.world.events.append({"type": "anvil_piece_collected", "data": {"count": self.world.mode.anvil_pieces_collected, "x": self.ball.x, "y": self.ball.y}})
                elif typeof(self.world) == TYPE_OBJECT and "mode" in self.world and self.world.mode.name == "Blacksmith Boss":
                    self.world.mode.anvil_pieces_collected += 1

                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
                    self.world.boosters.erase(nearest)
                elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                    self.world.boosters.erase(nearest)

                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("arena") and typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
                    self.world.arena.hazards.erase(nearest)
                elif typeof(self.world) == TYPE_OBJECT and "arena" in self.world and "hazards" in self.world.arena:
                    self.world.arena.hazards.erase(nearest)

            elif "kind" in nearest and nearest.kind == "legendary_loot":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                if typeof(inv) == TYPE_ARRAY and not inv.has("legendary_loot"): inv.append("legendary_loot")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)

                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["damage"] = self.ball.get("damage", 10.0) * 3.0
                    self.ball["speed"] = self.ball.get("speed", 100.0) * 1.5
                else:
                    if "damage" in self.ball: self.ball.damage = self.ball.damage * 3.0
                    if "speed" in self.ball: self.ball.speed = self.ball.speed * 1.5

                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("events"):
                    self.world.events.append({"type": "legendary_loot_collected", "data": {"x": self.ball.get("x", 0), "y": self.ball.get("y", 0)}})

                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
                    self.world.boosters.erase(nearest)
                elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                    self.world.boosters.erase(nearest)

                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("arena") and typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
                    self.world.arena.hazards.erase(nearest)
                elif typeof(self.world) == TYPE_OBJECT and "arena" in self.world and "hazards" in self.world.arena:
                    self.world.arena.hazards.erase(nearest)

            elif "kind" in nearest and nearest.kind == "overclock_booster":
				var inv = []
				if "inventory" in self.ball: inv = self.ball.inventory
				elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
				if typeof(inv) == TYPE_ARRAY and not inv.has("overclock_booster"): inv.append("overclock_booster")
				if "inventory" in self.ball: self.ball.inventory = inv
				elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)

				if "overclock_timer" in self.ball: self.ball.overclock_timer = 5.0
				elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("overclock_timer", 5.0)

				if self.world != null and "events" in self.world:
					self.world.events.append({"type": "overclock_start", "x": self.ball.x, "y": self.ball.y})

				if self.world != null and "balls" in self.world:
					for b in self.world.balls:
						if b != self.ball:
							var my_team = -1
							if "team" in self.ball: my_team = self.ball.team
							elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
							elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("team"): my_team = self.ball.team
							var b_team = -2
							if "team" in b: b_team = b.team
							elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("team"): b_team = b.get_meta("team")
							elif typeof(b) == TYPE_DICTIONARY and b.has("team"): b_team = b.team
							if b_team == my_team:
								var dist_sq = (b.x - self.ball.x)*(b.x - self.ball.x) + (b.y - self.ball.y)*(b.y - self.ball.y)
								if dist_sq < 40000.0:
									var binv = []
									if "inventory" in b: binv = b.inventory
									elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("inventory"): binv = b.get_meta("inventory")
									if typeof(binv) == TYPE_ARRAY and not binv.has("overclock_booster"): binv.append("overclock_booster")
									if "inventory" in b: b.inventory = binv
									elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("inventory", binv)

									if "overclock_timer" in b: b.overclock_timer = 5.0
									elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("overclock_timer", 5.0)

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "drone_item":
                self.ball.has_drone = true
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "deployable_mud_puddle":
                var b_inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                    if self.ball.has_meta("inventory"): b_inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: b_inv = self.ball.inventory
                b_inv.append("deployable_mud_puddle")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", b_inv)
                elif "inventory" in self.ball: self.ball.inventory = b_inv

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "deployable_proximity_mud_puddle":
                var b_inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta"):
                    if self.ball.has_meta("inventory"): b_inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: b_inv = self.ball.inventory
                b_inv.append("deployable_proximity_mud_puddle")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", b_inv)
                elif "inventory" in self.ball: self.ball.inventory = b_inv

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "gravity_multiplier_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("gravity_multiplier_timer", 10.0)
                else:
                    self.ball.gravity_multiplier_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "reverse_gravity_booster":
                if self.world != null and "balls" in self.world:
                    for other in self.world.balls:
                        var my_team = -2
                        if "team" in self.ball: my_team = self.ball.team
                        var other_team = -1
                        if "team" in other: other_team = other.team
                        if other_team != my_team and other.get("hp", 0) > 0:
                            if "invert_timer" in other:
                                other.invert_timer = 3.0
                            elif other.has_method("set_meta"):
                                other.set_meta("invert_timer", 3.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx >= 0:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "sticky_mine_booster":
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var mine = null
                    if load("res://src/arena/procedural_arena.gd") != null:
                        mine = load("res://src/arena/procedural_arena.gd").Hazard.new()

                    if mine != null:
                        mine.id = self.world.arena.hazards.size() + 50000
                        mine.x = self.ball.x if "x" in self.ball else (self.ball.get_meta("x") if self.ball.has_method("get_meta") and self.ball.has_meta("x") else 0.0)
                        mine.y = self.ball.y if "y" in self.ball else (self.ball.get_meta("y") if self.ball.has_method("get_meta") and self.ball.has_meta("y") else 0.0)
                        mine.radius = 20.0
                        mine.kind = "sticky_mine"
                        mine.set_meta("duration", 10.0)
                        var bid = self.ball.id if "id" in self.ball else (self.ball.get_meta("id") if self.ball.has_method("get_meta") and self.ball.has_meta("id") else null)
                        mine.set_meta("owner_id", bid)
                        mine.set_meta("attached_id", null)
                        self.world.arena.hazards.append(mine)

                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx != -1:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "turret_linker_booster":
                var ball_type = ""
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("ball_type"): ball_type = self.ball.ball_type
                elif typeof(self.ball) == TYPE_OBJECT and "ball_type" in self.ball: ball_type = self.ball.ball_type

                if ball_type == "engineer":
                    if self.world != null and "balls" in self.world:
                        var my_team = ""
                        if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("team"): my_team = self.ball.team
                        elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
                        elif typeof(self.ball) == TYPE_OBJECT and "team" in self.ball: my_team = self.ball.team

                        if my_team == "": my_team = ball_type

                        var self_id = -1
                        if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): self_id = self.ball.id
                        elif typeof(self.ball) == TYPE_OBJECT and "id" in self.ball: self_id = self.ball.id

                        for b in self.world.balls:
                            var is_turret = false
                            if typeof(b) == TYPE_DICTIONARY and b.has("is_turret"): is_turret = b.is_turret
                            elif typeof(b) == TYPE_OBJECT and "is_turret" in b: is_turret = b.is_turret

                            var b_owner = -1
                            if typeof(b) == TYPE_DICTIONARY and b.has("owner_id"): b_owner = b.owner_id
                            elif typeof(b) == TYPE_OBJECT and "owner_id" in b: b_owner = b.owner_id

                            if is_turret and b_owner == self_id:
                                var nearest_enemy = null
                                var min_dist = 999999.0
                                for eb in self.world.balls:
                                    var is_alive = true
                                    if typeof(eb) == TYPE_DICTIONARY and eb.has("alive"): is_alive = eb.alive
                                    elif typeof(eb) == TYPE_OBJECT and "alive" in eb: is_alive = eb.alive

                                    if is_alive and eb != b:
                                        var e_team = ""
                                        if typeof(eb) == TYPE_DICTIONARY and eb.has("team"): e_team = eb.team
                                        elif typeof(eb) == TYPE_OBJECT and eb.has_method("has_meta") and eb.has_meta("team"): e_team = eb.get_meta("team")
                                        elif typeof(eb) == TYPE_OBJECT and "team" in eb: e_team = eb.team

                                        if e_team == "":
                                            if typeof(eb) == TYPE_DICTIONARY and eb.has("ball_type"): e_team = eb.ball_type
                                            elif typeof(eb) == TYPE_OBJECT and "ball_type" in eb: e_team = eb.ball_type

                                        var is_decoy = false
                                        if typeof(eb) == TYPE_DICTIONARY and eb.has("is_decoy"): is_decoy = eb.is_decoy
                                        elif typeof(eb) == TYPE_OBJECT and "is_decoy" in eb: is_decoy = eb.is_decoy

                                        if e_team != my_team and not is_decoy:
                                            var bx = 0.0
                                            var by = 0.0
                                            if typeof(b) == TYPE_DICTIONARY:
                                                if b.has("x"): bx = b.x
                                                if b.has("y"): by = b.y
                                            else:
                                                if "x" in b: bx = b.x
                                                if "y" in b: by = b.y

                                            var ebx = 0.0
                                            var eby = 0.0
                                            if typeof(eb) == TYPE_DICTIONARY:
                                                if eb.has("x"): ebx = eb.x
                                                if eb.has("y"): eby = eb.y
                                            else:
                                                if "x" in eb: ebx = eb.x
                                                if "y" in eb: eby = eb.y

                                            var dx = ebx - bx
                                            var dy = eby - by
                                            var dist_sq = dx * dx + dy * dy
                                            if dist_sq < min_dist:
                                                min_dist = dist_sq
                                                nearest_enemy = eb

                                if nearest_enemy != null:
                                    var e_hp = 0.0
                                    if typeof(nearest_enemy) == TYPE_DICTIONARY and nearest_enemy.has("hp"): e_hp = nearest_enemy.hp
                                    elif typeof(nearest_enemy) == TYPE_OBJECT and "hp" in nearest_enemy: e_hp = nearest_enemy.hp

                                    e_hp -= 20.0

                                    if typeof(nearest_enemy) == TYPE_DICTIONARY:
                                        nearest_enemy.hp = e_hp
                                        if e_hp <= 0: nearest_enemy.alive = false
                                    elif typeof(nearest_enemy) == TYPE_OBJECT:
                                        if "hp" in nearest_enemy: nearest_enemy.hp = e_hp
                                        if e_hp <= 0 and "alive" in nearest_enemy: nearest_enemy.alive = false

                                    var b_id = -1
                                    if typeof(b) == TYPE_DICTIONARY and b.has("id"): b_id = b.id
                                    elif typeof(b) == TYPE_OBJECT and "id" in b: b_id = b.id

                                    var en_id = -1
                                    if typeof(nearest_enemy) == TYPE_DICTIONARY and nearest_enemy.has("id"): en_id = nearest_enemy.id
                                    elif typeof(nearest_enemy) == TYPE_OBJECT and "id" in nearest_enemy: en_id = nearest_enemy.id

                                    var en_x = 0.0
                                    var en_y = 0.0
                                    if typeof(nearest_enemy) == TYPE_DICTIONARY:
                                        if nearest_enemy.has("x"): en_x = nearest_enemy.x
                                        if nearest_enemy.has("y"): en_y = nearest_enemy.y
                                    elif typeof(nearest_enemy) == TYPE_OBJECT:
                                        if "x" in nearest_enemy: en_x = nearest_enemy.x
                                        if "y" in nearest_enemy: en_y = nearest_enemy.y

                                    if not ("events" in self.world):
                                        self.world.events = []
                                    self.world.events.append({"type": "turret_laser_blast", "source": b_id, "target": en_id, "x": en_x, "y": en_y})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx >= 0:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "ghost_mode_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["ghost_mode_timer"] = 5.0
                    self.ball["intangible"] = true
                    self.ball["ghost_mode_active"] = true
                else:
                    self.ball.set_meta("ghost_mode_timer", 5.0)
                    if "ghost_mode_timer" in self.ball: self.ball.ghost_mode_timer = 5.0
                    self.ball.set_meta("intangible", true)
                    if "intangible" in self.ball: self.ball.intangible = true
                    self.ball.set_meta("ghost_mode_active", true)
                    if "ghost_mode_active" in self.ball: self.ball.ghost_mode_active = true
                    self.ball.set_meta("is_ghost", true)
                    if "is_ghost" in self.ball: self.ball.is_ghost = true
                # Apply to nearby allies
                if self.world != null and "balls" in self.world:
                    var my_team = ""
                    if "team" in self.ball: my_team = self.ball.team
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
                    elif "ball_type" in self.ball: my_team = self.ball.ball_type
                    for ob in self.world.balls:
                        var ob_alive = true
                        if "alive" in ob: ob_alive = ob.alive
                        elif ob.has_method("has_meta") and ob.has_meta("alive"): ob_alive = ob.get_meta("alive")
                        if ob_alive and ob != self.ball:
                            var ob_team = ""
                            if "team" in ob: ob_team = ob.team
                            elif ob.has_method("has_meta") and ob.has_meta("team"): ob_team = ob.get_meta("team")
                            elif "ball_type" in ob: ob_team = ob.ball_type
                            if ob_team == my_team:
                                var dx = ob.x - self.ball.x
                                var dy = ob.y - self.ball.y
                                if dx*dx + dy*dy <= 40000.0:
                                    if typeof(ob) == TYPE_DICTIONARY:
                                        ob["ghost_mode_timer"] = 5.0
                                        ob["intangible"] = true
                                        ob["ghost_mode_active"] = true
                                    else:
                                        ob.set_meta("ghost_mode_timer", 5.0)
                                        if "ghost_mode_timer" in ob: ob.ghost_mode_timer = 5.0
                                        ob.set_meta("intangible", true)
                                        if "intangible" in ob: ob.intangible = true
                                        ob.set_meta("ghost_mode_active", true)
                                        if "ghost_mode_active" in ob: ob.ghost_mode_active = true
                                        ob.set_meta("is_ghost", true)
                                        if "is_ghost" in ob: ob.is_ghost = true

                if self.world != null and "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx >= 0:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "sticky_boots_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["has_sticky_boots"] = true
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                    self.ball.set_meta("has_sticky_boots", true)
                    if "has_sticky_boots" in self.ball: self.ball.has_sticky_boots = true
                if self.world != null and "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx >= 0:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "fire_sticky_bomb_booster":
                ball.active_skill = "fire_sticky_bomb"
                ball.skill_timer = 4.0
                if typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world["arena"]) == TYPE_DICTIONARY and world["arena"].has("hazards"):
                    world["arena"]["hazards"].erase(nearest)
                elif typeof(world) == TYPE_OBJECT and world.get("arena") != null and typeof(world.arena) == TYPE_OBJECT and world.arena.get("hazards") != null:
                    world.arena.hazards.erase(nearest)
                if typeof(world) == TYPE_DICTIONARY and world.has("boosters"):
                    world["boosters"].erase(nearest)
                elif typeof(world) == TYPE_OBJECT and world.get("boosters") != null:
                    world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "sticky_bomb_booster":
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var bomb = {}
                    bomb["id"] = self.world.arena.hazards.size() + 50000
                    bomb["x"] = self.ball.get("x", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.x if "x" in self.ball else 0.0)
                    bomb["y"] = self.ball.get("y", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.y if "y" in self.ball else 0.0)
                    bomb["radius"] = 20.0
                    bomb["kind"] = "sticky_bomb"
                    bomb["duration"] = 0.0
                    var bid = self.ball.get("id", null) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.id if "id" in self.ball else null)
                    bomb["owner_id"] = bid
                    bomb["attached_id"] = null
                    self.world.arena.hazards.append(bomb)

                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx != -1:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)

            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "sticky_mine_booster":
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var mine = {}
                    mine["id"] = self.world.arena.hazards.size() + 50000
                    mine["x"] = self.ball.get("x", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.x if "x" in self.ball else 0.0)
                    mine["y"] = self.ball.get("y", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.y if "y" in self.ball else 0.0)
                    mine["radius"] = 20.0
                    mine["kind"] = "sticky_mine"
                    mine["duration"] = 10.0
                    var bid = self.ball.get("id", null) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.id if "id" in self.ball else null)
                    mine["owner_id"] = bid
                    mine["attached_id"] = null
                    self.world.arena.hazards.append(mine)

                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx != -1:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "ghost_mode_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["ghost_mode_timer"] = 5.0
                    self.ball["intangible"] = true
                    self.ball["ghost_mode_active"] = true
                else:
                    self.ball.set_meta("ghost_mode_timer", 5.0)
                    if "ghost_mode_timer" in self.ball: self.ball.ghost_mode_timer = 5.0
                    self.ball.set_meta("intangible", true)
                    if "intangible" in self.ball: self.ball.intangible = true
                    self.ball.set_meta("ghost_mode_active", true)
                    if "ghost_mode_active" in self.ball: self.ball.ghost_mode_active = true
                    self.ball.set_meta("is_ghost", true)
                    if "is_ghost" in self.ball: self.ball.is_ghost = true
                # Apply to nearby allies
                if self.world != null and "balls" in self.world:
                    var my_team = ""
                    if "team" in self.ball: my_team = self.ball.team
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("team"): my_team = self.ball.get_meta("team")
                    elif "ball_type" in self.ball: my_team = self.ball.ball_type
                    for ob in self.world.balls:
                        var ob_alive = true
                        if "alive" in ob: ob_alive = ob.alive
                        elif ob.has_method("has_meta") and ob.has_meta("alive"): ob_alive = ob.get_meta("alive")
                        if ob_alive and ob != self.ball:
                            var ob_team = ""
                            if "team" in ob: ob_team = ob.team
                            elif ob.has_method("has_meta") and ob.has_meta("team"): ob_team = ob.get_meta("team")
                            elif "ball_type" in ob: ob_team = ob.ball_type
                            if ob_team == my_team:
                                var dx = ob.x - self.ball.x
                                var dy = ob.y - self.ball.y
                                if dx*dx + dy*dy <= 40000.0:
                                    if typeof(ob) == TYPE_DICTIONARY:
                                        ob["ghost_mode_timer"] = 5.0
                                        ob["intangible"] = true
                                        ob["ghost_mode_active"] = true
                                    else:
                                        ob.set_meta("ghost_mode_timer", 5.0)
                                        if "ghost_mode_timer" in ob: ob.ghost_mode_timer = 5.0
                                        ob.set_meta("intangible", true)
                                        if "intangible" in ob: ob.intangible = true
                                        ob.set_meta("ghost_mode_active", true)
                                        if "ghost_mode_active" in ob: ob.ghost_mode_active = true
                                        ob.set_meta("is_ghost", true)
                                        if "is_ghost" in ob: ob.is_ghost = true

                if self.world != null and "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
                    var h_idx = self.world.arena.hazards.find(nearest)
                    if h_idx >= 0:
                        self.world.arena.hazards.remove_at(h_idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "siren_decoy_booster":
                var decoy = null
                if self.ball.has_method("duplicate"):
                    decoy = self.ball.duplicate()
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    decoy = self.ball.duplicate()

                if decoy != null:
                    var next_id = randi() % 90000 + 10000
                    if self.world != null and "next_id" in self.world:
                        next_id = self.world.next_id

                    if typeof(decoy) == TYPE_DICTIONARY:
                        decoy["id"] = next_id
                        if "hp" in self.ball: decoy["hp"] = self.ball.hp
                        else: decoy["hp"] = 100.0
                        if "max_hp" in self.ball: decoy["max_hp"] = self.ball.max_hp
                        else: decoy["max_hp"] = 100.0
                        decoy["damage"] = 0
                        decoy["is_decoy"] = true
                        decoy["decoy_timer"] = 5.0
                        decoy["owner_id"] = self_id_stat
                        decoy["decoy_type"] = "siren"
                        decoy["siren_ping_timer"] = 1.0
                    elif decoy.has_method("set_meta"):
                        decoy.set_meta("id", next_id)
                        var chp = 100.0
                        if "hp" in self.ball: chp = self.ball.hp
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("hp"): chp = self.ball.get_meta("hp")
                        decoy.set_meta("hp", chp)
                        var cmhp = 100.0
                        if "max_hp" in self.ball: cmhp = self.ball.max_hp
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("max_hp"): cmhp = self.ball.get_meta("max_hp")
                        decoy.set_meta("max_hp", cmhp)
                        decoy.set_meta("damage", 0)
                        decoy.set_meta("is_decoy", true)
                        decoy.set_meta("decoy_timer", 5.0)
                        decoy.set_meta("owner_id", self_id_stat)
                        decoy.set_meta("decoy_type", "siren")
                        decoy.set_meta("siren_ping_timer", 1.0)

                    if self.world != null and "balls" in self.world:
                        self.world.balls.append(decoy)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "decoy_item":
                var decoy = null
                if typeof(self.ball) == TYPE_DICTIONARY:
                    decoy = self.ball.duplicate()
                elif self.ball.has_method("duplicate"):
                    decoy = self.ball.duplicate()

                if decoy != null:
                    if "id" in decoy:
                        decoy.id = randi() % 90000 + 10000
                    if "hp" in decoy and "max_hp" in decoy:
                        decoy.max_hp = float(self.ball.max_hp)
                        decoy.hp = float(self.ball.hp)
                    if "damage" in decoy:
                        decoy.damage = 0.0
                    var self_id_stat = -2
                    if "id" in self.ball: self_id_stat = self.ball.id
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id_stat = self.ball.get_meta("id")

                    if decoy.has_method("set_meta"):
                        decoy.set_meta("owner_id", self_id_stat)
                        decoy.set_meta("has_swapped", false)
                        decoy.set_meta("is_decoy", true)
                        decoy.set_meta("decoy_timer", 5.0)
                        decoy.set_meta("decoy_type", "explosive")
                    elif typeof(decoy) == TYPE_DICTIONARY:
                        decoy["is_decoy"] = true
                        decoy["decoy_timer"] = 5.0
                        decoy["owner_id"] = self_id_stat
                        decoy["decoy_type"] = "explosive"

                    if self.world != null and "balls" in self.world:
                        self.world.balls.append(decoy)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "blood_magic_booster":
                var cur_bmt = 0.0
                if typeof(ball) == TYPE_OBJECT and ball.has_method("has_meta") and ball.has_meta("blood_magic_timer"): cur_bmt = float(ball.get_meta("blood_magic_timer"))
                elif "blood_magic_timer" in ball: cur_bmt = float(ball.blood_magic_timer)
                if typeof(ball) == TYPE_OBJECT and ball.has_method("set_meta"): ball.set_meta("blood_magic_timer", cur_bmt + 15.0)
                elif "blood_magic_timer" in ball or typeof(ball) == TYPE_DICTIONARY: ball.blood_magic_timer = cur_bmt + 15.0

                var st = 0.0
                if typeof(ball) == TYPE_OBJECT and ball.has_method("has_meta") and ball.has_meta("skill_timer"): st = float(ball.get_meta("skill_timer"))
                elif "skill_timer" in self.ball: st = float(ball.skill_timer)
                if typeof(ball) == TYPE_OBJECT and ball.has_method("set_meta"): ball.set_meta("_prev_skill_timer", st)
                elif "_prev_skill_timer" in ball or typeof(ball) == TYPE_DICTIONARY: ball._prev_skill_timer = st

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "friendly_fire_reflect_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("friendly_fire_reflect_timer", 5.0)
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["friendly_fire_reflect_timer"] = 5.0
                elif typeof(self.ball) == TYPE_OBJECT:
                    self.ball.friendly_fire_reflect_timer = 5.0

                var w_arena35 = self.world.get("arena") if typeof(self.world) == TYPE_DICTIONARY else (self.world.arena if "arena" in self.world else null)
                if w_arena35 != null:
                    var w_hazards35 = w_arena35.get("hazards") if typeof(w_arena35) == TYPE_DICTIONARY else (w_arena35.hazards if "hazards" in w_arena35 else null)
                    if w_hazards35 != null:
                        var idx35 = w_hazards35.find(nearest)
                        if idx35 != -1: w_hazards35.remove_at(idx35)
            elif "kind" in nearest and nearest.kind == "pinball_booster":
                if typeof(ball) == TYPE_DICTIONARY:
                    ball["pinball_booster_timer"] = 10.0
                    ball["is_frictionless"] = true
                    ball["skill_silenced"] = true
                    ball["knockback_multiplier_outgoing"] = 2.0
                elif typeof(ball) == TYPE_OBJECT:
                    if "pinball_booster_timer" in ball: ball.pinball_booster_timer = 10.0
                    elif ball.has_method("set_meta"): ball.set_meta("pinball_booster_timer", 10.0)
                    if "is_frictionless" in ball: ball.is_frictionless = true
                    elif ball.has_method("set_meta"): ball.set_meta("is_frictionless", true)
                    if "skill_silenced" in ball: ball.skill_silenced = true
                    elif ball.has_method("set_meta"): ball.set_meta("skill_silenced", true)
                    if "knockback_multiplier_outgoing" in ball: ball.knockback_multiplier_outgoing = 2.0
                    elif ball.has_method("set_meta"): ball.set_meta("knockback_multiplier_outgoing", 2.0)

                if typeof(world) == TYPE_OBJECT and "arena" in world and typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "pinball_projectile_booster":
                ball.pinball_projectile_timer = 5.0
                if typeof(world) == TYPE_OBJECT and "arena" in world and typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
                if typeof(world) == TYPE_OBJECT and "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1:
                        world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "skill_reroll_booster":
                var skills = ['ice_trail', 'arena_shout', 'trigger_flipper', 'bite', 'black_hole_summon', 'bump', 'chain_bounce_attack', 'chaos_link', 'chi_blast', 'clone', 'teammate_clone', 'command', 'corpse_explosion', 'devour', 'dash', 'deploy_turret', 'deploy_clan_banner', 'turret_overload', 'elemental_burst', 'energy_shield', 'entangle', 'explosion', 'fireball', 'flare', 'global_mirage', 'ground_pound', 'health_link', 'holy_shield', 'life_drain', 'lightning_strike', 'mass_illusion', 'master_decoys', 'mirage_swarm', 'mimic_clone', 'multishot', 'observe', 'perfect_strike', 'phantom_stride', 'phase_through', 'spectral_burn', 'place_fake_booster', 'place_dummy_item', 'place_fake_flare', 'place_fake_healing_orb', 'poison_nova', 'protect_ally', 'rage_burst', 'sandstorm_cloak', 'smite', 'snipe', 'sonar_ping', 'stamina_dash', 'phantom_stride', 'summon_minions', 'target_strong', 'throw_hazard', 'throw_bomb', 'throw_vortex_grenade', 'throw_aura_nullifier_grenade', 'throw_decoy', 'throw_disruptor_bomb', 'throw_position_swap_grenade', 'time_rewind', 'time_rewind_self', 'tactical_rewind', 'survival_rewind', 'echo_rewind', 'tracking_beacon', 'trickster_swap', 'orbiting_beefy_decoy', 'trickster_clone', 'trickster_dash', 'reversed_trickster_clone', 'trickster_smoke_bomb', 'wall_jump', 'wave_attack', 'wind_rider', 'yeti_roar', 'impostor_disguise', 'orbital_mines', 'decoy_swap_survival', 'decoy_swap_detonate', 'throw_emp', 'throw_purge_bomb', 'kinetic_echo', 'kinetic_absorber', 'throw_noise_maker', 'deploy_lightning_rod', 'deploy_chain_lightning_relay', 'deploy_electric_beam_trap', 'bounty_trap', 'deploy_teleport_relay', 'deploy_time_anomaly_field', 'deploy_cluster_mines', 'deploy_sunlight_reflector', 'deploy_glass_shield', 'deploy_stabilizer_field', 'deploy_tracker_drone', 'deploy_distract_drone', 'deploy_fake_balls', 'decoy_swarm', 'hire_mercenary', 'hazard_surfing', 'grapple_hook', 'elastic_tether', 'instant_swap']
                var new_skill = skills[randi() % skills.size()]
                ball.skill = new_skill
                ball.SKILL = new_skill
                ball.skill_timer = 0.0
                if typeof(world) == TYPE_OBJECT and "arena" in world and typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
                if typeof(world) == TYPE_OBJECT and "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1:
                        world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "rearm_token":
                if "skill_timer" in self.ball:
                    self.ball.skill_timer = 0.0
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("skill_timer", 0.0)

                if "rearm_damage_boost" in self.ball:
                    self.ball.rearm_damage_boost = true
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("rearm_damage_boost", true)
                elif self.ball is Dictionary:
                    self.ball["rearm_damage_boost"] = true

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "stealth_drone_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("has_stealth_drone", true)
                    self.ball.set_meta("stealth_drone_timer", 15.0)
                elif "has_stealth_drone" in self.ball:
                    self.ball.has_stealth_drone = true
                    self.ball.stealth_drone_timer = 15.0
                elif "stealth_drone_timer" in self.ball:
                    self.ball.stealth_drone_timer = 15.0
            elif "kind" in nearest and nearest.kind == "artillery_pet_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("has_pet", true)
                    self.ball.set_meta("pet_type", "artillery")
                    self.ball.set_meta("pet_cooldown", 0.0)
                else:
                    self.ball["has_pet"] = true
                    self.ball["pet_type"] = "artillery"
                    self.ball["pet_cooldown"] = 0.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                    else:
                        if "items" in self.world.arena:
                            idx = self.world.arena.items.find(nearest)
                            if idx != -1:
                                self.world.arena.items.remove_at(idx)
                    var pet_exists = false
                    var b_id = null
                    if "id" in self.ball: b_id = self.ball.id
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get") and self.ball.get("id") != null: b_id = self.ball.get("id")
                    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): b_id = self.ball["id"]

                    for h in self.world.arena.hazards:
                        var hk = h.get("kind", h.kind if "kind" in h else "")
                        var ho = h.get("owner_id", h.owner_id if "owner_id" in h else null)
                        if hk == "pet" and ho == b_id:
                            pet_exists = true
                            break
                    if not pet_exists:
                        var new_pet = {"id": 999000 + self.world.arena.hazards.size() + randi() % 10000, "x": self.ball.x, "y": self.ball.y, "radius": 8.0, "kind": "pet", "damage": 0.0, "owner_id": b_id}
                        self.world.arena.hazards.append(new_pet)
            elif "kind" in nearest and nearest.kind == "pet_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("has_pet", true)
                    self.ball.set_meta("pet_type", "auto_looter")
                else:
                    self.ball["has_pet"] = true
                    self.ball["pet_type"] = "auto_looter"
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                    var rng = RandomNumberGenerator.new()
                    rng.randomize()
                    var b_id = null
                    if "id" in self.ball: b_id = self.ball.id
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get") and self.ball.get("id") != null: b_id = self.ball.get("id")
                    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): b_id = self.ball["id"]

                    var p = {}
                    p["id"] = 999000 + self.world.arena.hazards.size() + rng.randi() % 10000
                    p["x"] = self.ball.x
                    p["y"] = self.ball.y
                    p["radius"] = 8.0
                    p["kind"] = "pet"
                    p["damage"] = 0.0
                    p["owner_id"] = b_id
                    self.world.arena.hazards.append(p)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "disruptor_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("disruptor_aura_timer", 5.0)
                else:
                    self.ball["disruptor_aura_timer"] = 5.0
                if "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
                if "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1:
                        world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "aura_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("aura_booster_timer", 15.0)
                elif "aura_booster_timer" in self.ball:
                    self.ball.aura_booster_timer = 15.0
                else:
                    self.ball["aura_booster_timer"] = 15.0

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
                if "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1:
                        world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "vision_reduction_trap":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("vision_reduction_timer", 5.0)
                elif "vision_reduction_timer" in self.ball:
                    self.ball.vision_reduction_timer = 5.0
                else:
                    self.ball.vision_reduction_timer = 5.0

                var vr_applied = false
                if "vision_reduction_applied" in self.ball:
                    vr_applied = self.ball.vision_reduction_applied
                elif self.ball.has_method("get_meta") and self.ball.has_meta("vision_reduction_applied"):
                    vr_applied = self.ball.get_meta("vision_reduction_applied")

                if not vr_applied:
                    var has_base = false
                    if "base_perception_radius" in self.ball:
                        has_base = true
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("base_perception_radius"):
                        has_base = true

                    if not has_base:
                        var p_rad = 250.0
                        if "perception_radius" in self.ball:
                            p_rad = float(self.ball.perception_radius)
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("perception_radius"):
                            p_rad = self.ball.get_meta("perception_radius")

                        if "base_perception_radius" in self.ball:
                            self.ball.base_perception_radius = p_rad
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("base_perception_radius", p_rad)
                        else:
                            self.ball.base_perception_radius = p_rad

                    var b_rad = 250.0
                    if "base_perception_radius" in self.ball:
                        b_rad = float(self.ball.base_perception_radius)
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("base_perception_radius"):
                        b_rad = self.ball.get_meta("base_perception_radius")

                    if "perception_radius" in self.ball:
                        self.ball.perception_radius = b_rad * 0.2
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("perception_radius", b_rad * 0.2)

                    if "vision_reduction_applied" in self.ball:
                        self.ball.vision_reduction_applied = true
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("vision_reduction_applied", true)
                    else:
                        self.ball.vision_reduction_applied = true
                if "arena" in self.world and self.world.arena != null:
                    if "hazards" in self.world.arena and self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "vision_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("vision_booster_timer", 15.0)
                elif "vision_booster_timer" in self.ball:
                    self.ball.vision_booster_timer = 15.0
                else:
                    self.ball.vision_booster_timer = 15.0

                var vb_applied = false
                if "vision_booster_applied" in self.ball:
                    vb_applied = self.ball.vision_booster_applied
                elif self.ball.has_method("get_meta") and self.ball.has_meta("vision_booster_applied"):
                    vb_applied = self.ball.get_meta("vision_booster_applied")

                if not vb_applied:
                    var base_perc = 250.0
                    if "perception_radius" in self.ball:
                        base_perc = float(self.ball.perception_radius)
                    if self.ball.has_method("get_meta") and self.ball.has_meta("base_perception_radius"):
                        base_perc = self.ball.get_meta("base_perception_radius")

                    base_perc *= 2.0

                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("base_perception_radius", base_perc)
                        self.ball.set_meta("vision_booster_applied", true)

                    self.ball.perception_radius = base_perc

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
        elif kind == "permanent_aura_booster":
            if typeof(world) == TYPE_DICTIONARY and not world.has("permanent_aura_buffs"):
                world["permanent_aura_buffs"] = {}
            elif typeof(world) == TYPE_OBJECT and not "permanent_aura_buffs" in world:
                world.permanent_aura_buffs = {}

            var p_team = ""
            if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("team"):
                p_team = self.ball["team"]
            elif typeof(self.ball) == TYPE_OBJECT and "team" in self.ball:
                p_team = self.ball.team
            elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("ball_type"):
                p_team = self.ball["ball_type"]
            elif typeof(self.ball) == TYPE_OBJECT and "ball_type" in self.ball:
                p_team = self.ball.ball_type

            if typeof(world) == TYPE_DICTIONARY:
                if not world["permanent_aura_buffs"].has(p_team):
                    world["permanent_aura_buffs"][p_team] = 0
                world["permanent_aura_buffs"][p_team] += 1
            elif typeof(world) == TYPE_OBJECT:
                if typeof(world.permanent_aura_buffs) == TYPE_DICTIONARY:
                    if not world.permanent_aura_buffs.has(p_team):
                        world.permanent_aura_buffs[p_team] = 0
                    world.permanent_aura_buffs[p_team] += 1

            if world != null and typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
                var idx = world.arena.hazards.find(nearest)
                if idx != -1:
                    world.arena.hazards.remove_at(idx)
            elif world != null and typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null and typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
                var idx = world.arena.hazards.find(nearest)
                if idx != -1:
                    world.arena.hazards.remove_at(idx)
            elif world != null and typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null and typeof(world.arena) == TYPE_OBJECT and "hazards" in world.arena:
                var idx = world.arena.hazards.find(nearest)
                if idx != -1:
                    world.arena.hazards.remove_at(idx)

            if world != null and typeof(world) == TYPE_DICTIONARY and world.has("boosters"):
                var idx = world.boosters.find(nearest)
                if idx != -1:
                    world.boosters.remove_at(idx)
            elif world != null and typeof(world) == TYPE_OBJECT and "boosters" in world:
                var idx = world.boosters.find(nearest)
                if idx != -1:
                    world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "invert_booster":
                if self.world != null and "balls" in self.world:
                    for other in self.world.balls:
                        var my_team = -2
                        if "team" in self.ball: my_team = self.ball.team
                        var other_team = -1
                        if "team" in other: other_team = other.team
                        if other_team != my_team and other.get("hp", 0) > 0:
                            if "invert_timer" in other:
                                other.invert_timer = 5.0
                            elif other.has_method("set_meta"):
                                other.set_meta("invert_timer", 5.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "blink_relic":
                if "blink_relic_timer" in self.ball: self.ball.blink_relic_timer = 15.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("blink_relic_timer", 15.0)

                if "blink_relic_cooldown" in self.ball: self.ball.blink_relic_cooldown = 3.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("blink_relic_cooldown", 3.0)

                var blink_applied = false
                if "blink_relic_applied" in self.ball: blink_applied = self.ball.blink_relic_applied
                elif self.ball.has_method("has_meta") and self.ball.has_meta("blink_relic_applied"): blink_applied = self.ball.get_meta("blink_relic_applied")

                if not blink_applied:
                    var base_mhp = 100.0
                    if "max_hp" in self.ball: base_mhp = self.ball.max_hp

                    if "base_max_hp_blink_relic" in self.ball: self.ball.base_max_hp_blink_relic = base_mhp
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("base_max_hp_blink_relic", base_mhp)

                    var new_mhp = base_mhp * 0.7
                    if "max_hp" in self.ball: self.ball.max_hp = new_mhp

                    var cur_hp = 100.0
                    if "hp" in self.ball: cur_hp = self.ball.hp

                    if cur_hp > new_mhp:
                        if "hp" in self.ball: self.ball.hp = new_mhp
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("hp", new_mhp)

                    if "blink_relic_applied" in self.ball: self.ball.blink_relic_applied = true
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("blink_relic_applied", true)

                if typeof(nearest) == TYPE_DICTIONARY: nearest["active"] = false
                else: nearest.active = false

                if typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove(idx)
            elif "kind" in nearest and nearest.kind == "cursed_relic":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("cursed_relic_timer", 10.0)
                    self.ball.set_meta("invert_timer", 10.0)
                if "cursed_relic_timer" in self.ball:
                    self.ball.cursed_relic_timer = 10.0
                if "invert_timer" in self.ball:
                    self.ball.invert_timer = 10.0

                var cr_applied = false
                if "cursed_relic_applied" in self.ball: cr_applied = self.ball.cursed_relic_applied
                elif self.ball.has_method("has_meta") and self.ball.has_meta("cursed_relic_applied"): cr_applied = self.ball.get_meta("cursed_relic_applied")

                if not cr_applied:
                    if not "base_perception_radius_relic" in self.ball and not (self.ball.has_method("has_meta") and self.ball.has_meta("base_perception_radius_relic")):
                        var pr = 250.0
                        if "perception_radius" in self.ball: pr = self.ball.perception_radius
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("perception_radius"): pr = self.ball.get_meta("perception_radius")
                        if self.ball.has_method("set_meta"): self.ball.set_meta("base_perception_radius_relic", pr)
                        if "base_perception_radius_relic" in self.ball: self.ball.base_perception_radius_relic = pr

                    if "base_perception_radius_relic" in self.ball:
                        self.ball.perception_radius = self.ball.base_perception_radius_relic * 0.1
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("base_perception_radius_relic"):
                        var new_pr = self.ball.get_meta("base_perception_radius_relic") * 0.1
                        self.ball.set_meta("perception_radius", new_pr)

                    if not "base_speed_relic" in self.ball and not (self.ball.has_method("has_meta") and self.ball.has_meta("base_speed_relic")):
                        var sp = 2.0
                        if "speed" in self.ball: sp = self.ball.speed
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("speed"): sp = self.ball.get_meta("speed")
                        if self.ball.has_method("set_meta"): self.ball.set_meta("base_speed_relic", sp)
                        if "base_speed_relic" in self.ball: self.ball.base_speed_relic = sp

                    if "base_speed_relic" in self.ball:
                        self.ball.speed = self.ball.base_speed_relic * 3.0
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("base_speed_relic"):
                        self.ball.set_meta("speed", self.ball.get_meta("base_speed_relic") * 3.0)

                    if not "base_damage_relic" in self.ball and not (self.ball.has_method("has_meta") and self.ball.has_meta("base_damage_relic")):
                        var dm = 10.0
                        if "damage" in self.ball: dm = self.ball.damage
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("damage"): dm = self.ball.get_meta("damage")
                        if self.ball.has_method("set_meta"): self.ball.set_meta("base_damage_relic", dm)
                        if "base_damage_relic" in self.ball: self.ball.base_damage_relic = dm

                    if "base_damage_relic" in self.ball:
                        self.ball.damage = self.ball.base_damage_relic * 3.0
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("base_damage_relic"):
                        self.ball.set_meta("damage", self.ball.get_meta("base_damage_relic") * 3.0)

                    if self.ball.has_method("set_meta"): self.ball.set_meta("cursed_relic_applied", true)
                    if "cursed_relic_applied" in self.ball: self.ball.cursed_relic_applied = true

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif (typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "geyser_boots") or (typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "geyser_boots"):
                var inv = []
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("inventory"):
                    inv = self.ball.inventory
                elif typeof(self.ball) == TYPE_OBJECT and "inventory" in self.ball:
                    inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"):
                    inv = self.ball.get_meta("inventory")
                if not inv.has("geyser_boots"):
                    inv.append("geyser_boots")
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["inventory"] = inv
                elif typeof(self.ball) == TYPE_OBJECT and "inventory" in self.ball:
                    self.ball.inventory = inv
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("inventory", inv)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "cursed_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("slow_timer", 5.0)
                    self.ball.set_meta("poison_timer", 5.0)
                    self.ball.set_meta("confusion_timer", 5.0)
                if "slow_timer" in self.ball:
                    self.ball.slow_timer = 5.0
                    self.ball.poison_timer = 5.0
                    self.ball.confusion_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "exploding_booster":
                if "hp" in self.ball:
                    self.ball.hp -= 30.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "quantum_teleporter_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("quantum_teleporter_booster_timer", 10.0)
                if "quantum_teleporter_booster_timer" in self.ball:
                    self.ball.quantum_teleporter_booster_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "debuff_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("slow_timer", 5.0)
                if "slow_timer" in self.ball:
                    self.ball.slow_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "storm_link_booster":
                var enemies = self._get_enemies_internal()
                if enemies.size() > 0:
                    var min_d = 999999999.0
                    var closest_enemy = null
                    var bx = self.ball.get_meta("x") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("x") else self.ball.x if "x" in self.ball else 0.0
                    var by = self.ball.get_meta("y") if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("has_meta") and self.ball.has_meta("y") else self.ball.y if "y" in self.ball else 0.0
                    for e in enemies:
                        var ex = e.get_meta("x") if typeof(e) != TYPE_DICTIONARY and e.has_method("has_meta") and e.has_meta("x") else e.x if "x" in e else 0.0
                        var ey = e.get_meta("y") if typeof(e) != TYPE_DICTIONARY and e.has_method("has_meta") and e.has_meta("y") else e.y if "y" in e else 0.0
                        var d = (ex - bx)*(ex - bx) + (ey - by)*(ey - by)
                        if d < min_d:
                            min_d = d
                            closest_enemy = e
                    if closest_enemy != null:
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("storm_link_timer", 5.0)
                            self.ball.set_meta("storm_link_target", closest_enemy)
                        else:
                            self.ball.storm_link_timer = 5.0
                            self.ball.storm_link_target = closest_enemy
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "orbital_link_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("orbital_link_timer", 10.0)
                else:
                    self.ball.orbital_link_timer = 10.0
                if self.world != null and "events" in self.world:
                    var bx = self.ball.get("x") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("x") if self.ball.has_method("has_meta") and self.ball.has_meta("x") else (self.ball.x if "x" in self.ball else 0.0))
                    var by = self.ball.get("y") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("y") if self.ball.has_method("has_meta") and self.ball.has_meta("y") else (self.ball.y if "y" in self.ball else 0.0))
                    self.world.events.append({"type": "orbital_link", "x": bx, "y": by})
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "anchor_point_booster":
                var bx = self.ball.get("x") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("x") if self.ball.has_method("has_meta") and self.ball.has_meta("x") else (self.ball.x if "x" in self.ball else 0.0))
                var by = self.ball.get("y") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("y") if self.ball.has_method("has_meta") and self.ball.has_meta("y") else (self.ball.y if "y" in self.ball else 0.0))
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["anchor_point_timer"] = 10.0
                    self.ball["anchor_point_x"] = bx
                    self.ball["anchor_point_y"] = by
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("anchor_point_timer", 10.0)
                    self.ball.set_meta("anchor_point_x", bx)
                    self.ball.set_meta("anchor_point_y", by)
                else:
                    self.ball.anchor_point_timer = 10.0
                    self.ball.anchor_point_x = bx
                    self.ball.anchor_point_y = by

                if self.world != null and "events" in self.world:
                    self.world.events.append({"type": "anchor_point", "x": bx, "y": by})
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "tether_booster":
                var enemies = _get_enemies()
                var allies = _get_allies_internal()

                var closest_enemy = null
                var min_enemy_dist = 999999999.0
                for e in enemies:
                    var alive = true
                    if typeof(e) == TYPE_OBJECT:
                        if "alive" in e: alive = e.alive
                    elif typeof(e) == TYPE_DICTIONARY:
                        if e.has("alive"): alive = e.alive
                    if alive and e != self.ball:
                        var dx = e.x - self.ball.x
                        var dy = e.y - self.ball.y
                        var d = dx*dx + dy*dy
                        if d < min_enemy_dist:
                            min_enemy_dist = d
                            closest_enemy = e

                var closest_ally = null
                var min_ally_dist = 999999999.0
                for a in allies:
                    var alive = true
                    if typeof(a) == TYPE_OBJECT:
                        if "alive" in a: alive = a.alive
                    elif typeof(a) == TYPE_DICTIONARY:
                        if a.has("alive"): alive = a.alive
                    if alive and a != self.ball:
                        var dx = a.x - self.ball.x
                        var dy = a.y - self.ball.y
                        var d = dx*dx + dy*dy
                        if d < min_ally_dist:
                            min_ally_dist = d
                            closest_ally = a

                if closest_enemy != null and closest_ally != null:
                    if typeof(closest_enemy) == TYPE_OBJECT:
                        if "forced_tether_target" in closest_enemy: closest_enemy.forced_tether_target = closest_ally
                        elif closest_enemy.has_method("set_meta"): closest_enemy.set_meta("forced_tether_target", closest_ally)
                        if "forced_tether_timer" in closest_enemy: closest_enemy.forced_tether_timer = 10.0
                        elif closest_enemy.has_method("set_meta"): closest_enemy.set_meta("forced_tether_timer", 10.0)
                    elif typeof(closest_enemy) == TYPE_DICTIONARY:
                        closest_enemy.forced_tether_target = closest_ally
                        closest_enemy.forced_tether_timer = 10.0
                elif closest_enemy != null:
                    if typeof(closest_enemy) == TYPE_OBJECT:
                        if "forced_tether_target" in closest_enemy: closest_enemy.forced_tether_target = self.ball
                        elif closest_enemy.has_method("set_meta"): closest_enemy.set_meta("forced_tether_target", self.ball)
                        if "forced_tether_timer" in closest_enemy: closest_enemy.forced_tether_timer = 10.0
                        elif closest_enemy.has_method("set_meta"): closest_enemy.set_meta("forced_tether_timer", 10.0)
                    elif typeof(closest_enemy) == TYPE_DICTIONARY:
                        closest_enemy.forced_tether_target = self.ball
                        closest_enemy.forced_tether_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "blink_booster":
                var stamina_val = 0.0
                if "stamina" in self.ball: stamina_val = self.ball.stamina
                elif self.ball.has_method("has_meta") and self.ball.has_meta("stamina"): stamina_val = self.ball.get_meta("stamina")

                var new_stamina = max(0.0, stamina_val - 50.0)
                if "stamina" in self.ball: self.ball.stamina = new_stamina
                elif self.ball.has_method("set_meta"): self.ball.set_meta("stamina", new_stamina)

                var vx_val = 0.0
                var vy_val = 0.0
                if "vx" in self.ball: vx_val = self.ball.vx
                if "vy" in self.ball: vy_val = self.ball.vy

                var speed = sqrt(vx_val*vx_val + vy_val*vy_val)
                var nx = 1.0
                var ny = 0.0
                if speed > 0.1:
                    nx = vx_val / speed
                    ny = vy_val / speed

                self.ball.x += nx * 200.0
                self.ball.y += ny * 200.0

                if typeof(nearest) == TYPE_DICTIONARY:
                    nearest.active = false
                elif typeof(nearest) == TYPE_OBJECT and "active" in nearest:
                    nearest.active = false

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "teleport_booster":
                var old_x = self.ball.x
                if "pre_teleport_x" in self.ball: old_x = self.ball.pre_teleport_x
                elif self.ball.has_method("has_meta") and self.ball.has_meta("pre_teleport_x"): old_x = self.ball.get_meta("pre_teleport_x")

                var old_y = self.ball.y
                if "pre_teleport_y" in self.ball: old_y = self.ball.pre_teleport_y
                elif self.ball.has_method("has_meta") and self.ball.has_meta("pre_teleport_y"): old_y = self.ball.get_meta("pre_teleport_y")

                if self.world != null and "arena" in self.world and "safe_zone_center" in self.world.arena:
                    var cx = self.world.arena.safe_zone_center[0] if typeof(self.world.arena.safe_zone_center) == TYPE_ARRAY else self.world.arena.safe_zone_center.x
                    var cy = self.world.arena.safe_zone_center[1] if typeof(self.world.arena.safe_zone_center) == TYPE_ARRAY else self.world.arena.safe_zone_center.y

                    var radius = 500.0
                    if "safe_zone_radius" in self.world.arena:
                        radius = self.world.arena.safe_zone_radius

                    var angle = randf() * 2 * PI
                    var r = randf() * max(0.0, radius - 50.0)
                    var target_x = cx + cos(angle) * r
                    var target_y = cy + sin(angle) * r

                    var arena_width = 1000.0
                    if "width" in self.world.arena: arena_width = self.world.arena.width
                    var arena_height = 1000.0
                    if "height" in self.world.arena: arena_height = self.world.arena.height

                    self.ball.x = clamp(target_x, 10.0, arena_width - 10.0)
                    self.ball.y = clamp(target_y, 10.0, arena_height - 10.0)

                var current_imm = 0.0
                if "immunity_timer" in self.ball: current_imm = self.ball.immunity_timer
                elif self.ball.has_method("has_meta") and self.ball.has_meta("immunity_timer"): current_imm = self.ball.get_meta("immunity_timer")
                if current_imm < 3.0:
                    if "immunity_timer" in self.ball: self.ball.immunity_timer = 3.0
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("immunity_timer", 3.0)

                # Leave behind an explosive decoy
                if self.world != null and "balls" in self.world:
                    # GDScript object duplication might be tricky, let's create a minimal decoy if possible, or use duplicate
                    var decoy = null
                    if self.ball.has_method("duplicate"):
                        decoy = self.ball.duplicate()
                    elif self.ball.has_method("clone"):
                        decoy = self.ball.clone()

                    if decoy != null:
                        var new_id = randi() % 90000 + 10000
                        if "next_id" in self.world:
                            new_id = self.world.next_id
                            self.world.next_id += 1

                        if "id" in decoy: decoy.id = new_id
                        elif decoy.has_method("set_meta"): decoy.set_meta("id", new_id)

                        if "x" in decoy: decoy.x = old_x
                        elif decoy.has_method("set_meta"): decoy.set_meta("x", old_x)
                        if "y" in decoy: decoy.y = old_y
                        elif decoy.has_method("set_meta"): decoy.set_meta("y", old_y)

                        var mhp = 100
                        if "max_hp" in self.ball: mhp = self.ball.max_hp
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("max_hp"): mhp = self.ball.get_meta("max_hp")

                        if "hp" in decoy: decoy.hp = mhp
                        elif decoy.has_method("set_meta"): decoy.set_meta("hp", mhp)
                        if "max_hp" in decoy: decoy.max_hp = mhp
                        elif decoy.has_method("set_meta"): decoy.set_meta("max_hp", mhp)

                        if "damage" in decoy: decoy.damage = 0
                        elif decoy.has_method("set_meta"): decoy.set_meta("damage", 0)

                        var b_id = null
                        if "id" in self.ball: b_id = self.ball.id
                        elif self.ball.has_method("has_meta") and self.ball.has_meta("id"): b_id = self.ball.get_meta("id")

                        if "owner_id" in decoy: decoy.owner_id = b_id
                        elif decoy.has_method("set_meta"): decoy.set_meta("owner_id", b_id)

                        if "is_decoy" in decoy: decoy.is_decoy = true
                        elif decoy.has_method("set_meta"): decoy.set_meta("is_decoy", true)

                        if "decoy_type" in decoy: decoy.decoy_type = "explosive"
                        elif decoy.has_method("set_meta"): decoy.set_meta("decoy_type", "explosive")

                        if "decoy_timer" in decoy: decoy.decoy_timer = 5.0
                        elif decoy.has_method("set_meta"): decoy.set_meta("decoy_timer", 5.0)

                        self.world.balls.append(decoy)

                if self.world != null and "events" in self.world:
                    self.world.events.append({"type": "teleport", "data": {"x": self.ball.x, "y": self.ball.y}})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "cleanse_booster":
                if "immunity_timer" in self.ball: self.ball.immunity_timer = 15.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("immunity_timer", 15.0)
                if "burn_timer" in self.ball: self.ball.burn_timer = 0.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("burn_timer", 0.0)
                if "poison_timer" in self.ball: self.ball.poison_timer = 0.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("poison_timer", 0.0)
                if "slow_timer" in self.ball: self.ball.slow_timer = 0.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("slow_timer", 0.0)
                if "confusion_timer" in self.ball: self.ball.confusion_timer = 0.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("confusion_timer", 0.0)
                if "is_confused" in self.ball: self.ball.is_confused = false
                elif self.ball.has_method("set_meta"): self.ball.set_meta("is_confused", false)
                if "blindness_timer" in self.ball: self.ball.blindness_timer = 0.0
                elif self.ball.has_method("set_meta"): self.ball.set_meta("blindness_timer", 0.0)
                if "is_blinded" in self.ball: self.ball.is_blinded = false
                elif self.ball.has_method("set_meta"): self.ball.set_meta("is_blinded", false)

                var has_debuff = false
                if self.ball.has_method("has_meta") and self.ball.has_meta("zone_modifier_debuff"):
                    has_debuff = true
                if has_debuff:
                    if self.ball.has_method("has_meta") and self.ball.has_meta("base_max_hp"):
                        self.ball.max_hp = self.ball.get_meta("base_max_hp")
                    self.ball.remove_meta("zone_modifier_debuff")

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "material_magnet_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("material_magnet_timer", 10.0)
                else:
                    self.ball.material_magnet_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "insulator_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("insulator_timer", 15.0)
                elif "insulator_timer" in self.ball:
                    self.ball.insulator_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "insulator_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("insulator_timer", 15.0)
                elif "insulator_timer" in self.ball:
                    self.ball.insulator_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "hazard_immunity_booster":
                var curr_im = 0.0
                if typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("hazard_immunity_timer"):
                    curr_im = float(self.ball.hazard_immunity_timer)
                elif typeof(self.ball) == TYPE_OBJECT and "hazard_immunity_timer" in self.ball:
                    curr_im = float(self.ball.hazard_immunity_timer)
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("hazard_immunity_timer"):
                    curr_im = float(self.ball.get_meta("hazard_immunity_timer"))

                if "hazard_immunity_timer" in self.ball:
                    self.ball.hazard_immunity_timer = curr_im + 15.0
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("hazard_immunity_timer", curr_im + 15.0)
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["hazard_immunity_timer"] = curr_im + 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "phase_booster":
                if "phase_booster_timer" in self.ball:
                    self.ball.phase_booster_timer = 10.0
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("phase_booster_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "orbital_mine_immunity_booster":
                if "orbital_mine_immunity_timer" in self.ball:
                    self.ball.orbital_mine_immunity_timer = 15.0
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("orbital_mine_immunity_timer", 15.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "orbital_emp_strike_item":
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var ProceduralArenaModule = load("res://arena/procedural_arena.gd")
                    if ProceduralArenaModule != null:
                        var cx = 500.0
                        if "width" in self.world.arena:
                            cx = self.world.arena.width / 2.0
                        elif "width" in self.world:
                            cx = self.world.width / 2.0
                        var cy = 500.0
                        if "height" in self.world.arena:
                            cy = self.world.arena.height / 2.0
                        elif "height" in self.world:
                            cy = self.world.height / 2.0
                        var h_id = 5000 + self.world.arena.hazards.size() + (randi() % 10000)
                        var strike = ProceduralArenaModule.Hazard.new(h_id, cx, cy, 400.0, "emp_strike", 0.0)
                        strike.target_radius = 400.0
                        strike.set_meta("duration", 3.0)
                        self.world.arena.hazards.append(strike)
                if self.world != null and "events" in self.world:
                    self.world.events.append({"type": "orbital_emp_strike", "message": "An Orbital EMP Strike has been called down!"})
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "emp_immunity_booster":
                if "emp_immunity_timer" in self.ball:
                    self.ball.emp_immunity_timer = 15.0
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta("emp_immunity_timer", 15.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "emp_booster":
                var emp_radius = 800.0
                if self.world != null and "balls" in self.world:
                    for other in self.world.balls:
                        var o_alive = true
                        if "alive" in other: o_alive = other.alive
                        elif typeof(other) == TYPE_DICTIONARY and other.has("alive"): o_alive = other["alive"]

                        var o_id = null
                        if "id" in other: o_id = other.id
                        elif typeof(other) == TYPE_DICTIONARY and other.has("id"): o_id = other["id"]

                        var b_id = null
                        if "id" in self.ball: b_id = self.ball.id
                        elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): b_id = self.ball["id"]

                        if o_alive and o_id != b_id:
                            var b_team = ""
                            if "team" in self.ball: b_team = self.ball.team
                            elif "ball_type" in self.ball: b_team = self.ball.ball_type

                            var o_team = ""
                            if "team" in other: o_team = other.team
                            elif "ball_type" in other: o_team = other.ball_type

                            if o_team != b_team:
                                var o_x = 0.0
                                if "x" in other: o_x = other.x
                                elif typeof(other) == TYPE_DICTIONARY and other.has("x"): o_x = other["x"]

                                var o_y = 0.0
                                if "y" in other: o_y = other.y
                                elif typeof(other) == TYPE_DICTIONARY and other.has("y"): o_y = other["y"]

                                var dx = o_x - self.ball.x
                                var dy = o_y - self.ball.y
                                if (dx*dx + dy*dy) <= emp_radius * emp_radius:
                                    if typeof(other) == TYPE_OBJECT and other.has_method("set_meta"):
                                        other.set_meta("shield", 0.0)
                                        var current_skill = other.get_meta("skill_timer") if other.has_meta("skill_timer") else 0.0
                                        other.set_meta("skill_timer", max(current_skill, 10.0))
                                    elif typeof(other) == TYPE_DICTIONARY:
                                        other["shield"] = 0.0
                                        other["skill_timer"] = max(other.get("skill_timer", 0.0), 10.0)
                                    else:
                                        if "shield" in other: other.shield = 0.0
                                        if "skill_timer" in other: other.skill_timer = max(other.skill_timer, 10.0)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var hazards_arr = self.world.arena.hazards
                    for h in hazards_arr:
                        var h_kind = ""
                        if "kind" in h: h_kind = h.kind
                        elif typeof(h) == TYPE_DICTIONARY and h.has("kind"): h_kind = h["kind"]

                        if h_kind in ["laser_beam", "gravity_well", "spinning_laser", "laser_tripwire", "laser_wall", "bounce_laser", "orbital_accelerator"]:
                            var h_x = 0.0
                            if "x" in h: h_x = h.x
                            elif typeof(h) == TYPE_DICTIONARY and h.has("x"): h_x = h["x"]

                            var h_y = 0.0
                            if "y" in h: h_y = h.y
                            elif typeof(h) == TYPE_DICTIONARY and h.has("y"): h_y = h["y"]

                            var dx = h_x - self.ball.x
                            var dy = h_y - self.ball.y
                            if (dx*dx + dy*dy) <= emp_radius * emp_radius:
                                if typeof(h) == TYPE_OBJECT and h.has_method("set_meta"):
                                    h.set_meta("emp_disabled_timer", 10.0)
                                elif typeof(h) == TYPE_DICTIONARY:
                                    h["emp_disabled_timer"] = 10.0
                                else:
                                    if "emp_disabled_timer" in h:
                                        h.emp_disabled_timer = 10.0

                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "nemesis_booster":
                self.ball.set_meta("nemesis_booster_timer", 5.0)
                if "nemesis_booster_timer" in self.ball:
                    self.ball.nemesis_booster_timer = 5.0
                if "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
            elif "kind" in nearest and nearest.kind == "loadout_fragment":
                var current_fragments = 0
                if typeof(self.ball) == TYPE_DICTIONARY:
                    current_fragments = self.ball.get("collected_fragments", 0) + 1
                    self.ball["collected_fragments"] = current_fragments
                elif self.ball.has_method("get_meta"):
                    current_fragments = self.ball.get_meta("collected_fragments", 0) + 1
                    self.ball.set_meta("collected_fragments", current_fragments)
                elif "collected_fragments" in self.ball:
                    self.ball.collected_fragments += 1
                    current_fragments = self.ball.collected_fragments
                else:
                    self.ball.collected_fragments = 1
                    current_fragments = 1

                var unlocked = false
                if self.world != null and "profile_manager" in self.world and self.world.profile_manager != null and self.world.profile_manager.has_method("add_ancient_fragment"):
                    unlocked = self.world.profile_manager.add_ancient_fragment()
                elif current_fragments >= 3:
                    unlocked = true

                if unlocked:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["cosmetic"] = "ancient_aura"
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("cosmetic", "ancient_aura")
                    elif "cosmetic" in self.ball:
                        self.ball.cosmetic = "ancient_aura"

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif typeof(nearest) == TYPE_DICTIONARY and nearest.get("kind", "") == "mirror_buff" or (typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "mirror_buff"):
                var in_mirror = ball.in_mirror_dimension if "in_mirror_dimension" in ball else false
                if typeof(ball) == TYPE_OBJECT and ball.has_method("get_meta") and ball.has_meta("in_mirror_dimension"):
                    in_mirror = ball.get_meta("in_mirror_dimension")
                if in_mirror:
                    var current_damage = ball.damage if "damage" in ball else 10.0
                    var current_max_hp = ball.max_hp if "max_hp" in ball else 100.0
                    var current_hp = ball.hp if "hp" in ball else 100.0

                    if typeof(ball) == TYPE_OBJECT and ball.has_method("set"):
                        ball.set("damage", current_damage * 1.1)
                        ball.set("max_hp", current_max_hp * 1.1)
                        ball.set("hp", min(current_hp + 10.0, current_max_hp * 1.1))
                    else:
                        ball.damage = current_damage * 1.1
                        ball.max_hp = current_max_hp * 1.1
                        ball.hp = min(current_hp + 10.0, current_max_hp * 1.1)

                    if typeof(nearest) == TYPE_OBJECT and nearest.has_method("set"):
                        nearest.set("duration", 0.0)
                    elif typeof(nearest) == TYPE_DICTIONARY:
                        nearest["duration"] = 0.0

                    if world and typeof(world) == TYPE_OBJECT and "arena" in world and "hazards" in world.arena and nearest in world.arena.hazards:
                        world.arena.hazards.erase(nearest)
                    elif world and typeof(world) == TYPE_OBJECT and "arena" in world and "boosters" in world.arena and nearest in world.arena.boosters:
                        world.arena.boosters.erase(nearest)
                    elif world and typeof(world) == TYPE_OBJECT and "boosters" in world and nearest in world.boosters:
                        world.boosters.erase(nearest)

                    if world and typeof(world) == TYPE_OBJECT and world.has_method("add_event"):
                        var b_x = ball.x if "x" in ball else 0.0
                        var b_y = ball.y if "y" in ball else 0.0
                        world.add_event("buff_collected", {"x": b_x, "y": b_y})
            elif "kind" in nearest and nearest.kind == "lightning_rod_item":
                if "has_lightning_rod" in self.ball: self.ball.has_lightning_rod = true
                elif self.ball.has_method("set_meta"): self.ball.set_meta("has_lightning_rod", true)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "nemesis_compass_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("nemesis_compass_item")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "holographic_decoy_module":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("holographic_decoy_timer", 15.0)
                    self.ball.set_meta("holographic_decoy_spawn_timer", 0.0)
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["holographic_decoy_timer"] = 15.0
                    self.ball["holographic_decoy_spawn_timer"] = 0.0
                if "boosters" in self.world:
                    var b_idx = self.world.boosters.find(nearest)
                    if b_idx != -1:
                        self.world.boosters.remove_at(b_idx)
            elif "kind" in nearest and nearest.kind == "hologram_booster":
                for i in range(1):
                    var clone = null
                    if self.ball.has_method("duplicate"):
                        clone = self.ball.duplicate()
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        clone = self.ball.duplicate()

                    if clone != null:
                        if "id" in clone:
                            clone.id = randi() % 90000 + 10000
                        if "hp" in clone and "max_hp" in clone:
                            clone.max_hp = 1.0
                            clone.hp = 1.0
                        if "damage" in clone: clone.damage = 0.0
                        if "base_damage" in clone: clone.base_damage = 0.0
                        if "speed" in clone and "speed" in self.ball: clone.speed = self.ball.speed

                        var bx = 0.0
                        var by = 0.0
                        if typeof(self.ball) == TYPE_DICTIONARY:
                            bx = self.ball.get("vx", 0.0)
                            by = self.ball.get("vy", 0.0)
                        elif "vx" in self.ball:
                            bx = self.ball.vx
                            by = self.ball.vy
                        var angle = 0.0
                        if bx == 0.0 and by == 0.0:
                            angle = randf() * 2.0 * PI
                        else:
                            angle = atan2(by, bx)
                        if "x" in clone and "y" in clone:
                            clone.x += cos(angle) * 15.0
                            clone.y += sin(angle) * 15.0

                        var self_id_stat = -2
                        if "id" in self.ball: self_id_stat = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id_stat = self.ball.get_meta("id")

                        if clone.has_method("set_meta"):
                            clone.set_meta("owner_id", self_id_stat)
                            clone.set_meta("is_hologram", true)
                            clone.set_meta("hologram_timer", 5.0)
                            clone.set_meta("hologram_dir_x", cos(angle))
                            clone.set_meta("hologram_dir_y", sin(angle))
                            clone.set_meta("skill_timer", 9999.0)
                            clone.set_meta("attack_timer", 9999.0)
                            clone.set_meta("SKILL", null)
                            clone.set_meta("skill", null)
                            clone.set_meta("active_skill", null)
                        elif typeof(clone) == TYPE_DICTIONARY:
                            clone["owner_id"] = self_id_stat
                            clone["is_hologram"] = true
                            clone["hologram_timer"] = 5.0
                            clone["hologram_dir_x"] = cos(angle)
                            clone["hologram_dir_y"] = sin(angle)
                            clone["skill_timer"] = 9999.0
                            clone["attack_timer"] = 9999.0
                            clone["SKILL"] = null
                            clone["skill"] = null
                            clone["active_skill"] = null

                        if self.world != null and "balls" in self.world:
                            self.world.balls.append(clone)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "nemesis_drone_booster":
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var d = {}
                    d["id"] = 999000 + self.world.arena.hazards.size()
                    d["x"] = self.ball.x
                    d["y"] = self.ball.y
                    d["radius"] = 8.0
                    d["kind"] = "nemesis_drone"
                    d["damage"] = 15.0
                    var b_id = null
                    if "id" in self.ball: b_id = self.ball.id
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get") and self.ball.get("id") != null: b_id = self.ball.get("id")
                    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("id"): b_id = self.ball["id"]
                    d["owner_id"] = b_id
                    d["duration"] = 30.0
                    self.world.arena.hazards.append(d)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "flashbang_booster":
                if self.world != null and "balls" in self.world:
                    for b in self.world.balls:
                        if b != self.ball:
                            var b_alive = b.alive if "alive" in b else (b.get_meta("alive") if typeof(b) == TYPE_OBJECT and b.has_meta("alive") else true)
                            var b_team = b.team if "team" in b else (b.get_meta("team") if typeof(b) == TYPE_OBJECT and b.has_meta("team") else "")
                            var my_team = self.ball.team if "team" in self.ball else (self.ball.get_meta("team") if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("team") else "")

                            var bx = b.x if "x" in b else (b.get_meta("x") if typeof(b) == TYPE_OBJECT and b.has_meta("x") else 0.0)
                            var by = b.y if "y" in b else (b.get_meta("y") if typeof(b) == TYPE_OBJECT and b.has_meta("y") else 0.0)
                            var dist = sqrt(pow(bx - self.ball.x, 2) + pow(by - self.ball.y, 2))

                            if b_alive and b_team != my_team and dist <= 500.0:
                                if typeof(b) == TYPE_OBJECT:
                                    if "is_blinded" in b: b.is_blinded = true
                                    elif b.has_method("set_meta"): b.set_meta("is_blinded", true)

                                    var current_blindness = b.blindness_timer if "blindness_timer" in b else (b.get_meta("blindness_timer") if b.has_method("has_meta") and b.has_meta("blindness_timer") else 0.0)
                                    if current_blindness < 5.0:
                                        if "blindness_timer" in b: b.blindness_timer = 5.0
                                        elif b.has_method("set_meta"): b.set_meta("blindness_timer", 5.0)

                                    if "is_stunned" in b: b.is_stunned = true
                                    elif b.has_method("set_meta"): b.set_meta("is_stunned", true)

                                    var current_stun = b.stun_timer if "stun_timer" in b else (b.get_meta("stun_timer") if b.has_method("has_meta") and b.has_meta("stun_timer") else 0.0)
                                    if current_stun < 3.0:
                                        if "stun_timer" in b: b.stun_timer = 3.0
                                        elif b.has_method("set_meta"): b.set_meta("stun_timer", 3.0)

                                    var has_base_pr = b.has_meta("base_perception_radius") if b.has_method("has_meta") else ("base_perception_radius" in b)
                                    if not has_base_pr:
                                        var pr = b.perception_radius if "perception_radius" in b else (b.get_meta("perception_radius") if b.has_method("has_meta") and b.has_meta("perception_radius") else 100.0)
                                        if "base_perception_radius" in b: b.base_perception_radius = pr
                                        elif b.has_method("set_meta"): b.set_meta("base_perception_radius", pr)

                                    if "perception_radius" in b: b.perception_radius = 0.0
                                    elif b.has_method("set_meta"): b.set_meta("perception_radius", 0.0)
                                elif typeof(b) == TYPE_DICTIONARY:
                                    b["is_blinded"] = true
                                    var current_blindness = b.get("blindness_timer", 0.0)
                                    if current_blindness < 5.0:
                                        b["blindness_timer"] = 5.0
                                    b["is_stunned"] = true
                                    var current_stun = b.get("stun_timer", 0.0)
                                    if current_stun < 3.0:
                                        b["stun_timer"] = 3.0
                                    if not b.has("base_perception_radius"):
                                        b["base_perception_radius"] = b.get("perception_radius", 100.0)
                                    b["perception_radius"] = 0.0

                if self.world != null and "events" in self.world:
                    var bx = self.ball.x if "x" in self.ball else (self.ball.get_meta("x") if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("x") else 0.0)
                    var by = self.ball.y if "y" in self.ball else (self.ball.get_meta("y") if typeof(self.ball) == TYPE_OBJECT and self.ball.has_meta("y") else 0.0)
                    self.world.events.append({"type": "visual_effect", "data": {"type": "flashbang_explosion", "x": bx, "y": by, "radius": 500.0}})
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "clone_booster":
                for i in range(2):
                    var clone = null
                    if self.ball.has_method("duplicate"):
                        clone = self.ball.duplicate()
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        clone = self.ball.duplicate()

                    if clone != null:
                        if "id" in clone:
                            clone.id = randi() % 90000 + 10000
                        if "hp" in clone and "max_hp" in clone:
                            clone.max_hp = 1.0
                            clone.hp = 1.0
                        if "damage" in clone:
                            clone.damage = 0.0
                        if "base_damage" in clone:
                            clone.base_damage = 0.0
                        if "speed" in clone and "speed" in self.ball:
                            clone.speed = self.ball.speed

                        if "x" in clone and "y" in clone:
                            var angle = i * PI + PI / 2.0
                            clone.x += cos(angle) * 15.0
                            clone.y += sin(angle) * 15.0

                        var self_id_stat = -2
                        if "id" in self.ball: self_id_stat = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id_stat = self.ball.get_meta("id")

                        if clone.has_method("set_meta"):
                            clone.set_meta("owner_id", self_id_stat)
                            clone.set_meta("is_decoy", true)
                            clone.set_meta("intangible", true)
                            clone.set_meta("is_mirroring", true)
                            clone.set_meta("decoy_timer", 5.0)
                            clone.set_meta("skill_timer", 9999.0)
                            clone.set_meta("attack_timer", 9999.0)
                            clone.set_meta("SKILL", null)
                            clone.set_meta("skill", null)
                            clone.set_meta("active_skill", null)
                        elif typeof(clone) == TYPE_DICTIONARY:
                            clone["owner_id"] = self_id_stat
                            clone["is_decoy"] = true
                            clone["intangible"] = true
                            clone["is_mirroring"] = true
                            clone["decoy_timer"] = 5.0
                            clone["skill_timer"] = 9999.0
                            clone["attack_timer"] = 9999.0
                            clone["SKILL"] = null
                            clone["skill"] = null
                            clone["active_skill"] = null

                        if self.world != null and "balls" in self.world:
                            self.world.balls.append(clone)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "shadow_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("shadow_booster_timer", 15.0)
                elif "shadow_booster_timer" in self.ball:
                    self.ball.shadow_booster_timer = 15.0
                else:
                    self.ball.shadow_booster_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "invisibility_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("invisibility_timer", 10.0)
                elif "invisibility_timer" in self.ball:
                    self.ball.invisibility_timer = 10.0
                else:
                    self.ball.invisibility_timer = 10.0

                if "arena" in self.world and "hazards" in self.world.arena:
                    if nearest in self.world.arena.hazards:
                        self.world.arena.hazards.erase(nearest)
                if "boosters" in self.world:
                    if nearest in self.world.boosters:
                        self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "bounty_extension_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("bounty_extension_active", true)
                elif "bounty_extension_active" in self.ball:
                    self.ball.bounty_extension_active = true
                else:
                    self.ball.bounty_extension_active = true
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "bounty_extension_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("bounty_extension_active", true)
                elif "bounty_extension_active" in self.ball:
                    self.ball.bounty_extension_active = true
                else:
                    self.ball.bounty_extension_active = true
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "bounty_extension_item":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("bounty_extension_active", true)
                elif "bounty_extension_active" in self.ball:
                    self.ball.bounty_extension_active = true
                else:
                    self.ball.bounty_extension_active = true
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "stealth_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("stealth_booster_timer", 10.0)
                elif "stealth_booster_timer" in self.ball:
                    self.ball.stealth_booster_timer = 10.0
                else:
                    self.ball.stealth_booster_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "deployable_decoy_swap_item":
                var inv = []
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if self.ball.has("inventory"): inv = self.ball.inventory
                    else: self.ball.inventory = inv
                    inv.append("deployable_decoy_swap_item")
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "inventory" in self.ball: inv = self.ball.inventory
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                    else:
                        if "inventory" in self.ball: self.ball.inventory = inv
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                    inv.append("deployable_decoy_swap_item")
                    if "inventory" in self.ball: self.ball.inventory = inv
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "decoy_flare_item":
                var inv = []
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if self.ball.has("inventory"): inv = self.ball.inventory
                    else: self.ball.inventory = inv
                    inv.append("deployable_flare")
                elif typeof(self.ball) == TYPE_OBJECT:
                    if "inventory" in self.ball: inv = self.ball.inventory
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                    else:
                        if "inventory" in self.ball: self.ball.inventory = inv
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                    inv.append("deployable_flare")
                    if "inventory" in self.ball: self.ball.inventory = inv
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "silence_booster":
                if self.world != null and "balls" in self.world:
                    for other_ball in self.world.balls:
                        var same_team = false
                        if "team" in other_ball and "team" in self.ball and other_ball.team == self.ball.team:
                            same_team = true
                        if not same_team:
                            var dist_silence = sqrt(pow(other_ball.x - self.ball.x, 2) + pow(other_ball.y - self.ball.y, 2))
                            if dist_silence < 150.0:
                                var duration = 5.0
                                if "duration" in nearest: duration = nearest.duration
                                if other_ball.has_method("set_meta"):
                                    other_ball.set_meta("silence_timer", duration)
                                elif "silence_timer" in other_ball:
                                    other_ball.silence_timer = duration
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "freeze_booster":
                var fduration = 3.0
                if "duration" in nearest: fduration = nearest.duration
                if self.world != null and "balls" in self.world:
                    for other_ball in self.world.balls:
                        var same_team = false
                        if "team" in other_ball and "team" in self.ball and other_ball.team == self.ball.team:
                            same_team = true
                        var alive = true
                        if "alive" in other_ball: alive = other_ball.alive
                        if not same_team and alive:
                            var current_stun = 0.0
                            if "stun_timer" in other_ball: current_stun = other_ball.stun_timer
                            elif other_ball.has_method("get_meta") and other_ball.has_meta("stun_timer"): current_stun = other_ball.get_meta("stun_timer")
                            var new_stun = max(current_stun, fduration)
                            if "stun_timer" in other_ball: other_ball.stun_timer = new_stun
                            elif other_ball.has_method("set_meta"): other_ball.set_meta("stun_timer", new_stun)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    for h in self.world.arena.hazards:
			var is_disabled_sf = false
			if typeof(h) == TYPE_DICTIONARY:
				is_disabled_sf = h.get("is_disabled_by_flare", false)
			elif typeof(h) == TYPE_OBJECT:
				if h.has_method("get_meta") and h.has_meta("is_disabled_by_flare"):
					is_disabled_sf = h.get_meta("is_disabled_by_flare")
				elif "is_disabled_by_flare" in h:
					is_disabled_sf = h.is_disabled_by_flare
			if is_disabled_sf:
				continue
                        if h != nearest:
                            var current_frozen = 0.0
                            if "frozen_timer" in h: current_frozen = h.frozen_timer
                            elif h.has_method("get_meta") and h.has_meta("frozen_timer"): current_frozen = h.get_meta("frozen_timer")
                            var new_frozen = max(current_frozen, fduration)
                            if "frozen_timer" in h: h.frozen_timer = new_frozen
                            elif h.has_method("set_meta"): h.set_meta("frozen_timer", new_frozen)
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "emp_wave_item":
                if self.ball.has_meta("inventory"):
                    var inv = self.ball.get_meta("inventory")
                    inv.append("emp_wave_item")
                    self.ball.set_meta("inventory", inv)
                elif "inventory" in self.ball:
                    self.ball.inventory.append("emp_wave_item")
                else:
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["inventory"] = ["emp_wave_item"]
                    elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                        self.ball.set_meta("inventory", ["emp_wave_item"])

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "emp_item":
                if self.world != null and "balls" in self.world:
                    for other_ball in self.world.balls:
                        var same_team = false
                        if "team" in other_ball and "team" in self.ball and other_ball.team == self.ball.team:
                            same_team = true
                        if not same_team:
                            var dist_emp = sqrt(pow(other_ball.x - self.ball.x, 2) + pow(other_ball.y - self.ball.y, 2))
                            if dist_emp < 300.0: # EMP radius
                                var ob_emp_imm = 0.0
                                if "emp_immunity_timer" in other_ball: ob_emp_imm = other_ball.emp_immunity_timer
                                elif typeof(other_ball) == TYPE_OBJECT and other_ball.has_method("get_meta") and other_ball.has_meta("emp_immunity_timer"): ob_emp_imm = other_ball.get_meta("emp_immunity_timer")
                                elif typeof(other_ball) == TYPE_DICTIONARY and other_ball.has("emp_immunity_timer"): ob_emp_imm = other_ball.get("emp_immunity_timer", 0.0)
                                if ob_emp_imm <= 0:
                                    if "has_drone" in other_ball: other_ball.has_drone = false
                                    if "has_shield" in other_ball: other_ball.has_shield = false
                                    if typeof(other_ball) == TYPE_OBJECT and other_ball.has_method("set_meta"):
                                        other_ball.set_meta("speed_booster_timer", 0.0)
                                    elif "speed_booster_timer" in other_ball:
                                        other_ball.speed_booster_timer = 0.0
                                    if "is_emped" in other_ball: other_ball.is_emped = true
                                    elif typeof(other_ball) == TYPE_OBJECT and other_ball.has_method("set_meta"): other_ball.set_meta("is_emped", true)
                                    elif typeof(other_ball) == TYPE_DICTIONARY: other_ball["is_emped"] = true
                                    if "emp_timer" in other_ball: other_ball.emp_timer = 5.0
                                    elif typeof(other_ball) == TYPE_OBJECT and other_ball.has_method("set_meta"): other_ball.set_meta("emp_timer", 5.0)
                                    elif typeof(other_ball) == TYPE_DICTIONARY: other_ball["emp_timer"] = 5.0
                                    if "hud_disabled" in other_ball: other_ball.hud_disabled = true
                                    elif typeof(other_ball) == TYPE_OBJECT and other_ball.has_method("set_meta"): other_ball.set_meta("hud_disabled", true)
                                    elif typeof(other_ball) == TYPE_DICTIONARY: other_ball["hud_disabled"] = true
                                    if "abilities_disabled" in other_ball: other_ball.abilities_disabled = true
                                    elif typeof(other_ball) == TYPE_OBJECT and other_ball.has_method("set_meta"): other_ball.set_meta("abilities_disabled", true)
                                    elif typeof(other_ball) == TYPE_DICTIONARY: other_ball["abilities_disabled"] = true
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "flight_booster":
                if "flight_booster_timer" in self.ball: self.ball.flight_booster_timer = 5.0
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("flight_booster_timer", 5.0)
                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["flight_booster_timer"] = 5.0

                if "is_flying" in self.ball: self.ball.is_flying = true
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("is_flying", true)
                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["is_flying"] = true

                if "is_frictionless" in self.ball: self.ball.is_frictionless = true
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("is_frictionless", true)
                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["is_frictionless"] = true

                if "knockback_immune" in self.ball: self.ball.knockback_immune = true
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("knockback_immune", true)
                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["knockback_immune"] = true

                var bs = 2.0
                if "base_speed" in self.ball: bs = self.ball.base_speed
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"): bs = self.ball.get_meta("base_speed")
                elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("base_speed"): bs = self.ball["base_speed"]

                if "speed" in self.ball: self.ball.speed = bs * 3.0
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("speed", bs * 3.0)
                elif typeof(self.ball) == TYPE_DICTIONARY: self.ball["speed"] = bs * 3.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "speed_booster_item":
                var existing_speed = 0.0
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("speed_boost_timer"):
                    existing_speed = self.ball.get_meta("speed_boost_timer")
                elif "speed_boost_timer" in self.ball:
                    existing_speed = self.ball.speed_boost_timer
                if existing_speed > 0.0:
                    if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("speed_overdrive_timer", 5.0)
                    if "speed_overdrive_timer" in self.ball: self.ball.speed_overdrive_timer = 5.0
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("speed_boost_timer", 5.0)
                if "speed_boost_timer" in self.ball: self.ball.speed_boost_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "zone_immunity":
                var dur = 5.0
                if "duration" in nearest: dur = nearest.duration
                self.ball.set_meta("zone_immunity_timer", dur)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "placeable_trap_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("placeable_trap")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "exit_portal_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("exit_portal")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "position_swap_booster":
                var balls = []
                if "balls" in self.world:
                    balls = self.world.balls
                elif "entities" in self.world:
                    balls = self.world.entities
                var valid_targets = []
                for b in balls:
                    var is_alive = true
                    if "alive" in b: is_alive = b.alive
                    elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")
                    var is_decoy = false
                    if "is_decoy" in b: is_decoy = b.is_decoy
                    elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("is_decoy"): is_decoy = b.get_meta("is_decoy")

                    if is_alive and b != self.ball and not is_decoy:
                        valid_targets.append(b)

                if valid_targets.size() > 0:
                    var my_team = ""
                    if "team" in self.ball: my_team = self.ball.team
                    elif "ball_type" in self.ball: my_team = self.ball.ball_type

                    var enemies = []
                    for b in valid_targets:
                        var b_team = ""
                        if "team" in b: b_team = b.team
                        elif "ball_type" in b: b_team = b.ball_type
                        if b_team != my_team:
                            enemies.append(b)

                    if enemies.size() > 0:
                        var furthest_enemy = enemies[0]
                        var max_dist = -1.0
                        for e in enemies:
                            var ex = e.x if "x" in e else e.position.x if "position" in e else 0.0
                            var ey = e.y if "y" in e else e.position.y if "position" in e else 0.0
                            var dist_sq = (ex - self.ball.x)*(ex - self.ball.x) + (ey - self.ball.y)*(ey - self.ball.y)
                            if dist_sq > max_dist:
                                max_dist = dist_sq
                                furthest_enemy = e

                        var f_ex = furthest_enemy.x if "x" in furthest_enemy else furthest_enemy.position.x if "position" in furthest_enemy else 0.0
                        var f_ey = furthest_enemy.y if "y" in furthest_enemy else furthest_enemy.position.y if "position" in furthest_enemy else 0.0

                        var temp_x = f_ex
                        var temp_y = f_ey

                        if "x" in furthest_enemy:
                            furthest_enemy.x = self.ball.x
                            furthest_enemy.y = self.ball.y
                        elif "position" in furthest_enemy:
                            furthest_enemy.position.x = self.ball.x
                            furthest_enemy.position.y = self.ball.y

                        self.ball.x = temp_x
                        self.ball.y = temp_y

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "position_swap_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("position_swap")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "shuffle_booster":
                var radius = 300.0
                if "radius" in nearest:
                    radius = nearest.radius

                var nearby_players = []
                if self.world != null and "balls" in self.world:
                    for b in self.world.balls:
                        if b != self.ball:
                            var b_alive = true
                            if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") != null:
                                b_alive = b.get("alive")
                            elif typeof(b) == TYPE_DICTIONARY and b.has("alive"):
                                b_alive = b.alive
                            elif typeof(b) == TYPE_OBJECT and "alive" in b:
                                b_alive = b.alive

                            if b_alive:
                                var bx = 0.0
                                var by = 0.0
                                if "x" in b: bx = b.x
                                elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                                if "y" in b: by = b.y
                                elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")

                                var dist = sqrt((bx - self.ball.x)*(bx - self.ball.x) + (by - self.ball.y)*(by - self.ball.y))
                                if dist <= radius:
                                    nearby_players.append(b)

                if nearby_players.size() > 0:
                    var target = nearby_players[randi() % nearby_players.size()]

                    var my_inv = []
                    if self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): my_inv = self.ball.get_meta("inventory")
                    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("inventory"): my_inv = self.ball.inventory

                    var my_skill = null
                    if self.ball.has_method("get_meta") and self.ball.has_meta("active_skill"): my_skill = self.ball.get_meta("active_skill")
                    elif typeof(self.ball) == TYPE_DICTIONARY and self.ball.has("active_skill"): my_skill = self.ball.active_skill

                    var target_inv = []
                    if typeof(target) == TYPE_OBJECT and target.has_method("get_meta") and target.has_meta("inventory"):
                        target_inv = target.get_meta("inventory")
                    elif typeof(target) == TYPE_DICTIONARY and target.has("inventory"):
                        target_inv = target.inventory
                    elif typeof(target) == TYPE_OBJECT and "inventory" in target:
                        target_inv = target.inventory

                    var target_skill = null
                    if typeof(target) == TYPE_OBJECT and target.has_method("get_meta") and target.has_meta("active_skill"):
                        target_skill = target.get_meta("active_skill")
                    elif typeof(target) == TYPE_DICTIONARY and target.has("active_skill"):
                        target_skill = target.active_skill
                    elif typeof(target) == TYPE_OBJECT and "active_skill" in target:
                        target_skill = target.active_skill

                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("inventory", target_inv)
                        self.ball.set_meta("active_skill", target_skill)
                        self.ball.set_meta("shuffle_booster_timer", 10.0)
                        self.ball.set_meta("shuffle_booster_target", target)
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["inventory"] = target_inv
                        self.ball["active_skill"] = target_skill
                        self.ball["shuffle_booster_timer"] = 10.0
                        self.ball["shuffle_booster_target"] = target

                    if typeof(target) == TYPE_OBJECT and target.has_method("set_meta"):
                        target.set_meta("inventory", my_inv)
                        target.set_meta("active_skill", my_skill)
                    elif typeof(target) == TYPE_DICTIONARY:
                        target["inventory"] = my_inv
                        target["active_skill"] = my_skill
                    elif typeof(target) == TYPE_OBJECT:
                        if "inventory" in target: target.inventory = my_inv
                        if "active_skill" in target: target.active_skill = my_skill

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "hookshot_booster":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("hookshot")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var b_idx = self.world.boosters.find(nearest)
                    if b_idx != -1:
                        self.world.boosters.remove_at(b_idx)
            elif "kind" in nearest and nearest.kind == "tether_hook_booster":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("tether_hook")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "grapple_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("grapple_booster_timer", 5.0)
                else:
                    self.ball.grapple_booster_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var b_idx = self.world.boosters.find(nearest)
                    if b_idx != -1:
                        self.world.boosters.remove_at(b_idx)


            elif "kind" in nearest and nearest.kind == "mirror_shield_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("mirror_shield_active", true)
                    self.ball.set_meta("mirror_shield_timer", 5.0)
                else:
                    self.ball.mirror_shield_active = true
                    self.ball.mirror_shield_timer = 5.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "projectile_reflect_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("projectile_reflect_active", true)
                    self.ball.set_meta("projectile_reflect_timer", 5.0)
                else:
                    self.ball.projectile_reflect_active = true
                    self.ball.projectile_reflect_timer = 5.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "deflector_shield_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("deflector_shield_active", true)
                    self.ball.set_meta("deflector_shield_timer", 5.0)
                else:
                    self.ball.deflector_shield_active = true
                    self.ball.deflector_shield_timer = 5.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "rebound_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("rebound_booster_timer", 10.0)
                else:
                    self.ball.rebound_booster_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "bounce_shield_booster":
                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("bounce_shield_active", true)
                    self.ball.set_meta("bounce_shield_timer", 5.0)
                else:
                    self.ball.bounce_shield_active = true
                    self.ball.bounce_shield_timer = 5.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "damage_reflection_booster":
                self.ball.set_meta("damage_reflection_active", true)
                self.ball.set_meta("damage_reflection_timer", 5.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "half_reflect_shield_booster":
                self.ball.set_meta("half_reflect_shield_active", true)
                self.ball.set_meta("half_reflect_shield_timer", 5.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "healing_shield_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["healing_shield_active"] = true
                    self.ball["healing_shield_timer"] = 5.0
                    self.ball["healing_shield_capacity"] = 100.0
                    self.ball["healing_shield_initial_capacity"] = 100.0
                else:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("healing_shield_active", true)
                        self.ball.set_meta("healing_shield_timer", 5.0)
                        self.ball.set_meta("healing_shield_capacity", 100.0)
                        self.ball.set_meta("healing_shield_initial_capacity", 100.0)
                    else:
                        self.ball.healing_shield_active = true
                        self.ball.healing_shield_timer = 5.0
                        self.ball.healing_shield_capacity = 100.0
                        self.ball.healing_shield_initial_capacity = 100.0
                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx >= 0: self.world.arena.hazards.remove(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx >= 0: self.world.boosters.remove(idx)
            elif "kind" in nearest and nearest.kind == "layer_reflect_shield_booster":
                var bonus_dur = 0.0
                if "bonus_reflect_shield_duration" in self.ball: bonus_dur = self.ball.bonus_reflect_shield_duration
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("bonus_reflect_shield_duration"): bonus_dur = self.ball.get_meta("bonus_reflect_shield_duration")
                var bonus_cap = 0.0
                if "bonus_reflect_shield_capacity" in self.ball: bonus_cap = self.ball.bonus_reflect_shield_capacity
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("bonus_reflect_shield_capacity"): bonus_cap = self.ball.get_meta("bonus_reflect_shield_capacity")

                if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
                    self.ball.set_meta("reflect_shield_active", true)
                    self.ball.set_meta("reflect_shield_timer", 5.0 + bonus_dur)
                    self.ball.set_meta("reflect_shield_capacity", 100.0 + bonus_cap)
                    self.ball.set_meta("reflect_shield_initial_capacity", 100.0 + bonus_cap)
                    self.ball.set_meta("reflect_shield_max_layers", 3)
                    self.ball.set_meta("reflect_shield_current_layers", 3)
                else:
                    self.ball.reflect_shield_active = true
                    self.ball.reflect_shield_timer = 5.0 + bonus_dur
                    self.ball.reflect_shield_capacity = 100.0 + bonus_cap
                    self.ball.reflect_shield_initial_capacity = 100.0 + bonus_cap
                    self.ball.reflect_shield_max_layers = 3
                    self.ball.reflect_shield_current_layers = 3
                if "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "safe_zone_teleport_booster":
                self.ball.set_meta("safe_zone_teleport_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "safe_zone_teleport_booster":
                self.ball.set_meta("safe_zone_teleport_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_OBJECT and "kind" in nearest and nearest.kind == "safe_zone_booster":
                self.ball.set_meta("safe_zone_booster_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest["kind"] == "safe_zone_booster":
                self.ball.set_meta("safe_zone_booster_timer", 10.0)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    if self.world.arena.hazards.has(nearest):
                        self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world and self.world.boosters.has(nearest):
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "time_stop_booster":

                var entities = []
                if self.world != null:
                    if "entities" in self.world: entities = self.world.entities
                    elif "balls" in self.world: entities = self.world.balls
                for e in entities:
                    var e_id = e.get("id") if typeof(e) == TYPE_DICTIONARY else (e.get_meta("id") if e.has_method("has_meta") and e.has_meta("id") else (e.id if "id" in e else null))
                    var b_id = self.ball.get("id") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("id") if self.ball.has_method("has_meta") and self.ball.has_meta("id") else (self.ball.id if "id" in self.ball else null))
                    if e_id != null and b_id != null and e_id != b_id:
                        var is_alive = true
                        if typeof(e) == TYPE_DICTIONARY:
                            if e.has("alive"): is_alive = e.alive
                        else:
                            if "alive" in e: is_alive = e.alive
                        if is_alive:
                            var cur_stun = 0.0
                            if typeof(e) == TYPE_DICTIONARY:
                                cur_stun = float(e.get("stun_timer", 0.0))
                                e["stun_timer"] = max(cur_stun, 3.0)
                            elif e.has_method("set_meta"):
                                cur_stun = float(e.get_meta("stun_timer")) if e.has_meta("stun_timer") else (float(e.stun_timer) if "stun_timer" in e else 0.0)
                                e.set_meta("stun_timer", max(cur_stun, 3.0))
                                if "stun_timer" in e: e.stun_timer = max(cur_stun, 3.0)
                            elif "stun_timer" in e:
                                cur_stun = float(e.stun_timer)
                                e.stun_timer = max(cur_stun, 3.0)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    for h in self.world.arena.hazards:
                        var is_disabled = false
                        if typeof(h) == TYPE_DICTIONARY:
                            if h.has("is_disabled_by_flare"): is_disabled = h.is_disabled_by_flare
                        else:
                            if h.has_method("has_meta") and h.has_meta("is_disabled_by_flare"):
                                is_disabled = h.get_meta("is_disabled_by_flare")
                            elif "is_disabled_by_flare" in h:
                                is_disabled = h.is_disabled_by_flare
                        if not is_disabled:
                            var cur_frozen = 0.0
                            if typeof(h) == TYPE_DICTIONARY:
                                cur_frozen = float(h.get("frozen_timer", 0.0))
                                h["frozen_timer"] = max(cur_frozen, 3.0)
                            elif h.has_method("set_meta"):
                                cur_frozen = float(h.get_meta("frozen_timer")) if h.has_meta("frozen_timer") else (float(h.frozen_timer) if "frozen_timer" in h else 0.0)
                                h.set_meta("frozen_timer", max(cur_frozen, 3.0))
                                if "frozen_timer" in h: h.frozen_timer = max(cur_frozen, 3.0)
                            elif "frozen_timer" in h:
                                cur_frozen = float(h.frozen_timer)
                                h.frozen_timer = max(cur_frozen, 3.0)

                if self.world != null and "events" in self.world:
                    var b_id = self.ball.get("id") if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.get_meta("id") if self.ball.has_method("has_meta") and self.ball.has_meta("id") else (self.ball.id if "id" in self.ball else null))
                    self.world.events.append({"type": "time_stop", "data": {"id": b_id}})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "recall_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["recall_timer"] = 5.0
                    self.ball["recall_state"] = {
                        "x": float(self.ball.get("x", 0.0)),
                        "y": float(self.ball.get("y", 0.0)),
                        "hp": float(self.ball.get("hp", self.ball.get("max_hp", 100.0)))
                    }
                else:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("recall_timer", 5.0)
                        self.ball.set_meta("recall_state", {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        })
                    else:
                        self.ball.recall_timer = 5.0
                        self.ball.recall_state = {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        }
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "survival_rewind_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["survival_rewind_timer"] = 5.0
                    self.ball["survival_rewind_state"] = {
                        "x": float(self.ball.get("x", 0.0)),
                        "y": float(self.ball.get("y", 0.0)),
                        "hp": float(self.ball.get("hp", self.ball.get("max_hp", 100.0)))
                    }
                else:
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("survival_rewind_timer", 5.0)
                        self.ball.set_meta("survival_rewind_state", {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        })
                    else:
                        self.ball.survival_rewind_timer = 5.0
                        self.ball.survival_rewind_state = {
                            "x": float(self.ball.x),
                            "y": float(self.ball.y),
                            "hp": float(self.ball.hp) if "hp" in self.ball else float(self.ball.get("max_hp", 100.0))
                        }
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "time_rewind_booster":
                self.ball.set_meta("time_rewind_booster_active", true)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "instant_rewind_booster":
                var history = []
                if typeof(self.ball) == TYPE_DICTIONARY:
                    history = self.ball.get("state_history", [])
                else:
                    if self.ball.has_method("has_meta") and self.ball.has_meta("state_history"):
                        history = self.ball.get_meta("state_history")
                    elif "state_history" in self.ball:
                        history = self.ball.state_history
                if history.size() > 0:
                    # Retrieve state from ~3 seconds ago for instant rewind
                    var past_state_3s = history[0]
                    if typeof(self.ball) == TYPE_DICTIONARY:
                        # Rewind positional coordinates and health
                        self.ball["x"] = past_state_3s.get("x", self.ball.get("x", 0.0))
                        self.ball["y"] = past_state_3s.get("y", self.ball.get("y", 0.0))
                        self.ball["hp"] = past_state_3s.get("hp", self.ball.get("max_hp", 100.0))
                        if "attack_timer" in past_state_3s: self.ball["attack_timer"] = past_state_3s["attack_timer"]
                        if "skill_timer" in past_state_3s: self.ball["skill_timer"] = past_state_3s["skill_timer"]
                    else:
                        # Rewind positional coordinates and health
                        self.ball.x = past_state_3s.get("x", self.ball.x)
                        self.ball.y = past_state_3s.get("y", self.ball.y)
                        if "hp" in self.ball:
                            self.ball.hp = past_state_3s.get("hp", self.ball.max_hp if "max_hp" in self.ball else 100.0)
                        if "attack_timer" in past_state_3s and "attack_timer" in self.ball:
                            self.ball.attack_timer = past_state_3s["attack_timer"]
                        if "skill_timer" in past_state_3s and "skill_timer" in self.ball:
                            self.ball.skill_timer = past_state_3s["skill_timer"]

                    if self.world != null and "events" in self.world:
                        self.world.events.append({"type": "time_rewind", "data": {"id": self.ball.get("id", -1) if typeof(self.ball) == TYPE_DICTIONARY else self.ball.id}})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "portal_gun_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("portal_gun")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and (nearest.kind == "fake_booster" or nearest.kind == "dummy_item" or nearest.kind == "fake_flare" or nearest.kind == "fake_healing_orb"):
                var explosion_radius = 45.0
                if "radius" in nearest:
                    explosion_radius = nearest.radius * 3
                var dmg = 50.0
                if "damage" in nearest: dmg = nearest.damage
                var stun_dur = 2.0
                if "stun_duration" in nearest: stun_dur = nearest.stun_duration

                if self.world != null and "balls" in self.world:
                    for b in self.world.balls:
                        var bx = 0.0
                        var by = 0.0
                        if "x" in b: bx = b.x
                        elif b.has_method("get_meta") and b.has_meta("x"): bx = b.get_meta("x")
                        if "y" in b: by = b.y
                        elif b.has_method("get_meta") and b.has_meta("y"): by = b.get_meta("y")
                        var nx = 0.0
                        var ny = 0.0
                        if "x" in nearest: nx = nearest.x
                        if "y" in nearest: ny = nearest.y

                        var dx = bx - nx
                        var dy = by - ny
                        var dist = sqrt(dx*dx + dy*dy)
                        if dist <= explosion_radius:
                            if b.has_method("take_damage"):
                                b.take_damage(dmg)
                            if b.has_method("set_meta"):
                                b.set_meta("stun_timer", stun_dur)
                            else:
                                b.stun_timer = stun_dur
                            if b.has_method("set_meta"):
                                var current_silence = 0.0
                                if b.has_meta("silence_timer"): current_silence = b.get_meta("silence_timer")
                                b.set_meta("silence_timer", max(current_silence, 5.0))
                            else:
                                var current_silence = 0.0
                                if "silence_timer" in b: current_silence = b.silence_timer
                                b.silence_timer = max(current_silence, 5.0)
                            # Apply knockback using velocity if possible
                            if dist > 0.0001:
                                var knockback_force = 1500.0
                                if "vx" in b and "vy" in b:
                                    b.vx += (dx / dist) * knockback_force
                                    b.vy += (dy / dist) * knockback_force
                                else:
                                    # Fallback clamped
                                    if "x" in b:
                                        b.x += (dx / dist) * 15.0
                                    elif b.has_method("set_meta") and b.has_meta("x"):
                                        b.set_meta("x", b.get_meta("x") + (dx / dist) * 15.0)
                                    if "y" in b:
                                        b.y += (dy / dist) * 15.0
                                    elif b.has_method("set_meta") and b.has_meta("y"):
                                        b.set_meta("y", b.get_meta("y") + (dy / dist) * 15.0)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var num_shrapnel = randi() % 3 + 3 # 3 to 5
                    for i in range(num_shrapnel):
                        var shrapnel = {}
                        shrapnel.kind = "shrapnel"
                        shrapnel.x = nearest.x if "x" in nearest else 0.0
                        shrapnel.y = nearest.y if "y" in nearest else 0.0
                        var angle = randf() * 2.0 * PI
                        var speed = randf() * 200.0 + 200.0 # 200 to 400
                        shrapnel.vx = cos(angle) * speed
                        shrapnel.vy = sin(angle) * speed
                        shrapnel.radius = 5.0
                        shrapnel.duration = 5.0
                        shrapnel.damage = 10.0
                        self.world.arena.hazards.append(shrapnel)

                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "bumper_synergy_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("bumper_synergy_active", true)
                else:
                    self.ball.bumper_synergy_active = true

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "bumper_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("bumper_booster_timer", 10.0)
                else:
                    self.ball.bumper_booster_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "thermal_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("thermal_booster_timer", 15.0)
				else:
					self.ball.thermal_booster_timer = 15.0

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "cooling_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("cooling_booster_timer", 15.0)
				else:
					self.ball.cooling_booster_timer = 15.0

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "hazmat_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("hazmat_booster_timer", 15.0)
				else:
					self.ball.hazmat_booster_timer = 15.0

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "heavy_anchor_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("heavy_anchor_booster_timer", 15.0)
				else:
					self.ball.heavy_anchor_booster_timer = 15.0

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "forecast_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("forecast_booster_active", true)
					self.ball.set_meta("forecast_warning_issued", false)
				else:
					self.ball.forecast_booster_active = true
					self.ball.forecast_warning_issued = false

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "forecast_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("forecast_booster_active", true)
					self.ball.set_meta("forecast_warning_issued", false)
				else:
					self.ball.forecast_booster_active = true
					self.ball.forecast_warning_issued = false

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "weather_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("weather_control_timer", 10.0)
                else:
                    self.ball.weather_control_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "storm_booster":
				if typeof(self.ball) != TYPE_DICTIONARY and self.ball.has_method("set_meta"):
					self.ball.set_meta("storm_booster_timer", 10.0)
					var base_s = self.ball.get_meta("base_speed") if self.ball.has_meta("base_speed") else 200.0
					self.ball.set_meta("speed", base_s * 1.5)
				else:
					self.ball.storm_booster_timer = 10.0
					var base_s = self.ball.get("base_speed", 200.0)
					self.ball.speed = base_s * 1.5
				if self.world.has_method("get_node"):
					var arena = self.world.get_node_or_null("Arena")
					if arena and arena.has_method("get_hazards"):
						var hazards = arena.get_hazards()
						if hazards.has(nearest):
							hazards.erase(nearest)
							if typeof(nearest) != TYPE_DICTIONARY and nearest.has_method("queue_free"):
								nearest.queue_free()
				var b_list = self.world.get("boosters")
				if typeof(b_list) == TYPE_ARRAY and b_list.has(nearest):
					b_list.erase(nearest)
					if typeof(nearest) != TYPE_DICTIONARY and nearest.has_method("queue_free"):
						nearest.queue_free()
			elif "kind" in nearest and nearest.kind == "bomb_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("bomb_booster_timer", 10.0)
				else:
					self.ball.bomb_booster_timer = 10.0

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				var b_list = self.world.get("boosters")
				if typeof(b_list) == TYPE_ARRAY and b_list.has(nearest):
					b_list.erase(nearest)
					if typeof(nearest) != TYPE_DICTIONARY and nearest.has_method("queue_free"):
						nearest.queue_free()
			elif "kind" in nearest and nearest.kind == "cryogenic_booster":
				if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
					self.ball.set_meta("cryogenic_booster_timer", 10.0)
					self.ball.set_meta("shield_booster_active", true)
				elif typeof(self.ball) == TYPE_DICTIONARY:
					self.ball["cryogenic_booster_timer"] = 10.0
					self.ball["shield_booster_active"] = true
				else:
					self.ball.cryogenic_booster_timer = 10.0
					self.ball.shield_booster_active = true

				if typeof(self.world) == TYPE_DICTIONARY and self.world.has("arena") and typeof(self.world.arena) == TYPE_DICTIONARY and self.world.arena.has("hazards"):
					var h_idx = self.world.arena.hazards.find(nearest)
					if h_idx != -1:
						self.world.arena.hazards.remove_at(h_idx)
				elif typeof(self.world) == TYPE_OBJECT and "arena" in self.world and typeof(self.world.arena) == TYPE_OBJECT and "hazards" in self.world.arena:
					var h_idx = self.world.arena.hazards.find(nearest)
					if h_idx != -1:
						self.world.arena.hazards.remove_at(h_idx)

				if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters"):
					var b_idx = self.world.boosters.find(nearest)
					if b_idx != -1:
						self.world.boosters.remove_at(b_idx)
				elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world:
					var b_idx = self.world.boosters.find(nearest)
					if b_idx != -1:
						self.world.boosters.remove_at(b_idx)
			elif "kind" in nearest and nearest.kind == "leech_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("leech_booster_timer", 10.0)
				else:
					self.ball.leech_booster_timer = 10.0

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "glider_booster":
				if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
					self.ball.set_meta("glider_booster_timer", 10.0)
				else:
					self.ball.glider_booster_timer = 10.0
				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "tornado_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("tornado_booster_timer", 5.0)
                else:
                    self.ball.tornado_booster_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "reverse_grapple_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("reverse_grapple_booster_timer", 5.0)
                else:
                    self.ball.reverse_grapple_booster_timer = 5.0
                var enemies = _get_enemies()
                if enemies.size() > 0:
                    var closest_enemy = null
                    var min_dist_sq = 999999.0
                    for e in enemies:
                        var e_x = e.get("x") if typeof(e) == TYPE_DICTIONARY else e.x
                        var e_y = e.get("y") if typeof(e) == TYPE_DICTIONARY else e.y
                        var b_x = self.ball.get("x") if typeof(self.ball) == TYPE_DICTIONARY else self.ball.x
                        var b_y = self.ball.get("y") if typeof(self.ball) == TYPE_DICTIONARY else self.ball.y
                        var d_sq = (e_x - b_x)*(e_x - b_x) + (e_y - b_y)*(e_y - b_y)
                        if d_sq < min_dist_sq:
                            min_dist_sq = d_sq
                            closest_enemy = e
                    if closest_enemy != null:
                        if typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["reverse_grapple_target"] = closest_enemy
                        else:
                            if "reverse_grapple_target" in self.ball: self.ball.reverse_grapple_target = closest_enemy
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("reverse_grapple_target", closest_enemy)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "magnet_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("pull_booster_timer", 5.0)
                else:
                    self.ball.pull_booster_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "repulsor_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("repulsor_booster_timer", 10.0)
                else:
                    self.ball.repulsor_booster_timer = 10.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "gravity_well_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("gravity_well_aura_timer", 5.0)
                else:
                    self.ball.gravity_well_aura_timer = 5.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "weather_scanner_item":
                if not self.ball.has_meta("inventory"):
                    self.ball.set_meta("inventory", [])
                var inv = self.ball.get_meta("inventory")
                inv.append("weather_scanner")
                self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "weather_shield_item":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("weather_shield")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)

                if world != null and "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1:
                        world.arena.hazards.remove_at(idx)
                if world != null and "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1:
                        world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "gravity_boots":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("gravity_boots")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "mega_starlight_booster":
                if typeof(self.world) != TYPE_DICTIONARY and "events" in self.world:
                    var t_team = ""
                    if "team" in self.ball: t_team = self.ball.team
                    var t_id = 0
                    if "id" in self.ball: t_id = self.ball.id
                    self.world.events.append({"type": "starlight_booster_collected", "data": {"ball_id": t_id, "team": t_team}})

                var team = ""
                if "team" in self.ball: team = self.ball.team
                if team != "" and self.world != null and "balls" in self.world:
                    for member in self.world.balls:
                        var m_team = ""
                        if "team" in member: m_team = member.team
                        if m_team == team:
                            if "speed" in member:
                                member.speed += 20.0
                                if "base_speed" in member:
                                    member.base_speed += 20.0
                                elif member.has_method("has_meta") and member.has_meta("base_speed"):
                                    member.set_meta("base_speed", member.get_meta("base_speed") + 20.0)
                            elif member.has_method("has_meta") and member.has_meta("speed"):
                                member.set_meta("speed", member.get_meta("speed") + 20.0)
                                if member.has_meta("base_speed"):
                                    member.set_meta("base_speed", member.get_meta("base_speed") + 20.0)

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "invisible_status_trap_item":
                var inv = self.ball.get("inventory", []) if typeof(self.ball) == TYPE_DICTIONARY else (self.ball.inventory if "inventory" in self.ball else [])
                inv.append("invisible_status_trap")
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["inventory"] = inv
                elif "inventory" in self.ball:
                    self.ball.inventory = inv
                if world.has("arena") and world.arena != null and world.arena.has("hazards"):
                    if world.arena.hazards.has(nearest):
                        world.arena.hazards.erase(nearest)
                if world.has("boosters") and world.boosters.has(nearest):
                    world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "decoy_volatile_barrel_item":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("decoy_volatile_barrel")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "booster_trap_item":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("booster_trap")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "zero_gravity_trap_item":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("zero_gravity_trap")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "tracker_booster":
                var all_enemies = []
                if self.world != null and "balls" in self.world:
                    for b in self.world.balls:
                        var b_team = b.team if "team" in b else (b.get_meta("team") if b.has_method("has_meta") and b.has_meta("team") else (b.ball_type if "ball_type" in b else ""))
                        var my_team = self.ball.team if "team" in self.ball else (self.ball.get_meta("team") if self.ball.has_method("has_meta") and self.ball.has_meta("team") else (self.ball.ball_type if "ball_type" in self.ball else ""))
                        var b_alive = b.alive if "alive" in b else (b.get_meta("alive") if b.has_method("has_meta") and b.has_meta("alive") else true)
                        var b_decoy = b.is_decoy if "is_decoy" in b else (b.get_meta("is_decoy") if b.has_method("has_meta") and b.has_meta("is_decoy") else false)
                        var b_illusion = b.is_illusion if "is_illusion" in b else (b.get_meta("is_illusion") if b.has_method("has_meta") and b.has_meta("is_illusion") else false)
                        if b != self.ball and b_team != my_team and b_alive and not b_decoy and not b_illusion:
                            all_enemies.append(b)
                if all_enemies.size() > 0:
                    var closest_enemy = all_enemies[0]
                    var min_enemy_dist = INF
                    for b in all_enemies:
                        var dsq = pow(b.x - self.ball.x, 2) + pow(b.y - self.ball.y, 2)
                        if dsq < min_enemy_dist:
                            min_enemy_dist = dsq
                            closest_enemy = b
                    var t_id = closest_enemy.id if "id" in closest_enemy else null
                    if typeof(self.ball) == TYPE_OBJECT:
                        if "tracker_booster_target" in self.ball: self.ball.tracker_booster_target = t_id
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("tracker_booster_target", t_id)
                        if "tracker_booster_timer" in self.ball: self.ball.tracker_booster_timer = 20.0
                        elif self.ball.has_method("set_meta"): self.ball.set_meta("tracker_booster_timer", 20.0)
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        self.ball["tracker_booster_target"] = t_id
                        self.ball["tracker_booster_timer"] = 20.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "laser_sight_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("laser_sight_timer", 15.0)
                else: self.ball.laser_sight_timer = 15.0

                var ls_applied = false
                if "laser_sight_applied" in self.ball: ls_applied = self.ball.laser_sight_applied
                elif self.ball.has_method("has_meta") and self.ball.has_meta("laser_sight_applied"): ls_applied = self.ball.get_meta("laser_sight_applied")

                if not ls_applied:
                    var cur_ar = 150.0
                    if "attack_range" in self.ball: cur_ar = self.ball.attack_range
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("attack_range"): cur_ar = self.ball.get_meta("attack_range")

                    var ba = cur_ar
                    if "base_attack_range" in self.ball: ba = self.ball.base_attack_range
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("base_attack_range"): ba = self.ball.get_meta("base_attack_range")

                    ba *= 1.5
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("base_attack_range", ba)
                        self.ball.set_meta("attack_range", ba)
                        self.ball.set_meta("laser_sight_applied", true)
                    else:
                        self.ball.base_attack_range = ba
                        self.ball.attack_range = ba
                        self.ball.laser_sight_applied = true

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "placeable_trap_booster":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("placeable_trap_booster")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "aura_amplifier_trap_booster":
                var inv_tmp = []
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if "inventory" in self.ball: inv_tmp = self.ball.inventory
                    else: self.ball["inventory"] = inv_tmp
                else:
                    if self.ball.has_method("has_meta") and self.ball.has_meta("inventory"): inv_tmp = self.ball.get_meta("inventory")
                if typeof(inv_tmp) == TYPE_ARRAY:
                    inv_tmp.append("aura_amplifier_trap_booster")
                    if typeof(self.ball) == TYPE_DICTIONARY: self.ball.inventory = inv_tmp
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv_tmp)
                if "arena" in world and "hazards" in world.arena:
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1: world.arena.hazards.remove_at(idx)
                if "boosters" in world:
                    var idx = world.boosters.find(nearest)
                    if idx != -1: world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "aura_inverter_trap_booster":

                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("aura_inverter_trap_booster")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "smoke_grenade":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("smoke_grenade")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "deployable_black_hole":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("deployable_black_hole")
            elif h_kind == "deployable_fake_weather_station":
                var current_tick = 0
                if world != null and "tick" in world: current_tick = world.tick

                var last_updated = -1
                if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("last_updated_tick"):
                    last_updated = hazard.get_meta("last_updated_tick")
                elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("last_updated_tick"):
                    last_updated = hazard["last_updated_tick"]

                if last_updated != current_tick:
                    if typeof(hazard) == TYPE_OBJECT:
                        hazard.set_meta("last_updated_tick", current_tick)
                    elif typeof(hazard) == TYPE_DICTIONARY:
                        hazard["last_updated_tick"] = current_tick

                    var owner_id = null
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("owner_id"):
                        owner_id = hazard.get_meta("owner_id")
                    elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("owner_id"):
                        owner_id = hazard["owner_id"]

                    var capturers = []
                    if world != null and "balls" in world:
                        for b in world.balls:
                            var b_alive = true
                            if typeof(b) == TYPE_OBJECT and "alive" in b: b_alive = b.alive
                            elif typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]

                            var b_id = null
                            if typeof(b) == TYPE_OBJECT and "id" in b: b_id = b.id
                            elif typeof(b) == TYPE_DICTIONARY and b.has("id"): b_id = b["id"]

                            if b_alive and b_id != owner_id:
                                var bx = 0.0; var by = 0.0
                                if typeof(b) == TYPE_OBJECT: bx = b.x; by = b.y
                                elif typeof(b) == TYPE_DICTIONARY: bx = b["x"]; by = b["y"]

                                var dist_sq = (bx - hazard.x) * (bx - hazard.x) + (by - hazard.y) * (by - hazard.y)
                                var h_rad = 150.0
                                if typeof(hazard) == TYPE_OBJECT and "radius" in hazard: h_rad = hazard.radius
                                elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("radius"): h_rad = hazard["radius"]

                                if dist_sq <= (h_rad * h_rad):
                                    capturers.append(b)

                    if capturers.size() > 0:
                        var progress = 0.0
                        if typeof(hazard) == TYPE_OBJECT and hazard.has_meta("capture_progress"):
                            progress = hazard.get_meta("capture_progress")
                        elif typeof(hazard) == TYPE_DICTIONARY and hazard.has("capture_progress"):
                            progress = hazard["capture_progress"]

                        progress += 20.0 * delta

                        if typeof(hazard) == TYPE_OBJECT:
                            hazard.set_meta("capture_progress", progress)
                        elif typeof(hazard) == TYPE_DICTIONARY:
                            hazard["capture_progress"] = progress

                        if progress >= 100.0:
                            if typeof(hazard) == TYPE_OBJECT:
                                hazard.active = false
                            elif typeof(hazard) == TYPE_DICTIONARY:
                                hazard["active"] = false

                            if world != null and "events" in world:
                                world.events.append({"type": "emp_pulse_hit", "data": {"x": hazard.x, "y": hazard.y, "radius": 250.0}})

                            for b in capturers:
                                if typeof(b) == TYPE_OBJECT:
                                    if "hp" in b:
                                        b.hp -= 30.0
                                        if b.hp <= 0: b.alive = false
                                    if "speed_debuff_timer" in b:
                                        b.speed_debuff_timer = max(b.speed_debuff_timer, 5.0)
                                    elif b.has_method("set"):
                                        b.set("speed_debuff_timer", 5.0)
                                    if "speed_debuff_multiplier" in b:
                                        b.speed_debuff_multiplier = 0.5
                                    elif b.has_method("set"):
                                        b.set("speed_debuff_multiplier", 0.5)
                                elif typeof(b) == TYPE_DICTIONARY:
                                    if b.has("hp"):
                                        b["hp"] -= 30.0
                                        if b["hp"] <= 0: b["alive"] = false
                                    b["speed_debuff_timer"] = 5.0
                                    b["speed_debuff_multiplier"] = 0.5

            elif h_kind == "deployable_shockwave_mine":
                var inv = []
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("has_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                elif "inventory" in self.ball: inv = self.ball.inventory
                if typeof(inv) != TYPE_ARRAY: inv = []
                inv.append("deployable_shockwave_mine")
                if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                elif "inventory" in self.ball: self.ball.inventory = inv
                if "boosters" in world and nearest in world.boosters:
                    world.boosters.erase(nearest)
                if "arena" in world and "hazards" in world.arena and nearest in world.arena.hazards:
                    world.arena.hazards.erase(nearest)
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "safe_zone_radar":
                if self.world != null and "arena" in self.world and "items" in self.world.arena:
                    var idx = self.world.arena.items.find(nearest)
                    if idx != -1:
                        self.world.arena.items.remove_at(idx)
                inv.append("safe_zone_radar")
            elif "kind" in nearest and nearest.kind == "reverse_gravity_item":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                if typeof(inv) != TYPE_ARRAY: inv = []
                inv.append("reverse_gravity_item")
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["inventory"] = inv
                elif "inventory" in self.ball:
                    self.ball.inventory = inv
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                    self.ball.set_meta("inventory", inv)
                if nearest.has("active"):
                    nearest.active = false
                elif typeof(nearest) == TYPE_OBJECT and "active" in nearest:
                    nearest.active = false
                if world != null and world.has("arena") and world.arena != null and world.arena.has("hazards"):
                    var idx = world.arena.hazards.find(nearest)
                    if idx != -1: world.arena.hazards.remove_at(idx)
                if world != null and world.has("boosters"):
                    var idx = world.boosters.find(nearest)
                    if idx != -1: world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "lightning_rod_item":
                var inv = []
                if "inventory" in self.ball: inv = self.ball.inventory
                elif self.ball.has_method("get_meta") and self.ball.has_meta("inventory"): inv = self.ball.get_meta("inventory")
                inv.append("lightning_rod_item")
                if "inventory" in self.ball: self.ball.inventory = inv
                elif self.ball.has_method("set_meta"): self.ball.set_meta("inventory", inv)
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "charging_shockwave_shield_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["charging_shockwave_shield_active"] = true
                    self.ball["charging_shockwave_shield_timer"] = 0.0
                else:
                    self.ball.set_meta("charging_shockwave_shield_active", true)
                    self.ball.set_meta("charging_shockwave_shield_timer", 0.0)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "crystal_armor_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["crystal_armor_active"] = true
                    self.ball["crystal_armor_charges"] = 3
                else:
                    self.ball.set_meta("crystal_armor_active", true)
                    self.ball.set_meta("crystal_armor_charges", 3)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world and self.world.boosters != null:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "trap_disarm_kit":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["trap_disarm_timer"] = 5.0
                else:
                    if "trap_disarm_timer" in self.ball:
                        self.ball.trap_disarm_timer = 5.0
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("trap_disarm_timer", 5.0)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "quantum_relay_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["has_quantum_relay"] = true
                    self.ball["quantum_relay_timer"] = 30.0
                    self.ball["quantum_relay_x"] = self.ball.x
                    self.ball["quantum_relay_y"] = self.ball.y
                else:
                    if "has_quantum_relay" in self.ball:
                        self.ball.has_quantum_relay = true
                        self.ball.quantum_relay_timer = 30.0
                        self.ball.quantum_relay_x = self.ball.x
                        self.ball.quantum_relay_y = self.ball.y
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("has_quantum_relay", true)
                        self.ball.set_meta("quantum_relay_timer", 30.0)
                        self.ball.set_meta("quantum_relay_x", self.ball.x)
                        self.ball.set_meta("quantum_relay_y", self.ball.y)
                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters") and self.world["boosters"].has(nearest):
                    self.world["boosters"].erase(nearest)
                elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world and nearest in self.world.boosters:
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "quantum_leap_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["quantum_leap_active"] = true
                else:
                    if "quantum_leap_active" in self.ball:
                        self.ball.quantum_leap_active = true
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("quantum_leap_active", true)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx_h = self.world.arena.hazards.find(nearest)
                    if idx_h != -1:
                        self.world.arena.hazards.remove_at(idx_h)
                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("boosters") and self.world["boosters"].has(nearest):
                    self.world["boosters"].erase(nearest)
                elif typeof(self.world) == TYPE_OBJECT and "boosters" in self.world and nearest in self.world.boosters:
                    self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "death_defy_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["death_defy_active"] = true
                else:
                    if "death_defy_active" in self.ball:
                        self.ball.death_defy_active = true
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta("death_defy_active", true)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "nemesis_shield_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["nemesis_shield_active"] = true
                elif typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"):
                    self.ball.set_meta("nemesis_shield_active", true)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "shield_booster":
                if typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["shield_booster_active"] = true
                else:
                    self.ball.set_meta("shield_booster_active", true)

                if self.world != null and "arena" in self.world and self.world.arena != null and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "stamina_booster":
                var max_stam = 100.0
                var current_stam = 0.0
                if self.ball.has_method("get_meta") and self.ball.has_meta("max_stamina"): max_stam = self.ball.get_meta("max_stamina")
                elif "max_stamina" in self.ball: max_stam = self.ball.max_stamina

                if self.ball.has_method("get_meta") and self.ball.has_meta("stamina"): current_stam = self.ball.get_meta("stamina")
                elif "stamina" in self.ball: current_stam = self.ball.stamina

                if self.ball.has_method("set_meta"):
                    if current_stam >= max_stam:
                        var cur_speed = 0.0
                        if self.ball.has_meta("speed_boost_timer"): cur_speed = self.ball.get_meta("speed_boost_timer")
                        self.ball.set_meta("speed_boost_timer", cur_speed + 3.0)
                    self.ball.set_meta("stamina", max_stam)
                    self.ball.set_meta("infinite_stamina_timer", 5.0)
                else:
                    if current_stam >= max_stam:
                        var cur_speed = 0.0
                        if "speed_boost_timer" in self.ball: cur_speed = self.ball.speed_boost_timer
                        self.ball.speed_boost_timer = cur_speed + 3.0
                    self.ball.stamina = max_stam
                    self.ball.infinite_stamina_timer = 5.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "forecast_booster":
				if self.ball.has_method("set_meta"):
					self.ball.set_meta("forecast_booster_active", true)
					self.ball.set_meta("forecast_warning_issued", false)
				else:
					self.ball.forecast_booster_active = true
					self.ball.forecast_warning_issued = false

				if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
					var idx = self.world.arena.hazards.find(nearest)
					if idx != -1:
						self.world.arena.hazards.remove_at(idx)
				if self.world != null and "boosters" in self.world:
					var idx = self.world.boosters.find(nearest)
					if idx != -1:
						self.world.boosters.remove_at(idx)
			elif "kind" in nearest and nearest.kind == "weather_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("weather_control_timer", 10.0)
                else:
                    self.ball.weather_control_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "cleanser":
                if "burn_timer" in self.ball: self.ball.burn_timer = 0.0
                if "poison_timer" in self.ball: self.ball.poison_timer = 0.0
                if "slow_timer" in self.ball: self.ball.slow_timer = 0.0
                if "silence_timer" in self.ball: self.ball.silence_timer = 0.0
                if "stun_timer" in self.ball:
                    self.ball.stun_timer = 0.0
                    if "is_stunned" in self.ball: self.ball.is_stunned = false

                var link_target = null
                if "damage_link_target" in self.ball: link_target = self.ball.damage_link_target
                elif self.ball.has_method("get_meta") and self.ball.has_meta("damage_link_target"): link_target = self.ball.get_meta("damage_link_target")

                if link_target != null:
                    var target_link = null
                    if "damage_link_target" in link_target: target_link = link_target.damage_link_target
                    elif link_target.has_method("get_meta") and link_target.has_meta("damage_link_target"): target_link = link_target.get_meta("damage_link_target")

                    if target_link == self.ball:
                        if "damage_link_target" in link_target: link_target.damage_link_target = null
                        elif link_target.has_method("set_meta"): link_target.set_meta("damage_link_target", null)

                    if "damage_link_target" in self.ball: self.ball.damage_link_target = null
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("damage_link_target", null)
            elif "kind" in nearest and nearest.kind == "chain_lightning_booster":
                var enemies = _get_enemies()
                if enemies.size() > 0:
                    var target = null
                    var min_dist = INF
                    for e in enemies:
                        var d = (e.x - self.ball.x)*(e.x - self.ball.x) + (e.y - self.ball.y)*(e.y - self.ball.y)
                        if d < min_dist:
                            min_dist = d
                            target = e
                    if target != null:
                        var current_damage = 25.0
                        if "hp" in target:
                            target.hp -= current_damage
                        elif target.has_method("set_meta") and target.has_meta("hp"):
                            target.set_meta("hp", target.get_meta("hp") - current_damage)
                        if self.world != null and "events" in self.world:
                            self.world.events.append({"type": "visual_effect", "data": {"type": "lightning", "x": self.ball.x, "y": self.ball.y, "tx": target.x, "ty": target.y}})

                        var bounced_enemies = [target]
                        var current_pos = target
                        for i in range(3):
                            current_damage *= 0.8
                            var next_target = null
                            var best_dist = INF
                            for e in enemies:
                                if bounced_enemies.find(e) == -1:
                                    var is_alive = true
                                    if "alive" in e: is_alive = e.alive
                                    if is_alive:
                                        var d = (e.x - current_pos.x)*(e.x - current_pos.x) + (e.y - current_pos.y)*(e.y - current_pos.y)
                                        if d < best_dist and d < 40000:
                                            best_dist = d
                                            next_target = e
                            if next_target != null:
                                if "hp" in next_target:
                                    next_target.hp -= current_damage
                                elif next_target.has_method("set_meta") and next_target.has_meta("hp"):
                                    next_target.set_meta("hp", next_target.get_meta("hp") - current_damage)
                                if self.world != null and "events" in self.world:
                                    self.world.events.append({"type": "visual_effect", "data": {"type": "lightning", "x": current_pos.x, "y": current_pos.y, "tx": next_target.x, "ty": next_target.y}})
                                bounced_enemies.append(next_target)
                                current_pos = next_target
                            else:
                                break
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "chain_lightning_overload_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("chain_lightning_overload_timer", 15.0)
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["chain_lightning_overload_timer"] = 15.0
                else:
                    self.ball.chain_lightning_overload_timer = 15.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "storm_caller_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("storm_caller_timer", 15.0)
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    self.ball["storm_caller_timer"] = 15.0
                else:
                    self.ball.storm_caller_timer = 15.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "vampiric_frenzy_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("vampiric_frenzy_timer", 15.0)
                else:
                    self.ball.vampiric_frenzy_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "juggernaut_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("juggernaut_booster_timer", 15.0)
                else:
                    self.ball.juggernaut_booster_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "mirage_booster":
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("mirage_booster_timer", 15.0)
                    self.ball.set_meta("mirage_spawn_timer", 0.0)
                else:
                    self.ball.mirage_booster_timer = 15.0
                    self.ball.mirage_spawn_timer = 0.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "damage_link_booster":
                var enemies_link = _get_enemies()
                if enemies_link.size() > 0:
                    var link_target = null
                    var min_dist_link_sq = INF
                    for e in enemies_link:
                        var d_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                        if d_sq < min_dist_link_sq:
                            min_dist_link_sq = d_sq
                            link_target = e
                    if link_target != null:
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("damage_link_target", link_target)
                        else:
                            self.ball.damage_link_target = link_target

                        if link_target.has_method("set_meta"):
                            link_target.set_meta("damage_link_target", self.ball)
                        elif "damage_link_target" in link_target:
                            link_target.damage_link_target = self.ball

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "entanglement_booster":
                var others = []
                if self.world != null and "balls" in self.world:
                    for b in self.world.balls:
                        var alive = true
                        if typeof(b) == TYPE_DICTIONARY:
                            alive = b.get("alive", true)
                        elif "alive" in b:
                            alive = b.alive

                        var b_id = -1
                        if typeof(b) == TYPE_DICTIONARY:
                            b_id = b.get("id", -1)
                        elif "id" in b:
                            b_id = b.id

                        var my_id = -1
                        if typeof(self.ball) == TYPE_DICTIONARY:
                            my_id = self.ball.get("id", -1)
                        elif "id" in self.ball:
                            my_id = self.ball.id

                        if alive and b_id != my_id:
                            others.append(b)

                if others.size() > 0:
                    var link_target = null
                    var min_dist_link_sq = INF
                    for e in others:
                        var e_x = e.get("x", 0.0) if typeof(e) == TYPE_DICTIONARY else e.x
                        var e_y = e.get("y", 0.0) if typeof(e) == TYPE_DICTIONARY else e.y
                        var my_x = self.ball.get("x", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else self.ball.x
                        var my_y = self.ball.get("y", 0.0) if typeof(self.ball) == TYPE_DICTIONARY else self.ball.y
                        var d_sq = pow(e_x - my_x, 2) + pow(e_y - my_y, 2)
                        if d_sq < min_dist_link_sq:
                            min_dist_link_sq = d_sq
                            link_target = e

                    if link_target != null:
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("entanglement_target", link_target)
                            self.ball.set_meta("entanglement_timer", 10.0)
                        elif typeof(self.ball) == TYPE_DICTIONARY:
                            self.ball["entanglement_target"] = link_target
                            self.ball["entanglement_timer"] = 10.0
                        else:
                            self.ball.entanglement_target = link_target
                            self.ball.entanglement_timer = 10.0

                        if link_target.has_method("set_meta"):
                            link_target.set_meta("entanglement_target", self.ball)
                            link_target.set_meta("entanglement_timer", 10.0)
                        elif typeof(link_target) == TYPE_DICTIONARY:
                            link_target["entanglement_target"] = self.ball
                            link_target["entanglement_timer"] = 10.0
                        else:
                            link_target.entanglement_target = self.ball
                            link_target.entanglement_timer = 10.0

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and (nearest.kind == "fragment_of_aegis" or nearest.kind == "fragment_of_hermes"):
                var frag_kind = nearest.kind
                var current_count = 0
                if frag_kind in self.ball:
                    current_count = self.ball.get(frag_kind)
                elif self.ball.has_method("get_meta") and self.ball.has_meta(frag_kind):
                    current_count = self.ball.get_meta(frag_kind)

                current_count += 1

                if frag_kind in self.ball:
                    self.ball.set(frag_kind, current_count)
                elif self.ball.has_method("set_meta"):
                    self.ball.set_meta(frag_kind, current_count)

                if current_count >= 3:
                    if frag_kind in self.ball:
                        self.ball.set(frag_kind, 0)
                    elif self.ball.has_method("set_meta"):
                        self.ball.set_meta(frag_kind, 0)

                    if frag_kind == "fragment_of_aegis":
                        if "has_aegis_shield" in self.ball:
                            self.ball.has_aegis_shield = true
                            self.ball.aegis_shield_cooldown = 0.0
                            self.ball.aegis_shield_active_timer = 0.0
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("has_aegis_shield", true)
                            self.ball.set_meta("aegis_shield_cooldown", 0.0)
                            self.ball.set_meta("aegis_shield_active_timer", 0.0)
                        if self.world != null and "events" in self.world:
                            self.world.events.append(["artifact_completed", {"artifact": "aegis_shield", "ball_id": self.ball.id}])
                    elif frag_kind == "fragment_of_hermes":
                        if "has_hermes_boots" in self.ball:
                            self.ball.has_hermes_boots = true
                            self.ball.hermes_boots_cooldown = 0.0
                            self.ball.hermes_boots_active_timer = 0.0
                        elif self.ball.has_method("set_meta"):
                            self.ball.set_meta("has_hermes_boots", true)
                            self.ball.set_meta("hermes_boots_cooldown", 0.0)
                            self.ball.set_meta("hermes_boots_active_timer", 0.0)
                        if self.world != null and "events" in self.world:
                            self.world.events.append(["artifact_completed", {"artifact": "hermes_boots", "ball_id": self.ball.id}])

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)
            elif "kind" in nearest and nearest.kind == "link_booster":
                var enemies_link = _get_enemies()
                if enemies_link.size() > 0:
                    var link_target = null
                    var min_dist_link_sq = INF
                    for e in enemies_link:
                        var d_sq = pow(e.x - self.ball.x, 2) + pow(e.y - self.ball.y, 2)
                        if d_sq < min_dist_link_sq:
                            min_dist_link_sq = d_sq
                            link_target = e
                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("link_booster_timer", 5.0)
                        self.ball.set_meta("link_booster_target", link_target)
                    else:
                        self.ball.link_booster_timer = 5.0
                        self.ball.link_booster_target = link_target

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "quantum_swap_powerup":
                var enemies_list = _get_enemies()
                if enemies_list.size() > 0:
                    var valid_enemies = []
                    for e in enemies_list:
                        var dx_e = e.x - self.ball.x
                        var dy_e = e.y - self.ball.y
                        if dx_e * dx_e + dy_e * dy_e <= 250000.0:
                            valid_enemies.append(e)

                    if valid_enemies.size() > 0:
                        var rng = RandomNumberGenerator.new()
                        rng.randomize()
                        var target = valid_enemies[rng.randi() % valid_enemies.size()]

                        var b_x_orig = self.ball.x
                        var b_y_orig = self.ball.y
                        var target_x = target.x
                        var target_y = target.y

                        self.ball.x = target_x
                        self.ball.y = target_y
                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("intangible", true)
                            self.ball.set_meta("intangible_timer", 2.0)
                        else:
                            self.ball.intangible = true
                            self.ball.intangible_timer = 2.0

                        target.x = b_x_orig
                        target.y = b_y_orig
                        if target.has_method("set_meta"):
                            target.set_meta("stun_timer", max(target.get_meta("stun_timer") if target.has_meta("stun_timer") else 0.0, 1.5))
                            target.set_meta("confusion_timer", max(target.get_meta("confusion_timer") if target.has_meta("confusion_timer") else 0.0, 2.0))
                        else:
                            if "stun_timer" in target:
                                target.stun_timer = max(target.stun_timer, 1.5)
                            else:
                                target.stun_timer = 1.5
                            if "confusion_timer" in target:
                                target.confusion_timer = max(target.confusion_timer, 2.0)
                            else:
                                target.confusion_timer = 2.0

                        if "events" in self.world:
                            self.world.events.append({"type": "quantum_swap", "x": b_x_orig, "y": b_y_orig, "target_x": target_x, "target_y": target_y})

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)

                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1:
                        self.world.boosters.remove_at(idx)

            elif "kind" in nearest and nearest.kind == "silencer_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("silencer_timer", 15.0)
                else: self.ball.silencer_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "extended_mag_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("extended_mag_timer", 15.0)
                else: self.ball.extended_mag_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "modified_scope_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("modified_scope_timer", 15.0)
                else: self.ball.modified_scope_timer = 15.0

                var ms_applied = false
                if "modified_scope_applied" in self.ball: ms_applied = self.ball.modified_scope_applied
                elif self.ball.has_method("has_meta") and self.ball.has_meta("modified_scope_applied"): ms_applied = self.ball.get_meta("modified_scope_applied")

                if not ms_applied:
                    var cur_pr = 250.0
                    if "perception_radius" in self.ball: cur_pr = self.ball.perception_radius
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("perception_radius"): cur_pr = self.ball.get_meta("perception_radius")

                    var bp = cur_pr
                    if "base_perception_radius" in self.ball: bp = self.ball.base_perception_radius
                    elif self.ball.has_method("has_meta") and self.ball.has_meta("base_perception_radius"): bp = self.ball.get_meta("base_perception_radius")

                    bp *= 1.5

                    if self.ball.has_method("set_meta"):
                        self.ball.set_meta("base_perception_radius", bp)
                        self.ball.set_meta("perception_radius", bp)
                        self.ball.set_meta("modified_scope_applied", true)
                    else:
                        self.ball.base_perception_radius = bp
                        self.ball.perception_radius = bp
                        self.ball.modified_scope_applied = true

                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "fire_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("fire_attachment_timer", 15.0)
                else: self.ball.fire_attachment_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "shrink_beam_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("shrink_beam_attachment_timer", 15.0)
                else: self.ball.shrink_beam_attachment_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(nearest)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(nearest)
            elif "kind" in nearest and nearest.kind == "ice_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("ice_attachment_timer", 15.0)
                else: self.ball.ice_attachment_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "spread_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("spread_attachment_timer", 15.0)
                else: self.ball.spread_attachment_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "pierce_attachment":
                if self.ball.has_method("set_meta"): self.ball.set_meta("pierce_attachment_timer", 15.0)
                else: self.ball.pierce_attachment_timer = 15.0
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1: self.world.arena.hazards.erase(b)
                if self.world != null and "boosters" in self.world:
                    var idx = self.world.boosters.find(nearest)
                    if idx != -1: self.world.boosters.erase(b)
            elif "kind" in nearest and nearest.kind == "chain_lightning":
                var dur = 5.0
                if "duration" in nearest: dur = nearest.duration
                if self.ball.has_method("set_meta"):
                    self.ball.set_meta("chain_lightning_timer", dur)
                elif "chain_lightning_timer" in self.ball:
                    self.ball.chain_lightning_timer = dur
                if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
                    var idx = self.world.arena.hazards.find(nearest)
                    if idx != -1:
                        self.world.arena.hazards.remove_at(idx)
            else:
                var is_cursed = false
                if self.world != null and "mode" in self.world:
                    if typeof(self.world.mode) == TYPE_OBJECT and "name" in self.world.mode and self.world.mode.name == "Cursed Boosters":
                        is_cursed = true
                    elif typeof(self.world.mode) == TYPE_DICTIONARY and self.world.mode.has("name") and self.world.mode["name"] == "Cursed Boosters":
                        is_cursed = true

                var pre_hp = 100.0
                var pre_speed = 100.0
                var pre_damage = 10.0
                var pre_stamina = 100.0

                if is_cursed:
                    if typeof(self.ball) == TYPE_OBJECT:
                        if "hp" in self.ball: pre_hp = self.ball.hp
                        if "speed" in self.ball: pre_speed = self.ball.speed
                        if "damage" in self.ball: pre_damage = self.ball.damage
                        if "stamina" in self.ball: pre_stamina = self.ball.stamina
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        if self.ball.has("hp"): pre_hp = self.ball["hp"]
                        if self.ball.has("speed"): pre_speed = self.ball["speed"]
                        if self.ball.has("damage"): pre_damage = self.ball["damage"]
                        if self.ball.has("stamina"): pre_stamina = self.ball["stamina"]

                if self.world != null and self.world.has_method("_collect_booster"):
                    self.world._collect_booster(self.ball, nearest)

                var current_hp = pre_hp
                var current_speed = pre_speed
                if typeof(self.ball) == TYPE_OBJECT:
                    if "hp" in self.ball: current_hp = self.ball.hp
                    if "speed" in self.ball: current_speed = self.ball.speed
                elif typeof(self.ball) == TYPE_DICTIONARY:
                    if self.ball.has("hp"): current_hp = self.ball["hp"]
                    if self.ball.has("speed"): current_speed = self.ball["speed"]

                var ent_timer = 0.0
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if self.ball.has("entanglement_timer"): ent_timer = self.ball["entanglement_timer"]
                elif self.ball.has_method("get_meta") and self.ball.has_meta("entanglement_timer"):
                    ent_timer = self.ball.get_meta("entanglement_timer")
                elif "entanglement_timer" in self.ball:
                    ent_timer = self.ball.entanglement_timer

                var target = null
                if typeof(self.ball) == TYPE_DICTIONARY:
                    if self.ball.has("entanglement_target"): target = self.ball["entanglement_target"]
                elif self.ball.has_method("get_meta") and self.ball.has_meta("entanglement_target"):
                    target = self.ball.get_meta("entanglement_target")
                elif "entanglement_target" in self.ball:
                    target = self.ball.entanglement_target

                if target != null and ent_timer > 0.0:
                    if current_hp > pre_hp:
                        var hp_diff = current_hp - pre_hp
                        if typeof(target) == TYPE_OBJECT:
                            if "hp" in target:
                                var mhp = 100.0
                                if "max_hp" in target: mhp = target.max_hp
                                target.hp = min(target.hp + hp_diff * 0.5, mhp)
                        elif typeof(target) == TYPE_DICTIONARY:
                            if target.has("hp"):
                                var mhp = 100.0
                                if target.has("max_hp"): mhp = target["max_hp"]
                                target["hp"] = min(target["hp"] + hp_diff * 0.5, mhp)

                    if current_speed > pre_speed:
                        var speed_diff = current_speed - pre_speed
                        if typeof(target) == TYPE_OBJECT:
                            if "speed" in target:
                                target.speed += speed_diff * 0.5
                        elif typeof(target) == TYPE_DICTIONARY:
                            if target.has("speed"):
                                target["speed"] += speed_diff * 0.5

                if is_cursed:
                    var post_hp = 100.0
                    var post_speed = 100.0
                    var post_damage = 10.0
                    var post_stamina = 100.0
                    if typeof(self.ball) == TYPE_OBJECT:
                        if "hp" in self.ball: post_hp = self.ball.hp
                        if "speed" in self.ball: post_speed = self.ball.speed
                        if "damage" in self.ball: post_damage = self.ball.damage
                        if "stamina" in self.ball: post_stamina = self.ball.stamina
                    elif typeof(self.ball) == TYPE_DICTIONARY:
                        if self.ball.has("hp"): post_hp = self.ball["hp"]
                        if self.ball.has("speed"): post_speed = self.ball["speed"]
                        if self.ball.has("damage"): post_damage = self.ball["damage"]
                        if self.ball.has("stamina"): post_stamina = self.ball["stamina"]

                    if post_hp > pre_hp:
                        var diff = post_hp - pre_hp
                        if typeof(self.ball) == TYPE_OBJECT: self.ball.hp = pre_hp - diff
                        else: self.ball["hp"] = pre_hp - diff

                    if post_speed > pre_speed:
                        var diff = post_speed - pre_speed
                        if typeof(self.ball) == TYPE_OBJECT:
                            self.ball.speed = pre_speed - diff
                            if "slow_timer" in self.ball: self.ball.slow_timer = 10.0
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("slow_timer", 10.0)
                        else:
                            self.ball["speed"] = pre_speed - diff
                            self.ball["slow_timer"] = 10.0

                    if post_damage > pre_damage:
                        var diff = post_damage - pre_damage
                        if typeof(self.ball) == TYPE_OBJECT: self.ball.damage = pre_damage - diff
                        else: self.ball["damage"] = pre_damage - diff

                    if post_stamina > pre_stamina:
                        var diff = post_stamina - pre_stamina
                        if typeof(self.ball) == TYPE_OBJECT: self.ball.stamina = pre_stamina - diff
                        else: self.ball["stamina"] = pre_stamina - diff
    else:
        _idle(delta)
