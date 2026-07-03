Task: Rainy weather creates temporary mud patches in dirt/sand arenas, slowing down movement speed of all units except those with a 'swamp' or 'water' trait.

1.  **Modify Python AI Game Modes (`src/ai/game_modes.py`)**:
    *   Create a patch script `patch_game_modes.py` to modify `src/ai/game_modes.py`.
    *   Find the exact lines where `mud_pit = Hazard` is spawned under `self.weather == "rain"`. There are two occurrences. Wrap them in a condition:
        ```python
<<<<<<< SEARCH
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn mud pit
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    mud_pit = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=60.0, kind="quicksand", damage=0.0)
                    setattr(mud_pit, 'duration', 15.0)
                    world.arena.hazards.append(mud_pit)
=======
                arena_name = getattr(world.arena, "__class__", type(world.arena)).__name__.lower()
                is_dirt_sand = "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name or getattr(world.arena, "is_sandstorming", False)
                if is_dirt_sand and getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn mud pit
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    mud_pit = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=60.0, kind="quicksand", damage=0.0)
                    setattr(mud_pit, 'duration', 15.0)
                    world.arena.hazards.append(mud_pit)
>>>>>>> REPLACE
        ```
    *   Find the exact lines where `b.speed = b.base_speed * 0.8` is applied under `self.weather == "rain"`. Wrap it in a condition:
        ```python
<<<<<<< SEARCH
            elif self.weather == "rain":
                b.cosmetic = "umbrella"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.5
                b.speed = b.base_speed * 0.8
                b.damage = b.base_damage
=======
            elif self.weather == "rain":
                b.cosmetic = "umbrella"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.5

                # Check for swamp/water traits
                b_type = str(getattr(b, "ball_type", "")).lower()
                traits = getattr(b, "traits", [])
                has_water_trait = "water" in b_type or "swamp" in b_type or any("water" in str(t).lower() or "swamp" in str(t).lower() for t in traits)

                if not has_water_trait:
                    b.speed = b.base_speed * 0.8
                else:
                    b.speed = b.base_speed
                b.damage = b.base_damage
>>>>>>> REPLACE
        ```
    *   Execute the patch script and use `grep` to verify the changes.

2.  **Modify Python AI Actions (`src/ai/action.py`)**:
    *   Create a patch script `patch_action.py` to modify `src/ai/action.py`.
    *   Find the exact block under `elif hazard.kind == "quicksand":` where the debuff is applied.
        ```python
<<<<<<< SEARCH
                            # Occasional slow debuff that lingers
                            if getattr(self.ball, "quicksand_debuff_timer", 0.0) <= 0:
                                if random.random() < 0.1:  # 10% chance per tick to apply debuff
                                    self.ball.quicksand_debuff_timer = 2.0

                            if getattr(self.ball, "quicksand_debuff_timer", 0.0) > 0:
                                self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.3
                                self.ball.quicksand_debuff_timer -= delta

                            self.ball.is_in_quicksand = True
=======
                            # Occasional slow debuff that lingers
                            b_type = str(getattr(self.ball, "ball_type", "")).lower()
                            traits = getattr(self.ball, "traits", [])
                            has_water_trait = "water" in b_type or "swamp" in b_type or any("water" in str(t).lower() or "swamp" in str(t).lower() for t in traits)

                            if not has_water_trait:
                                if getattr(self.ball, "quicksand_debuff_timer", 0.0) <= 0:
                                    if random.random() < 0.1:  # 10% chance per tick to apply debuff
                                        self.ball.quicksand_debuff_timer = 2.0

                                if getattr(self.ball, "quicksand_debuff_timer", 0.0) > 0:
                                    self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.3
                                    self.ball.quicksand_debuff_timer -= delta

                            self.ball.is_in_quicksand = True
>>>>>>> REPLACE
        ```
    *   Execute the patch script and use `grep` to verify the changes.

3.  **Modify GDScript AI Game Modes (`src/ai/game_modes.gd`)**:
    *   Create a patch script `patch_game_modes_gd.py` to modify `src/ai/game_modes.gd`.
    *   Find the exact lines where `mud = Hazard.new` is spawned under `elif self.weather == "rain" or self.weather == "thunderstorm":`. Wrap it in a condition:
        ```python
<<<<<<< SEARCH
                if self.weather == "rain" and randf() < 0.05 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var mud = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 60.0, "quicksand", 0.0)
                    mud.set_meta("duration", 15.0)
                    world.arena.hazards.append(mud)
=======
                var arena_name = "unknown"
                if "arena" in world and world.arena != null:
                    arena_name = str(world.arena.get_script().resource_path).to_lower()
                var is_dirt_sand = false
                if "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name:
                    is_dirt_sand = true
                elif "arena" in world and "is_sandstorming" in world.arena and world.arena.is_sandstorming:
                    is_dirt_sand = true

                if is_dirt_sand and self.weather == "rain" and randf() < 0.05 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var mud = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 60.0, "quicksand", 0.0)
                    mud.set_meta("duration", 15.0)
                    world.arena.hazards.append(mud)
>>>>>>> REPLACE
        ```
    *   Also patch the `b.speed = base_spd * 0.8` effect for rain:
        ```python
<<<<<<< SEARCH
                elif self.weather == "rain":
			if "speed" in b: b.speed = base_spd * 0.8
			if "damage" in b: b.damage = base_dmg
=======
                elif self.weather == "rain":
			var has_wt = false
			var bt = ""
			if "ball_type" in b: bt = str(b.ball_type).to_lower()
			elif b.has_method("get_meta") and b.has_meta("ball_type"): bt = str(b.get_meta("ball_type")).to_lower()
			if "water" in bt or "swamp" in bt: has_wt = true
			var tr = []
			if "traits" in b: tr = b.traits
			elif b.has_method("get_meta") and b.has_meta("traits"): tr = b.get_meta("traits")
			if typeof(tr) == TYPE_ARRAY:
				for t in tr:
					if "water" in str(t).to_lower() or "swamp" in str(t).to_lower():
						has_wt = true
			if "speed" in b:
				if has_wt: b.speed = base_spd
				else: b.speed = base_spd * 0.8
			if "damage" in b: b.damage = base_dmg
>>>>>>> REPLACE
        ```
    *   Execute the patch script and use `grep` to verify the changes.

