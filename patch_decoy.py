import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

search = """            elif skill_name == "deploy_decoy":
                import copy
                active_decoys = [b for b in getattr(self.world, "balls", []) if getattr(b, "is_decoy", False) and getattr(b, "owner_id", None) == self.ball.id and getattr(b, "alive", True)]
                if active_decoys:
                    decoy = active_decoys[0]
                    tx, ty = self.ball.x, self.ball.y
                    self.ball.x, self.ball.y = decoy.x, decoy.y
                    decoy.x, decoy.y = tx, ty
                    decoy.has_swapped = True
                    self.ball.skill_timer = getattr(self.ball, "SKILL_COOLDOWN", 4.0)
                elif hasattr(self.world, "balls"):"""

replace = """            elif skill_name == "deploy_decoy":
                import copy
                active_decoys = [b for b in getattr(self.world, "balls", []) if getattr(b, "is_decoy", False) and getattr(b, "owner_id", None) == self.ball.id and getattr(b, "alive", True)]
                if active_decoys:
                    has_swapped_any = any(getattr(d, "has_swapped", False) for d in active_decoys)
                    if not has_swapped_any:
                        decoy = active_decoys[0]
                        tx, ty = self.ball.x, self.ball.y
                        self.ball.x, self.ball.y = decoy.x, decoy.y
                        decoy.x, decoy.y = tx, ty
                        decoy.has_swapped = True
                        self.ball.skill_timer = getattr(self.ball, "SKILL_COOLDOWN", 4.0)
                    else:
                        for d in active_decoys:
                            d.hp = 0
                            d.alive = False
                        self.ball.skill_timer = getattr(self.ball, "SKILL_COOLDOWN", 4.0)
                elif hasattr(self.world, "balls"):"""

if search in content:
    content = content.replace(search, replace)
    with open("src/ai/action.py", "w") as f:
        f.write(content)
else:
    print("Action.py search string not found!")

# Now action.gd
with open("src/ai/action.gd", "r") as f:
    gd_content = f.read()

gd_search = """        elif skill_name == "deploy_decoy":
            var swapped = false
            if "balls" in self.world:
                for b in self.world.balls:
                    var is_d = false
                    if "is_decoy" in b and b.is_decoy:
                        is_d = true
                    elif b.has_method("get_meta") and b.has_meta("is_decoy") and b.get_meta("is_decoy"):
                        is_d = true

                    if is_d:
                        var owner = -1
                        if "owner_id" in b: owner = b.owner_id
                        elif b.has_method("get_meta") and b.has_meta("owner_id"): owner = b.get_meta("owner_id")

                        var has_swapped = false
                        if "has_swapped" in b: has_swapped = b.has_swapped
                        elif b.has_method("get_meta") and b.has_meta("has_swapped"): has_swapped = b.get_meta("has_swapped")

                        var b_alive = true
                        if "alive" in b: b_alive = b.alive
                        elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                        var self_id = -2
                        if "id" in self.ball: self_id = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id = self.ball.get_meta("id")

                        if owner == self_id and b_alive:
                            var tx = self.ball.x
                            var ty = self.ball.y
                            self.ball.x = b.x
                            self.ball.y = b.y
                            b.x = tx
                            b.y = ty

                            if b.has_method("set_meta"):
                                b.set_meta("has_swapped", true)
                            elif "has_swapped" in b:
                                b.has_swapped = true

                            var cooldown = 4.0
                            if "SKILL_COOLDOWN" in self.ball: cooldown = float(self.ball.SKILL_COOLDOWN)
                            elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = float(self.ball.get_meta("SKILL_COOLDOWN"))

                            if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                            elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)

                            swapped = true
                            break

                if not swapped:
                    for i in range(2):"""

gd_replace = """        elif skill_name == "deploy_decoy":
            var active_decoys = []
            var has_swapped_any = false
            if "balls" in self.world:
                for b in self.world.balls:
                    var is_d = false
                    if "is_decoy" in b and b.is_decoy:
                        is_d = true
                    elif b.has_method("get_meta") and b.has_meta("is_decoy") and b.get_meta("is_decoy"):
                        is_d = true

                    if is_d:
                        var owner = -1
                        if "owner_id" in b: owner = b.owner_id
                        elif b.has_method("get_meta") and b.has_meta("owner_id"): owner = b.get_meta("owner_id")

                        var b_alive = true
                        if "alive" in b: b_alive = b.alive
                        elif b.has_method("get_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")

                        var self_id = -2
                        if "id" in self.ball: self_id = self.ball.id
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("id"): self_id = self.ball.get_meta("id")

                        if owner == self_id and b_alive:
                            active_decoys.append(b)
                            var has_swapped = false
                            if "has_swapped" in b: has_swapped = b.has_swapped
                            elif b.has_method("get_meta") and b.has_meta("has_swapped"): has_swapped = b.get_meta("has_swapped")
                            if has_swapped:
                                has_swapped_any = true

            if active_decoys.size() > 0:
                if not has_swapped_any:
                    var b = active_decoys[0]
                    var tx = self.ball.x
                    var ty = self.ball.y
                    self.ball.x = b.x
                    self.ball.y = b.y
                    b.x = tx
                    b.y = ty

                    if b.has_method("set_meta"):
                        b.set_meta("has_swapped", true)
                    elif "has_swapped" in b:
                        b.has_swapped = true

                    var cooldown = 4.0
                    if "SKILL_COOLDOWN" in self.ball: cooldown = float(self.ball.SKILL_COOLDOWN)
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = float(self.ball.get_meta("SKILL_COOLDOWN"))

                    if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)
                else:
                    for d in active_decoys:
                        if "hp" in d: d.hp = 0.0
                        if "alive" in d: d.alive = false
                        if d.has_method("set_meta"):
                            d.set_meta("hp", 0.0)
                            d.set_meta("alive", false)

                    var cooldown = 4.0
                    if "SKILL_COOLDOWN" in self.ball: cooldown = float(self.ball.SKILL_COOLDOWN)
                    elif self.ball.has_method("get_meta") and self.ball.has_meta("SKILL_COOLDOWN"): cooldown = float(self.ball.get_meta("SKILL_COOLDOWN"))

                    if "skill_timer" in self.ball: self.ball.skill_timer = cooldown
                    elif self.ball.has_method("set_meta"): self.ball.set_meta("skill_timer", cooldown)
            else:
                if true:
                    for i in range(2):"""

if gd_search in gd_content:
    gd_content = gd_content.replace(gd_search, gd_replace)
    with open("src/ai/action.gd", "w") as f:
        f.write(gd_content)
else:
    print("Action.gd search string not found!")

# Now fix the test!
with open("src/ai/test_action_advanced.py", "r") as f:
    test_content = f.read()

test_search = """    # Second swap
    action._use_skill()
    assert ball.x == 100 and ball.y == 100 # It swaps with the first active decoy which is now at 100, 100
    assert ball.skill_timer > 0.0"""

test_replace = """    # Second swap (now Detonation)
    action._use_skill()
    active_decoys = [b for b in world.balls if getattr(b, 'is_decoy', False) and getattr(b, 'alive', True)]
    assert len(active_decoys) == 0 # Decoys are detonated
    assert ball.skill_timer > 0.0"""

if test_search in test_content:
    test_content = test_content.replace(test_search, test_replace)
    with open("src/ai/test_action_advanced.py", "w") as f:
        f.write(test_content)
else:
    print("Test search string not found!")