4.  **Modify GDScript AI Actions (`src/ai/action.gd`)**:
    *   Create a patch script `patch_action_gd.py` to modify `src/ai/action.gd`.
    *   Find the exact lines under `elif hazard.kind == "quicksand":` where `quicksand_debuff_timer` is handled. Wrap the slow logic in `has_wt`:
        ```python
<<<<<<< SEARCH
                        # Occasional slow debuff that lingers
                        var debuff_timer = 0.0
                        if self.ball.has_method("get_meta") and self.ball.has_meta("quicksand_debuff_timer"):
                            debuff_timer = self.ball.get_meta("quicksand_debuff_timer")
                        elif "quicksand_debuff_timer" in self.ball:
                            debuff_timer = self.ball.quicksand_debuff_timer

                        if debuff_timer <= 0.0:
                            if randf() < 0.1:
                                if self.ball.has_method("set_meta"):
                                    self.ball.set_meta("quicksand_debuff_timer", 2.0)
                                else:
                                    self.ball.quicksand_debuff_timer = 2.0

                        if debuff_timer > 0.0:
                            var b_spd = 100.0
                            if "base_speed" in self.ball: b_spd = self.ball.base_speed
                            elif self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"): b_spd = self.ball.get_meta("base_speed")
                            self.ball.speed = b_spd * 0.3
                            debuff_timer -= delta
                            if self.ball.has_method("set_meta"):
                                self.ball.set_meta("quicksand_debuff_timer", debuff_timer)
                            else:
                                self.ball.quicksand_debuff_timer = debuff_timer

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("is_in_quicksand", true)
                        else:
                            self.ball.is_in_quicksand = true
=======
                        var has_wt = false
                        var bt = ""
                        if "ball_type" in self.ball: bt = str(self.ball.ball_type).to_lower()
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("ball_type"): bt = str(self.ball.get_meta("ball_type")).to_lower()
                        if "water" in bt or "swamp" in bt: has_wt = true
                        var tr = []
                        if "traits" in self.ball: tr = self.ball.traits
                        elif self.ball.has_method("get_meta") and self.ball.has_meta("traits"): tr = self.ball.get_meta("traits")
                        if typeof(tr) == TYPE_ARRAY:
                            for t in tr:
                                if "water" in str(t).to_lower() or "swamp" in str(t).to_lower():
                                    has_wt = true

                        # Occasional slow debuff that lingers
                        if not has_wt:
                            var debuff_timer = 0.0
                            if self.ball.has_method("get_meta") and self.ball.has_meta("quicksand_debuff_timer"):
                                debuff_timer = self.ball.get_meta("quicksand_debuff_timer")
                            elif "quicksand_debuff_timer" in self.ball:
                                debuff_timer = self.ball.quicksand_debuff_timer

                            if debuff_timer <= 0.0:
                                if randf() < 0.1:
                                    if self.ball.has_method("set_meta"):
                                        self.ball.set_meta("quicksand_debuff_timer", 2.0)
                                    else:
                                        self.ball.quicksand_debuff_timer = 2.0

                            if debuff_timer > 0.0:
                                var b_spd = 100.0
                                if "base_speed" in self.ball: b_spd = self.ball.base_speed
                                elif self.ball.has_method("get_meta") and self.ball.has_meta("base_speed"): b_spd = self.ball.get_meta("base_speed")
                                self.ball.speed = b_spd * 0.3
                                debuff_timer -= delta
                                if self.ball.has_method("set_meta"):
                                    self.ball.set_meta("quicksand_debuff_timer", debuff_timer)
                                else:
                                    self.ball.quicksand_debuff_timer = debuff_timer

                        if self.ball.has_method("set_meta"):
                            self.ball.set_meta("is_in_quicksand", true)
                        else:
                            self.ball.is_in_quicksand = true
>>>>>>> REPLACE
        ```
    *   Execute the patch script and use `grep` to verify the changes.

5.  **Create JSON Idea Files**:
    *   Generate 2 valid JSON files in `ideas/` with `title` and `description` for new features by executing `cat << 'EOF' > ideas/idea_idea-501_1.json` and `cat << 'EOF' > ideas/idea_idea-501_2.json`.
    *   Verify files with `cat` commands.

6.  **Run Tests**:
    *   Run tests (`PYTHONPATH=src pytest src/`) to verify logic.

7.  **Complete pre-commit steps**:
    *   Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

8.  **Submit Changes**:
    *   Commit changes via `git add .` and `git commit -m "[idea-501] implement rainy mud patches with traits"`. Wait, the branch name is `idea-501`.
    *   Request code review.
