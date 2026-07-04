class_name GameModes

class GameMode:
    var name: String = "Unknown"
    var description: String = "Base game mode"

    func _init() -> void:
        pass

    func setup(world, balls: Array) -> void:
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            var sponsor = ""
            if "sponsor" in b:
                sponsor = b.sponsor
            elif b.has_method("get_meta") and b.has_meta("sponsor"):
                sponsor = b.get_meta("sponsor")

            if sponsor == "aggressor":
                if "max_hp" in b:
                    b.max_hp *= 0.8
                    if "hp" in b: b.hp = min(b.hp, b.max_hp)
            elif sponsor == "juggernaut":
                if "speed" in b: b.speed *= 0.8
                if "base_speed" in b: b.base_speed *= 0.8
                elif b.has_method("set_meta") and b.has_meta("base_speed"):
                    b.set_meta("base_speed", float(b.get_meta("base_speed")) * 0.8)
            elif sponsor == "vampiric":
                if "max_hp" in b:
                    b.max_hp *= 0.9
                    if "hp" in b: b.hp = min(b.hp, b.max_hp)

        var season_num = 1
        if "leaderboard_manager" in world and world.leaderboard_manager != null:
            season_num = world.leaderboard_manager.data.get("current_season", 1)
        elif "profile_manager" in world and world.profile_manager != null:
            if "leaderboard_manager" in world.profile_manager and world.profile_manager.leaderboard_manager != null:
                season_num = world.profile_manager.leaderboard_manager.data.get("current_season", 1)

        var modifiers = {
            1: {"type": "global_speed", "value": 1.2},
            2: {"type": "global_damage", "value": 0.9},
            3: {"type": "global_hp", "value": 1.15},
            4: {"type": "global_cooldown", "value": 0.8}
        }

        var mod_index = ((season_num - 1) % 4) + 1
        var mod = modifiers[mod_index]

        var current_week = int(Time.get_unix_time_from_system() / (7.0 * 24.0 * 3600.0))
        var weekly_mutators = {
            0: {"type": "low_gravity"},
            1: {"type": "double_damage"},
            2: {"type": "high_speed"},
            3: {"type": "vampirism"}
        }
        var week_index = current_week % weekly_mutators.size()
        var week_mod = weekly_mutators[week_index]
        if typeof(world) == TYPE_OBJECT or typeof(world) == TYPE_DICTIONARY:
            if world is Object and world.has_method("set"):
                world.set("weekly_mutator", week_mod["type"])
            elif typeof(world) == TYPE_DICTIONARY:
                world["weekly_mutator"] = week_mod["type"]


        for b in balls:
            if b.ball_type != "spectator":
                if not ("experience" in b): b.experience = 0.0
                if not ("level" in b): b.level = 1
                if mod["type"] == "global_speed":
                    if "base_speed" in b:
                        b.base_speed = b.base_speed * mod["value"]
                    elif b.has_method("get_meta") and b.has_meta("base_speed"):
                        b.set_meta("base_speed", b.get_meta("base_speed") * mod["value"])
                    if "speed" in b:
                        b.speed = b.speed * mod["value"]
                elif mod["type"] == "global_damage":
                    if "base_damage" in b:
                        b.base_damage = b.base_damage * mod["value"]
                    elif b.has_method("get_meta") and b.has_meta("base_damage"):
                        b.set_meta("base_damage", b.get_meta("base_damage") * mod["value"])
                    if "damage" in b:
                        b.damage = b.damage * mod["value"]
                elif mod["type"] == "global_hp":
                    if "max_hp" in b:
                        b.max_hp = b.max_hp * mod["value"]
                    elif b.has_method("get_meta") and b.has_meta("max_hp"):
                        b.set_meta("max_hp", b.get_meta("max_hp") * mod["value"])
                    if "hp" in b:
                        if "max_hp" in b:
                            b.hp = b.max_hp
                        elif b.has_method("get_meta") and b.has_meta("max_hp"):
                            b.hp = b.get_meta("max_hp")
                elif mod["type"] == "global_cooldown":
                    if "cooldown_multiplier" in b:
                        b.cooldown_multiplier = b.cooldown_multiplier * mod["value"]

                    elif b.has_method("get_meta") and b.has_meta("cooldown_multiplier"):
                        b.set_meta("cooldown_multiplier", b.get_meta("cooldown_multiplier") * mod["value"])
                    elif b.has_method("set_meta"):
                        b.set_meta("cooldown_multiplier", mod["value"])

                if week_mod["type"] == "double_damage":
                    if "base_damage" in b:
                        b.base_damage = b.base_damage * 2.0
                    elif b.has_method("get_meta") and b.has_meta("base_damage"):
                        b.set_meta("base_damage", b.get_meta("base_damage") * 2.0)
                    if "damage" in b:
                        b.damage = b.damage * 2.0
                elif week_mod["type"] == "high_speed":
                    if "base_speed" in b:
                        b.base_speed = b.base_speed * 1.5
                    elif b.has_method("get_meta") and b.has_meta("base_speed"):
                        b.set_meta("base_speed", b.get_meta("base_speed") * 1.5)
                    if "speed" in b:
                        b.speed = b.speed * 1.5
                elif week_mod["type"] == "vampirism":
                    if "lifesteal" in b:
                        b.lifesteal = b.lifesteal + 0.5
                    elif b.has_method("get_meta"):
                        b.set_meta("lifesteal", b.get_meta("lifesteal", 0.0) + 0.5)
                elif week_mod["type"] == "low_gravity":
                    if "mass" in b:
                        b.mass = b.mass * 0.5
                    elif b.has_method("get_meta"):
                        b.set_meta("mass", b.get_meta("mass", 1.0) * 0.5)


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        pass


    func check_winner(world, balls: Array):
        return null


class DraftRoyaleMode extends GameMode:
    var phase: String = "drafting"
    var draft_state: String = "ban"
    var turn_index: int = 0
    var banned_types: Array = []
    var available_types: Array = [
        "time_mage", "assassin", "berserker", "bomber", "brawler", "chaos", "conjurer", "druid",
        "elementalist", "guardian", "healer", "juggernaut", "king", "mage", "mimic",
        "monk", "necromancer", "ninja", "paladin", "phantom", "ranger", "rogue", "drone",
        "scout", "sniper", "swarm", "tank", "templar", "trickster", "vampire",
        "warlock", "warrior"
    ]
    var team_rosters: Dictionary = {"Team A": [], "Team B": []}
    var teams: Array = ["Team A", "Team B"]
    var max_bans: int = 2
    var picks_per_team: int = 5
    var timer: float = 0.0

    func _init() -> void:
        name = "Draft Royale"
        description = "Before the match, teams take turns picking and banning ball types to create synergies and counter opponents."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        phase = "drafting"
        draft_state = "ban"
        turn_index = 0
        banned_types = []
        team_rosters = {"Team A": [], "Team B": []}
        timer = 0.0

        for b in balls:
            if b.has_method("set_meta"):
                var orig_type = "tank"
                if "ball_type" in b:
                    orig_type = b.ball_type
                b.set_meta("original_type", orig_type)

                var base_spd = 100.0
                if "speed" in b:
                    base_spd = float(b.speed)
                b.set_meta("base_speed", base_spd)

                var base_dmg = 10.0
                if "damage" in b:
                    base_dmg = float(b.damage)
                b.set_meta("base_damage", base_dmg)

            b.ball_type = "spectator"
            b.team = "spectator"
            if "speed" in b:
                b.speed = 0.0

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if phase == "drafting":
            timer += delta
            if timer > 0.5:
                timer = 0.0
                var current_team = teams[turn_index % teams.size()]

                if draft_state == "ban":
                    if banned_types.size() < max_bans * teams.size():
                        var choices = []
                        for t in available_types:
                            if not banned_types.has(t):
                                choices.append(t)
                        if choices.size() > 0:
                            var ban = choices[randi() % choices.size()]
                            banned_types.append(ban)
                        turn_index += 1

                        if banned_types.size() >= max_bans * teams.size():
                            draft_state = "pick"
                            turn_index = 0

                elif draft_state == "pick":
                    var team_a_picks = team_rosters["Team A"].size()
                    var team_b_picks = team_rosters["Team B"].size()

                    if team_a_picks < picks_per_team or team_b_picks < picks_per_team:
                        if team_rosters[current_team].size() < picks_per_team:
                            var picked_by_a = team_rosters["Team A"]
                            var picked_by_b = team_rosters["Team B"]
                            var choices = []
                            for t in available_types:
                                if not banned_types.has(t) and not picked_by_a.has(t) and not picked_by_b.has(t):
                                    choices.append(t)
                            if choices.size() == 0:
                                for t in available_types:
                                    if not banned_types.has(t):
                                        choices.append(t)
                            if choices.size() > 0:
                                var pick = choices[randi() % choices.size()]
                                team_rosters[current_team].append(pick)
                        turn_index += 1
                    else:
                        phase = "combat"
                        start_combat(world, balls)

    func start_combat(world, balls: Array) -> void:
        var team_a_balls = []
        var team_b_balls = []

        for b in balls:
            var is_orig_spec = false
            if b.has_method("get_meta") and b.has_meta("original_type"):
                if b.get_meta("original_type") == "spectator":
                    is_orig_spec = true
            elif b.ball_type == "spectator":
                pass # can't check original type easily without meta

            if not is_orig_spec:
                if team_a_balls.size() < picks_per_team:
                    team_a_balls.append(b)
                elif team_b_balls.size() < picks_per_team:
                    team_b_balls.append(b)

        for i in range(team_a_balls.size()):
            var b = team_a_balls[i]
            if i < team_rosters["Team A"].size():
                b.ball_type = team_rosters["Team A"][i]
                b.team = "Team A"
                b.alive = true
                if b.has_method("get_meta"):
                    if b.has_meta("base_speed") and "speed" in b:
                        b.speed = b.get_meta("base_speed")
                    if b.has_meta("base_damage") and "damage" in b:
                        b.damage = b.get_meta("base_damage")

        for i in range(team_b_balls.size()):
            var b = team_b_balls[i]
            if i < team_rosters["Team B"].size():
                b.ball_type = team_rosters["Team B"][i]
                b.team = "Team B"
                b.alive = true
                if b.has_method("get_meta"):
                    if b.has_meta("base_speed") and "speed" in b:
                        b.speed = b.get_meta("base_speed")
                    if b.has_meta("base_damage") and "damage" in b:
                        b.damage = b.get_meta("base_damage")

        for b in balls:
            if b.team == "spectator" or b.ball_type == "spectator":
                b.ball_type = "spectator"
                b.alive = false

    func check_winner(world, balls: Array):
        if phase == "drafting":
            return null

        var alive_a = 0
        var alive_b = 0

        for b in balls:
            if b.alive:
                if b.team == "Team A":
                    alive_a += 1
                elif b.team == "Team B":
                    alive_b += 1

        if alive_a > 0 and alive_b == 0:
            return "Team A"
        elif alive_b > 0 and alive_a == 0:
            return "Team B"
        elif alive_a == 0 and alive_b == 0:
            return "Draw"

        return null

class BattleRoyaleMode extends GameMode:
    var dark_phase_timer: float = 0.0
    var is_dark_phase: bool = false
    var weather_timer: float = 0.0
    var weather: String = "clear"
    var supply_drop_timer: float = 0.0
    var rng = RandomNumberGenerator.new()

    func _init() -> void:
        name = "Battle Royale"
        description = "Last man standing. Everyone for themselves. Includes periodic dark phases."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = false
            else:
                b.team = b.ball_type
                var base_perc = 250.0
                if "perception_radius" in b:
                    base_perc = float(b.perception_radius)
                if b.has_method("set_meta"):
                    b.set_meta("base_perception_radius", base_perc)


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        dark_phase_timer += delta

        supply_drop_timer += delta
        if supply_drop_timer >= 15.0:
            supply_drop_timer = 0.0
            if "boosters" in world:
                var arena_width = 1000
                var arena_height = 1000
                if "arena" in world and world.arena:
                    if "width" in world.arena: arena_width = world.arena.width
                    if "height" in world.arena: arena_height = world.arena.height

                rng.randomize()
                var booster_kinds = ["speed_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "shadow_booster", "weather_scanner_item", "aura_booster", "emp_immunity_booster"]
                var chosen_kind = booster_kinds[rng.randi() % booster_kinds.size()]
                var b_id = 9000 + world.boosters.size() + (rng.randi() % 1000)
                var b_x = rng.randf_range(100, arena_width - 100)
                var b_y = rng.randf_range(100, arena_height - 100)

                var new_booster = {
                    "id": b_id,
                    "x": b_x,
                    "y": b_y,
                    "kind": chosen_kind,
                    "radius": 15.0,
                    "ball_type": "booster",
                    "active": true
                }
                world.boosters.append(new_booster)

                if "arena" in world and world.arena and "hazards" in world.arena:
                    var h = {
                        "id": b_id,
                        "x": b_x,
                        "y": b_y,
                        "radius": 15.0,
                        "kind": chosen_kind,
                        "damage": 0.0,
                        "active": true
                    }
                    world.arena.hazards.append(h)

                if "add_event" in world and world.has_method("add_event"):
                    world.add_event("supply_drop", {"message": "A " + chosen_kind + " supply drop has appeared!"})

        # Weather logic
        if not "weather_timer" in self:
            self.weather_timer = 0.0
            self.weather = "clear"

        var controller = null
        for b in balls:
            var c_timer = 0.0
            if "weather_control_timer" in b: c_timer = b.weather_control_timer
            elif b.has_method("get_meta") and b.has_meta("weather_control_timer"): c_timer = b.get_meta("weather_control_timer")

            var is_alive = false
            if "alive" in b: is_alive = b.alive
            elif b.has_method("get_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

            if is_alive and c_timer > 0:
                controller = b
                break

        if controller != null:
            self.weather_timer = 0.0
            var ctype = "default"
            if "ball_type" in controller: ctype = controller.ball_type
            elif controller.has_method("get_meta") and controller.has_meta("ball_type"): ctype = controller.get_meta("ball_type")

            var pref = "clear"
            if ctype in ["elementalist"]: pref = "thunderstorm"
            elif ctype in ["druid", "healer"]: pref = "rain"
            elif ctype in ["rogue", "assassin", "stealth"]: pref = "fog"
            elif ctype in ["mage", "conjurer"]: pref = "snow"
            elif ctype in ["speed", "scout"]: pref = "wind"
            elif ctype in ["tank", "brawler"]: pref = "heatwave"
            elif ctype in ["swarm"]: pref = "sandstorm"
            else: pref = "thunderstorm"

            var old_weather = self.weather
            if old_weather != pref:
                self.weather = pref
                if world != null and world.has_method("add_event"):
                    world.add_event("weather_change", {"weather": self.weather})
                if self.weather == "wind":
                    if has_method("set_meta"):
                        set_meta("wind_dx", (randf() * 100.0) - 50.0)
                        set_meta("wind_dy", (randf() * 100.0) - 50.0)
        else:
            self.weather_timer += delta
            if self.weather_timer > 15.0:
                self.weather_timer = 0.0
                var weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm", "heatwave", "blizzard", "magnetic_storm"]
                var old_weather = self.weather
                self.weather = weathers[randi() % weathers.size()]
                if old_weather != self.weather and world != null and world.has_method("add_event"):
                    world.add_event("weather_change", {"weather": self.weather})
                if self.weather == "wind":
                    if has_method("set_meta"):
                        set_meta("wind_dx", (randf() * 100.0) - 50.0)
                        set_meta("wind_dy", (randf() * 100.0) - 50.0)

        if world != null and "arena" in world and world.arena != null:
            if self.weather == "fog" or self.weather in ["snow", "blizzard"]:
                world.arena.is_foggy = true
            else:
                world.arena.is_foggy = false
            if self.weather == "rain" or self.weather == "thunderstorm":
                world.arena.is_raining = true
            else:
                world.arena.is_raining = false
            if self.weather == "sandstorm":
                world.arena.is_sandstorming = true
            else:
                world.arena.is_sandstorming = false
            if self.weather == "heatwave":
                world.arena.is_heatwave = true
            else:
                world.arena.is_heatwave = false
            if self.weather in ["snow", "blizzard"]:
                world.arena.is_snowing = true
            else:
                world.arena.is_snowing = false

            if not "hazards" in world.arena:
                world.arena.hazards = []

            if self.weather == "wind":
                if randf() < 0.1 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var tornado = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 40.0, "tornado", 20.0)
                    tornado.set_meta("duration", 5.0)
                    tornado.set_meta("vx", randf_range(-100.0, 100.0))
                    tornado.set_meta("vy", randf_range(-100.0, 100.0))
                    world.arena.hazards.append(tornado)
            elif self.weather in ["snow", "blizzard"]:
                if randf() < 0.05 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var ice = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 50.0, "ice_patch", 0.0)
                    ice.set_meta("duration", 10.0)
                    ice.set_meta("vx", randf_range(-20.0, 20.0))
                    ice.set_meta("vy", randf_range(-20.0, 20.0))
                    world.arena.hazards.append(ice)
            elif self.weather == "rain" or self.weather == "thunderstorm":
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
                var chance = 0.05
                if self.weather == "thunderstorm":
                    chance = 0.2
                if randf() < chance * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var lightning = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 30.0, "lightning_strike", 50.0)
                    lightning.set_meta("duration", 1.0)
                    world.arena.hazards.append(lightning)
                if self.weather == "thunderstorm" and randf() < 0.05 * delta:
                    var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
                    var x = randf_range(100.0, world.arena.width - 100.0)
                    var y = randf_range(100.0, world.arena.height - 100.0)
                    var warning = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 40.0, "tornado_warning", 0.0)
                    warning.set_meta("duration", 3.0)
                    if world.has_method("add_event"):
                        world.add_event("audio_event", {"sound": "siren_warning", "volume": 1.0, "x": x, "y": y})
                    world.arena.hazards.append(warning)

        for b in balls:
            if b.alive and b.ball_type != "spectator":
                var base_spd = 100.0
                if "base_speed" in b:
                    base_spd = b.base_speed
                elif b.has_method("has_meta") and b.has_meta("base_speed"):
                    base_spd = b.get_meta("base_speed")
                elif "speed" in b:
                    base_spd = b.speed

                var base_dmg = 10.0
                if "base_damage" in b:
                    base_dmg = b.base_damage
                elif b.has_method("has_meta") and b.has_meta("base_damage"):
                    base_dmg = b.get_meta("base_damage")
                elif "damage" in b:
                    base_dmg = b.damage
                var t = ""
                if "ball_type" in b: t = b.ball_type
                var is_fire = t in ["mage", "bomber", "chaos"]
                var is_water = t in ["elementalist", "healer", "trickster"]
                var is_air = t in ["ninja", "scout", "phantom"]
                var is_earth = t in ["tank", "druid", "juggernaut"]

                if self.weather == "clear":
                    if "speed" in b: b.speed = base_spd
                    if "damage" in b:
                        if is_fire: b.damage = base_dmg * 1.5
                        else: b.damage = base_dmg
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 1.0)
                        b.set_meta("steering_mult", 1.0)
                        b.set_meta("attack_accuracy", 1.0)
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
			if "hp" in b:
				var m_hp = 100.0
				if "max_hp" in b: m_hp = b.max_hp
				b.hp = min(m_hp, b.hp + 5.0 * delta)
			var sk_r = ""
			if "SKILL" in b:
				sk_r = b.SKILL
			elif b.has_method("has_meta") and b.has_meta("SKILL"):
				sk_r = b.get_meta("SKILL")
			if sk_r == "fireball":
				if "hp" in b:
					b.hp -= 2.0 * delta
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 1.5)
                        b.set_meta("steering_mult", 0.5)
                        b.set_meta("attack_accuracy", 0.8)
                    if "vx" in b and "vy" in b:
                        b.x += b.vx * delta * 0.5
                        b.y += b.vy * delta * 0.5
                    if is_water and "hp" in b:
                        var m = 100.0
                        if "max_hp" in b: m = b.max_hp
                        elif b.has_method("has_meta") and b.has_meta("max_hp"): m = b.get_meta("max_hp")
                        b.hp = min(m, b.hp + 5.0 * delta)
                elif self.weather == "fog":
                    if "speed" in b: b.speed = base_spd * 0.8
                    if "damage" in b: b.damage = base_dmg * 0.9
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 1.0)
                        b.set_meta("steering_mult", 1.0)
                elif self.weather in ["snow", "blizzard"]:
			if "speed" in b: b.speed = base_spd * 0.5
			if "damage" in b: b.damage = base_dmg * 1.2
			var sk_s = ""
			if "SKILL" in b:
				sk_s = b.SKILL
			elif b.has_method("has_meta") and b.has_meta("SKILL"):
				sk_s = b.get_meta("SKILL")
			if sk_s == "iceball" or sk_s == "elemental_burst":
				if "speed" in b: b.speed = base_spd * 1.2
				if "damage" in b: b.damage = base_dmg * 1.5
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 1.0)
                        b.set_meta("steering_mult", 1.0)
                    if b.has_method("set_meta") and b.has_method("get_meta"):
                        var stacks = 0.0
                        if b.has_meta("chill_stacks"):
                            stacks = b.get_meta("chill_stacks")
                        stacks += delta
                        if stacks >= 3.0:
                            stacks = 0.0
                            b.set_meta("stutter_timer", 1.0)
                        b.set_meta("chill_stacks", stacks)
                    if b.has_method("set_meta"):
                        b.set_meta("attack_accuracy", 0.9)
                elif self.weather == "wind":
                    if "speed" in b:
                        if is_air: b.speed = base_spd * 1.5
                        else: b.speed = base_spd
                    if "damage" in b: b.damage = base_dmg
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 1.0)
                        b.set_meta("steering_mult", 1.0)
                    var wind_dx = 0.0
                    var wind_dy = 0.0
                    if has_method("has_meta") and has_meta("wind_dx"):
                        wind_dx = get_meta("wind_dx")
                    if has_method("has_meta") and has_meta("wind_dy"):
                        wind_dy = get_meta("wind_dy")
                    b.x += wind_dx * delta
                    b.y += wind_dy * delta
                elif self.weather == "thunderstorm":
                    if "speed" in b: b.speed = base_spd * 1.1
                    if "damage" in b: b.damage = base_dmg * 1.5
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 1.0)
                        b.set_meta("steering_mult", 1.0)
                elif self.weather == "sandstorm":
                    if "speed" in b: b.speed = base_spd * 0.7
                    if "damage" in b: b.damage = base_dmg
                    if b.has_method("set_meta"):
                        b.set_meta("dash_range_mult", 0.5)
                        b.set_meta("steering_mult", 0.5)
                        b.set_meta("attack_accuracy", 0.5)
                        var sand_timer = 0.0
                        if b.has_meta("sandstorm_timer"):
                            sand_timer = b.get_meta("sandstorm_timer")
                        sand_timer += delta
                        if sand_timer >= 1.0:
                            sand_timer = 0.0
                            if "hp" in b and not is_earth:
                                b.hp -= 1.0
                        b.set_meta("sandstorm_timer", sand_timer)
                    if randf() < 0.05 * delta and not is_earth:
                        if "hp" in b:
                            b.hp -= 20.0

        if randf() < 0.05 * delta:
            if "arena" in world and "hazards" in world.arena:
                var hx = 100.0 + randf() * (1000.0 - 200.0)
                var hy = 100.0 + randf() * (1000.0 - 200.0)
                if "width" in world.arena: hx = 100.0 + randf() * (world.arena.width - 200.0)
                if "height" in world.arena: hy = 100.0 + randf() * (world.arena.height - 200.0)
                var HazardType = load("res://src/arena/procedural_arena.gd").Hazard
                if HazardType != null:
                    var vb = HazardType.new()
                    vb.id = world.arena.hazards.size() + int(randf() * 9000.0) + 1000
                    vb.x = hx
                    vb.y = hy
                    vb.radius = 30.0
                    vb.kind = "vision_booster"
                    vb.damage = 0.0
                    vb.set_meta("duration", 15.0)
                    world.arena.hazards.append(vb)

        # Dark phase cycle: 20s normal, 10s dark
        if not is_dark_phase and dark_phase_timer >= 20.0:
            is_dark_phase = true
            dark_phase_timer = 0.0

            # Apply dark phase
            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var current_perc = 250.0
                    if "perception_radius" in b:
                        current_perc = float(b.perception_radius)
                    if b.has_method("set_meta"):
                        b.set_meta("base_perception_radius", current_perc)

                    var vb_timer = 0.0
                    if "vision_booster_timer" in b: vb_timer = b.vision_booster_timer
                    elif b.has_method("get_meta") and b.has_meta("vision_booster_timer"): vb_timer = b.get_meta("vision_booster_timer")

                    if vb_timer > 0.0:
                        b.perception_radius = current_perc
                    else:
                        if b.ball_type == "scout":
                            b.perception_radius = 120.0
                        else:
                            b.perception_radius = 60.0
        elif is_dark_phase and dark_phase_timer >= 10.0:
            is_dark_phase = false
            dark_phase_timer = 0.0

            # Restore normal phase
            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var base_perc = 250.0
                    if b.has_method("get_meta") and b.has_meta("base_perception_radius"):
                        base_perc = b.get_meta("base_perception_radius")
                    b.perception_radius = base_perc

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            _award_skill_points()
            return "Draw"

        var teams_alive = {}
        for b in alive:
            if b.has_method("get") or "team" in b:
                teams_alive[b.team] = true
            else:
                teams_alive[b.ball_type] = true

        if teams_alive.size() == 1:
            _award_skill_points()
            return teams_alive.keys()[0]

        if alive.size() == 1:
            _award_skill_points()
            return alive[0].ball_type

        return null

    func _award_skill_points() -> void:
        var pm = ProfileManager.new()
        pm.add_skill_points(10)

class TeamDeathmatchMode extends GameMode:
    func _init() -> void:
        name = "Team Deathmatch"
        description = "Two teams fight until one is eliminated."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        var mid = valid_balls.size() / 2
        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i < mid:
                b.team = "Red"
            else:
                b.team = "Blue"

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            teams_alive[b.team] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        return null

class ZombieInfectionMode extends GameMode:
    func _init() -> void:
        name = "Zombie Infection"
        description = "One zombie infects others. Survivors win if time runs out."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        if valid_balls.size() > 0:
            var zombie = valid_balls[randi() % valid_balls.size()]
            for b in valid_balls:
                if b == zombie:
                    b.team = "Zombie"
                    b.ball_type = "berserker"
                else:
                    b.team = "Survivor"


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        var survivors = []
        for b in balls:
            if ("team" in b) and b.team == "Survivor":
                survivors.append(b)

        for survivor in survivors:
            if not survivor.alive:
                survivor.team = "Zombie"
                survivor.ball_type = "berserker"
                if "max_hp" in survivor:
                    survivor.hp = survivor.max_hp
                else:
                    survivor.hp = 100
                survivor.alive = true

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var zombies = 0
        var survivors = 0
        for b in alive:
            if b.team == "Zombie":
                zombies += 1
            elif b.team == "Survivor":
                survivors += 1

        if survivors == 0:
            return "Zombies"
        elif zombies == 0:
            return "Survivors"

        return null

class BossFightMode extends GameMode:
    func _init() -> void:
        name = "Boss Fight"
        description = "One giant boss ball faces off against a team of weaker hunters."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        if valid_balls.size() > 0:
            var boss = valid_balls[0]
            boss.team = "Boss"
            if "max_hp" in boss:
                boss.max_hp *= 10.0
                boss.hp = boss.max_hp
            if "damage" in boss:
                boss.damage *= 3.0

            var arena_width = 1000
            var arena_height = 1000
            if world != null and "arena" in world and world.arena != null:
                if "width" in world.arena:
                    arena_width = world.arena.width
                if "height" in world.arena:
                    arena_height = world.arena.height

            if "x" in boss and "y" in boss:
                boss.x = arena_width / 2.0
                boss.y = arena_height / 2.0

            if "radius" in boss:
                boss.radius *= 3.0
            elif boss.has_meta("radius"):
                boss.set_meta("radius", boss.get_meta("radius") * 3.0)
            else:
                boss.set_meta("radius", 30.0)

            if "base_speed" in boss:
                boss.base_speed *= 0.6
            elif boss.has_meta("base_speed"):
                boss.set_meta("base_speed", boss.get_meta("base_speed") * 0.6)

            if "mass" in boss:
                boss.mass *= 5.0
            elif boss.has_meta("mass"):
                boss.set_meta("mass", boss.get_meta("mass") * 5.0)

            for i in range(1, valid_balls.size()):
                valid_balls[i].team = "Hunters"
                if "max_hp" in valid_balls[i]:
                    valid_balls[i].max_hp *= 0.8
                    valid_balls[i].hp = valid_balls[i].max_hp

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        super.tick(world, balls, delta)
        for b in balls:
            if "team" in b and b.team == "Boss" and b.alive:
                if "hp" in b and "max_hp" in b:
                    b.hp = min(b.hp + 5.0 * delta, b.max_hp)

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var boss_alive = false
        var hunters_alive = false

        for b in alive:
            if b.team == "Boss":
                boss_alive = true
            elif b.team == "Hunters":
                hunters_alive = true

        if not boss_alive:
            return "Hunters"
        if not hunters_alive:
            return "Boss"

        return null

class VIPDefenseMode extends GameMode:
    func _init() -> void:
        name = "VIP Defense"
        description = "Protect the VIP. If the VIP dies, the attackers win."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        var mid = valid_balls.size() / 2
        var defenders = []

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i < mid:
                b.team = "Defenders"
                defenders.append(b)
            else:
                b.team = "Attackers"

        if defenders.size() > 0:
            var vip = defenders[0]
            vip.team = "VIP"
            vip.ball_type = "king"

    func check_winner(world, balls: Array):
        var vip_alive = false
        for b in balls:
            if b.alive and ("team" in b) and b.team == "VIP":
                vip_alive = true
                break

        if not vip_alive:
            return "Attackers"

        var attackers_alive = false
        for b in balls:
            if b.alive and ("team" in b) and b.team == "Attackers" and b.ball_type != "spectator":
                attackers_alive = true
                break

        if not attackers_alive:
            return "Defenders"

        return null

class SurvivalMode extends GameMode:
    func _init() -> void:
        name = "Survival"
        description = "Players team up to survive against waves of enemies."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        var players_count = min(4, valid_balls.size())

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i < players_count:
                b.team = "Players"
            else:
                b.team = "Enemies"

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var players_alive = false
        var enemies_alive = false

        for b in alive:
            if b.team == "Players":
                players_alive = true
            elif b.team == "Enemies":
                enemies_alive = true

        if not players_alive:
            return "Enemies"
        if not enemies_alive:
            return "Players"

        return null




class DualPayloadMode extends GameMode:
	var payload_red
	var payload_blue

	func _init() -> void:
		name = "Dual Payload"
		description = "Two payloads move towards the center, the team that destroys the enemy payload first wins."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		var valid_balls = []
		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				if b.get("ball_type", "") != "spectator":
					valid_balls.append(b)
			else:
				if b.get("ball_type") != "spectator":
					valid_balls.append(b)

		var mid = valid_balls.size() / 2
		var red_team = []
		var blue_team = []

		for i in range(valid_balls.size()):
			var b = valid_balls[i]
			if i < mid:
				if typeof(b) == TYPE_DICTIONARY:
					b["team"] = "Red"
				else:
					b.set("team", "Red")
				red_team.append(b)
			else:
				if typeof(b) == TYPE_DICTIONARY:
					b["team"] = "Blue"
				else:
					b.set("team", "Blue")
				blue_team.append(b)

		var arena_width = 1000.0
		var arena_height = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
			else:
				arena_width = world.arena.get("width")
				arena_height = world.arena.get("height")

		if red_team.size() > 0:
			payload_red = red_team[0]
			if typeof(payload_red) == TYPE_DICTIONARY:
				payload_red["ball_type"] = "payload"
				payload_red["is_payload"] = true
				payload_red["speed"] = 10.0
				payload_red["base_speed"] = 10.0
				payload_red["damage"] = 0.0
				payload_red["base_damage"] = 0.0
				payload_red["max_hp"] = payload_red.get("max_hp", 100.0) * 5.0
				payload_red["hp"] = payload_red["max_hp"]
				payload_red["x"] = 100.0
				payload_red["y"] = arena_height / 2.0
			else:
				payload_red.set("ball_type", "payload")
				payload_red.set("is_payload", true)
				payload_red.set("speed", 10.0)
				payload_red.set("base_speed", 10.0)
				payload_red.set("damage", 0.0)
				payload_red.set("base_damage", 0.0)
				payload_red.set("max_hp", payload_red.get("max_hp") * 5.0 if payload_red.get("max_hp") else 500.0)
				payload_red.set("hp", payload_red.get("max_hp"))
				payload_red.set("x", 100.0)
				payload_red.set("y", arena_height / 2.0)

		if blue_team.size() > 0:
			payload_blue = blue_team[0]
			if typeof(payload_blue) == TYPE_DICTIONARY:
				payload_blue["ball_type"] = "payload"
				payload_blue["is_payload"] = true
				payload_blue["speed"] = 10.0
				payload_blue["base_speed"] = 10.0
				payload_blue["damage"] = 0.0
				payload_blue["base_damage"] = 0.0
				payload_blue["max_hp"] = payload_blue.get("max_hp", 100.0) * 5.0
				payload_blue["hp"] = payload_blue["max_hp"]
				payload_blue["x"] = arena_width - 100.0
				payload_blue["y"] = arena_height / 2.0
			else:
				payload_blue.set("ball_type", "payload")
				payload_blue.set("is_payload", true)
				payload_blue.set("speed", 10.0)
				payload_blue.set("base_speed", 10.0)
				payload_blue.set("damage", 0.0)
				payload_blue.set("base_damage", 0.0)
				payload_blue.set("max_hp", payload_blue.get("max_hp") * 5.0 if payload_blue.get("max_hp") else 500.0)
				payload_blue.set("hp", payload_blue.get("max_hp"))
				payload_blue.set("x", arena_width - 100.0)
				payload_blue.set("y", arena_height / 2.0)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		for b in balls:
			var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.get("alive")
			if not alive:
				if not world.get_meta("dead_balls").has(b):
					if typeof(b) == TYPE_DICTIONARY:
						b["time_since_death"] = 0.0
					else:
						b.set("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if typeof(b) == TYPE_DICTIONARY:
						b["time_since_death"] = b.get("time_since_death", 0.0) + delta
					else:
						b.set("time_since_death", b.get("time_since_death") + delta if b.get("time_since_death") else delta)

		var arena_width = 1000.0
		var arena_height = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
			else:
				arena_width = world.arena.get("width")
				arena_height = world.arena.get("height")

		var center_x = arena_width / 2.0
		var center_y = arena_height / 2.0

		if payload_red:
			var red_alive = payload_red.get("alive", false) if typeof(payload_red) == TYPE_DICTIONARY else payload_red.get("alive")
			if red_alive:
				var red_x = payload_red.get("x", 0.0) if typeof(payload_red) == TYPE_DICTIONARY else payload_red.get("x")
				var red_y = payload_red.get("y", 0.0) if typeof(payload_red) == TYPE_DICTIONARY else payload_red.get("y")
				var dx = center_x - red_x
				var dy = center_y - red_y
				var dist = sqrt(dx*dx + dy*dy)
				if dist > 5.0:
					var speed = payload_red.get("speed", 10.0) if typeof(payload_red) == TYPE_DICTIONARY else payload_red.get("speed")
					if typeof(payload_red) == TYPE_DICTIONARY:
						payload_red["x"] += (dx / dist) * speed * delta
						payload_red["y"] += (dy / dist) * speed * delta
					else:
						payload_red.set("x", red_x + (dx / dist) * speed * delta)
						payload_red.set("y", red_y + (dy / dist) * speed * delta)

		if payload_blue:
			var blue_alive = payload_blue.get("alive", false) if typeof(payload_blue) == TYPE_DICTIONARY else payload_blue.get("alive")
			if blue_alive:
				var blue_x = payload_blue.get("x", 0.0) if typeof(payload_blue) == TYPE_DICTIONARY else payload_blue.get("x")
				var blue_y = payload_blue.get("y", 0.0) if typeof(payload_blue) == TYPE_DICTIONARY else payload_blue.get("y")
				var dx = center_x - blue_x
				var dy = center_y - blue_y
				var dist = sqrt(dx*dx + dy*dy)
				if dist > 5.0:
					var speed = payload_blue.get("speed", 10.0) if typeof(payload_blue) == TYPE_DICTIONARY else payload_blue.get("speed")
					if typeof(payload_blue) == TYPE_DICTIONARY:
						payload_blue["x"] += (dx / dist) * speed * delta
						payload_blue["y"] += (dy / dist) * speed * delta
					else:
						payload_blue.set("x", blue_x + (dx / dist) * speed * delta)
						payload_blue.set("y", blue_y + (dy / dist) * speed * delta)

	func check_winner(world, balls: Array):
		var red_alive = false
		if payload_red:
			red_alive = payload_red.get("alive", false) if typeof(payload_red) == TYPE_DICTIONARY else payload_red.get("alive")
		var blue_alive = false
		if payload_blue:
			blue_alive = payload_blue.get("alive", false) if typeof(payload_blue) == TYPE_DICTIONARY else payload_blue.get("alive")

		if not red_alive and blue_alive:
			return "Blue"
		elif not blue_alive and red_alive:
			return "Red"
		elif not red_alive and not blue_alive:
			return "Draw"

		return null


class EscortMode extends GameMode:
    var payload
    var goal_x: float = 900.0
    var goal_y: float = 500.0
    var timer: float = 180.0

    func _init() -> void:
        name = "Escort Mode"
        description = "One team defends an invulnerable payload moving towards a goal. The other tries to delay it until time runs out."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        var valid_balls = []
        for b in balls:
            if typeof(b) == TYPE_DICTIONARY:
                if b.get("ball_type", "") != "spectator":
                    valid_balls.append(b)
            else:
                if b.ball_type != "spectator":
                    valid_balls.append(b)

        var mid = valid_balls.size() / 2
        var defenders = []
        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if typeof(b) == TYPE_DICTIONARY:
                b["team"] = "Defenders" if i < mid else "Attackers"
                if i < mid: defenders.append(b)
            else:
                b.team = "Defenders" if i < mid else "Attackers"
                if i < mid: defenders.append(b)

        if defenders.size() > 0:
            payload = defenders[0]
            if typeof(payload) == TYPE_DICTIONARY:
                payload["ball_type"] = "payload"
                payload["is_invulnerable"] = true
                payload["speed"] = 0.5
                payload["damage"] = 0.0
                payload["x"] = 100.0
                payload["y"] = 500.0
            else:
                payload.ball_type = "payload"
                payload.is_invulnerable = true
                payload.speed = 0.5
                payload.damage = 0.0
                payload.x = 100.0
                payload.y = 500.0

    var pulse_timer: float = 0.0

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if timer > 0.0:
            timer -= delta

        pulse_timer += delta
        if pulse_timer >= 5.0:
            pulse_timer = 0.0
            if payload != null:
                var px = payload.get("x") if typeof(payload) == TYPE_DICTIONARY else payload.x
                var py = payload.get("y") if typeof(payload) == TYPE_DICTIONARY else payload.y

                for b in balls:
                    if typeof(b) == TYPE_DICTIONARY and b.has("id") and typeof(payload) == TYPE_DICTIONARY and payload.has("id") and b["id"] == payload["id"]:
                        continue
                    if typeof(b) == TYPE_OBJECT and typeof(payload) == TYPE_OBJECT and b == payload:
                        continue
                    var balive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.get("alive")
                    if not balive:
                        continue
                    var btype = b.get("ball_type") if typeof(b) == TYPE_DICTIONARY else b.get("ball_type")
                    if btype == "spectator":
                        continue

                    var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("x")
                    var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.get("y")

                    var bdx = bx - px
                    var bdy = by - py
                    var bdist = sqrt(bdx*bdx + bdy*bdy)

                    if bdist <= 300.0:
                        var bteam = b.get("team", "") if typeof(b) == TYPE_DICTIONARY else b.get("team")
                        if bteam == "Defenders":
                            var bmax_hp = b.get("max_hp") if b.get("max_hp") != null else 100.0 if typeof(b) == TYPE_DICTIONARY else b.get("max_hp")
                            var bhp = b.get("hp", 100.0) if typeof(b) == TYPE_DICTIONARY else b.get("hp")
                            var new_hp = min(bmax_hp, bhp + 20.0)
                            if typeof(b) == TYPE_DICTIONARY:
                                b["hp"] = new_hp
                            else:
                                b.set("hp", new_hp)
                        elif bteam == "Attackers":
                            var bhp = b.get("hp", 100.0) if typeof(b) == TYPE_DICTIONARY else b.get("hp")
                            var new_hp = max(0.0, bhp - 20.0)
                            if typeof(b) == TYPE_DICTIONARY:
                                b["hp"] = new_hp
                                if new_hp <= 0:
                                    b["alive"] = false
                            else:
                                b.set("hp", new_hp)
                                if new_hp <= 0:
                                    b.set("alive", false)

        if payload != null:
            var is_alive = payload.get("alive", false) if typeof(payload) == TYPE_DICTIONARY else payload.alive
            if is_alive:
                var px = payload.get("x", 0) if typeof(payload) == TYPE_DICTIONARY else payload.x
                var py = payload.get("y", 0) if typeof(payload) == TYPE_DICTIONARY else payload.y
                var spd = payload.get("speed", 0) if typeof(payload) == TYPE_DICTIONARY else payload.speed
                var dx = goal_x - px
                var dy = goal_y - py
                var dist = sqrt(dx * dx + dy * dy)
                if dist > 0:
                    if typeof(payload) == TYPE_DICTIONARY:
                        payload["x"] += (dx / dist) * spd
                        payload["y"] += (dy / dist) * spd
                    else:
                        payload.x += (dx / dist) * spd
                        payload.y += (dy / dist) * spd

    func check_winner(world, balls: Array):
        if payload == null:
            return null

        var px = payload.get("x", 0) if typeof(payload) == TYPE_DICTIONARY else payload.x
        var py = payload.get("y", 0) if typeof(payload) == TYPE_DICTIONARY else payload.y
        var dx = goal_x - px
        var dy = goal_y - py
        var dist = sqrt(dx * dx + dy * dy)

        if timer <= 0.0:
            return "Attackers"

        if dist < 10.0:
            return "Defenders"

        return null

        var dx = goal_x - payload["x"]
        var dy = goal_y - payload["y"]
        var dist = sqrt(dx * dx + dy * dy)

        var is_dead = false
        if payload.has("hp") and payload["hp"] <= 0:
            is_dead = true
        if payload.has("alive") and not payload["alive"]:
            is_dead = true

        if is_dead:
            payload["alive"] = false
            return "Attackers"

        if dist < 10.0:
            return "Defenders"

        return null

class CaptureTheFlagMode extends GameMode:
    func _init() -> void:
        name = "Capture The Flag"
        description = "Teams try to steal the enemy's flag and return it to their base."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        var mid = valid_balls.size() / 2
        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i < mid:
                b.team = "Red"
            else:
                b.team = "Blue"

        if "boosters" in world:
            var red_flag = {"id": "red_flag", "x": 100, "y": 100, "is_flag": true, "team": "Red", "carrier": null, "ball_type": "booster"}
            var blue_flag = {"id": "blue_flag", "x": 900, "y": 900, "is_flag": true, "team": "Blue", "carrier": null, "ball_type": "booster"}
            world.boosters.append(red_flag)
            world.boosters.append(blue_flag)
            if not "flags" in world:
                world.flags = {"Red": red_flag, "Blue": blue_flag}

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            if b.has_method("get") or "team" in b:
                teams_alive[b.team] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        if "scores" in world:
            if world.scores.has("Red") and world.scores["Red"] >= 3:
                return "Red"
            if world.scores.has("Blue") and world.scores["Blue"] >= 3:
                return "Blue"

        return null


class EvolutionarySimulationMode extends GameMode:
    func _init() -> void:
        name = "Evolutionary Simulation"
        description = "Only Neural Balls compete. After the match, a genetic algorithm breeds top performers."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for i in range(balls.size()):
            var b = balls[i]
            if b.ball_type != "spectator":
                b.ball_type = "neural"
                b.team = "Neural_" + str(i)

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        if alive.size() == 1:
            if "team" in alive[0]:
                return alive[0].team
            return alive[0].ball_type

        return null


class VampireRoyaleMode extends GameMode:
    var tick_timer = 0.0

    func _init() -> void:
        name = "Vampire Royale"
        description = "All balls slowly lose HP over time but regain HP when dealing damage. Last one standing wins."


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        tick_timer += delta
        if tick_timer >= 1.0:
            tick_timer = 0.0
            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    if "hp" in b:
                        b.hp = max(0, b.hp - 5.0)
                        if b.hp <= 0:
                            b.alive = false

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            if "team" in b:
                teams_alive[b.team] = true
            else:
                teams_alive[b.ball_type] = true

        if teams_alive.size() == 1:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return alive[0].ball_type

        return null


class KingOfTheHillMode extends GameMode:
    var tick_timer = 0.0
    var game_time = 0.0

    func _init() -> void:
        name = "King of the Hill"
        description = "Control a central shrinking zone. First to 100 points wins."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        game_time = 0.0
        for b in balls:
            if b.ball_type != "spectator":
                b.set_meta("score", 0)


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        game_time += delta
        tick_timer += delta
        if tick_timer >= 0.5:
            tick_timer = 0.0

            var arena_width = 1000.0
            var arena_height = 1000.0
            if world != null and "arena" in world and world.arena != null:
                if "width" in world.arena:
                    arena_width = float(world.arena.width)
                if "height" in world.arena:
                    arena_height = float(world.arena.height)

            var center_x = arena_width / 2.0
            var center_y = arena_height / 2.0

            var max_radius = min(arena_width, arena_height) * 0.5
            var min_radius = min(arena_width, arena_height) * 0.05
            var zone_radius = max(min_radius, max_radius - game_time * 5.0)

            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var dx = b.x - center_x
                    var dy = b.y - center_y
                    var dist_sq = dx * dx + dy * dy

                    if dist_sq <= zone_radius * zone_radius:
                        var s = 0
                        if b.has_meta("score"):
                            s = b.get_meta("score")
                        b.set_meta("score", s + 1)

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        for b in balls:
            if b.ball_type != "spectator":
                var score = 0
                if b.has_meta("score"):
                    score = b.get_meta("score")
                if score >= 100:
                    if "team" in b:
                        return b.team
                    return b.ball_type

        return null


class BlackHoleMode extends GameMode:
    var black_hole_radius = 50.0

    func _init() -> void:
        name = "Black Hole"
        description = "The entire arena is slowly sucked into a massive black hole in the center. Avoid the center!"


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        var arena_width = 1000.0
        var arena_height = 1000.0
        if world != null and "arena" in world and world.arena != null:
            if "width" in world.arena:
                arena_width = world.arena.width
            if "height" in world.arena:
                arena_height = world.arena.height

        var center_x = arena_width / 2.0
        var center_y = arena_height / 2.0

        # The black hole slowly grows over time
        black_hole_radius += 2.0 * delta

        for b in balls:
            if b.alive and b.ball_type != "spectator":
                var dx = center_x - b.x
                var dy = center_y - b.y
                var dist = sqrt(dx * dx + dy * dy)

                if dist < black_hole_radius:
                    # Instantly die if inside the event horizon
                    if "hp" in b:
                        b.hp = 0
                    b.alive = false
                elif dist > 0:
                    # Pull towards center
                    var pull_strength = 20000.0 / (dist * dist)

                    var radius_multiplier = black_hole_radius / 50.0
                    pull_strength *= radius_multiplier

                    # Cap max pull to avoid crazy speeds
                    pull_strength = min(pull_strength, 150.0 * radius_multiplier)

                    b.x += (dx / dist) * pull_strength * delta
                    b.y += (dy / dist) * pull_strength * delta

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            if "team" in b:
                teams_alive[b.team] = true
            else:
                teams_alive[b.ball_type] = true

        if teams_alive.size() == 1:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return alive[0].ball_type

        return null


class WeatherChaosMode extends GameMode:
	var weather: String = "clear"
	var weather_timer: float = 0.0

	func _init() -> void:
		set_meta("next_weather", "clear")
		set_meta("weather_warning_issued", false)
		name = "Weather Chaos"
		description = "Weather conditions change throughout the match, affecting stats."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		for b in balls:
			if b.ball_type != "spectator":
				b.team = b.ball_type
				if not b.has_meta("base_perception_radius"):
					var pr = 250.0
					if "perception_radius" in b:
						pr = b.perception_radius
					b.set_meta("base_perception_radius", pr)
				if not b.has_meta("base_speed"):
					if "speed" in b:
						b.set_meta("base_speed", b.speed)
					else:
						b.set_meta("base_speed", 100.0)
				if not b.has_meta("base_damage"):
					if "damage" in b:
						b.set_meta("base_damage", b.damage)
					else:
						b.set_meta("base_damage", 10.0)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		var controller = null
		for b in balls:
			var c_timer = 0.0
			if "weather_control_timer" in b: c_timer = b.weather_control_timer
			elif b.has_method("get_meta") and b.has_meta("weather_control_timer"): c_timer = b.get_meta("weather_control_timer")

			var is_alive = false
			if "alive" in b: is_alive = b.alive
			elif b.has_method("get_meta") and b.has_meta("alive"): is_alive = b.get_meta("alive")

			if is_alive and c_timer > 0:
				controller = b
				break

		if controller != null:
			weather_timer = 0.0
			var ctype = "default"
			if "ball_type" in controller: ctype = controller.ball_type
			elif controller.has_method("get_meta") and controller.has_meta("ball_type"): ctype = controller.get_meta("ball_type")

			var pref = "clear"
			if ctype in ["elementalist"]: pref = "thunderstorm"
			elif ctype in ["druid", "healer"]: pref = "rain"
			elif ctype in ["rogue", "assassin", "stealth"]: pref = "fog"
			elif ctype in ["mage", "conjurer"]: pref = "snow"
			elif ctype in ["speed", "scout"]: pref = "wind"
			elif ctype in ["tank", "brawler"]: pref = "heatwave"
			elif ctype in ["swarm"]: pref = "sandstorm"
			else: pref = "thunderstorm"

			var old_weather = weather
			if old_weather != pref:
				weather = pref
				if world != null and world.has_method("add_event"):
					world.add_event("weather_change", {"weather": weather})
				if weather == "wind":
					if has_method("set_meta"):
						set_meta("wind_dx", (randf() * 100.0) - 50.0)
						set_meta("wind_dy", (randf() * 100.0) - 50.0)
		else:
			weather_timer += delta

			var warning_threshold = 7.0 # 3s warning
			var warning_issued = false
			if has_meta("weather_warning_issued"):
				warning_issued = get_meta("weather_warning_issued")
			if weather_timer >= warning_threshold and not warning_issued:
				if world != null and "arena" in world and "hazards" in world.arena:
					var scanners = []
					for h in world.arena.hazards:
						var k = h.kind if "kind" in h else ""
						var a = h.active if "active" in h else true
						if k == "weather_scanner" and a:
							scanners.append(h)
					if scanners.size() > 0:
						var next_w = "unknown"
						if has_meta("next_weather"): next_w = get_meta("next_weather")
						if world != null and world.has_method("add_event"):
							world.add_event("weather_warning", {"type": "weather_warning", "message": "Scanner warns: " + next_w.to_upper() + " incoming in 3s!"})
						set_meta("weather_warning_issued", true)

			if weather_timer > 10.0:
				weather_timer = 0.0
				var weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm", "heatwave", "blizzard", "magnetic_storm"]
				var old_weather = weather
				if not has_meta("next_weather"):
					set_meta("next_weather", weathers[randi() % weathers.size()])
				weather = get_meta("next_weather")
				set_meta("next_weather", weathers[randi() % weathers.size()])
				set_meta("weather_warning_issued", false)
				if old_weather != weather and world != null and world.has_method("add_event"):
					world.add_event("weather_change", {"weather": weather})
				if weather == "wind":
					if has_method("set_meta"):
						set_meta("wind_dx", (randf() * 100.0) - 50.0)
						set_meta("wind_dy", (randf() * 100.0) - 50.0)

		if world != null and "arena" in world:
			if weather == "fog" or weather in ["snow", "blizzard"]:
				world.arena.is_foggy = true
			else:
				world.arena.is_foggy = false
			if weather == "rain":
				world.arena.is_raining = true
			else:
				world.arena.is_raining = false
			if weather == "sandstorm":
				world.arena.is_sandstorming = true
			else:
				world.arena.is_sandstorming = false
			if weather == "heatwave":
				world.arena.is_heatwave = true
			else:
				world.arena.is_heatwave = false
			if weather in ["snow", "blizzard"]:
				world.arena.is_snowing = true
			else:
				world.arena.is_snowing = false
			if weather == "wind":
				var wx = 0.0
				var wy = 0.0
				if has_method("has_meta") and has_meta("wind_dx"):
					wx = get_meta("wind_dx")
				if has_method("has_meta") and has_meta("wind_dy"):
					wy = get_meta("wind_dy")
				world.arena.wind_dx = wx
				world.arena.wind_dy = wy
			else:
				world.arena.wind_dx = 0.0
				world.arena.wind_dy = 0.0

			if not "hazards" in world.arena:
				world.arena.hazards = []

			if weather == "sandstorm":
				if randf() < 0.05 * delta:
					var BallClass = load("res://src/ai/ball_types_swarm.gd")
					if BallClass:
						var minion = BallClass.new("sand_minion_" + str(randi() % 9000 + 1000), randf_range(100.0, world.arena.width - 100.0), randf_range(100.0, world.arena.height - 100.0))
						minion.team = "Sandstorm"
						minion.ball_type = "sand_minion"
						minion.hp = 30.0
						if not "max_hp" in minion:
							minion.set_meta("max_hp", 30.0)
						else:
							minion.max_hp = 30.0
						minion.speed = 120.0
						minion.damage = 10.0
						if not "balls" in world: world.balls = []
						world.balls.append(minion)
						if world.has_method("add_event"):
							world.add_event("minion_spawn", {"type": "minion_spawn", "message": "A Sand Minion emerged from the storm!"})

			if weather == "fog":
				if randf() < 0.02 * delta:
					var BallClass = load("res://src/ai/ball_types_phantom.gd")
					if BallClass:
						var minion = BallClass.new("fog_phantom_" + str(randi() % 9000 + 1000), randf_range(100.0, world.arena.width - 100.0), randf_range(100.0, world.arena.height - 100.0))
						minion.team = "Fog"
						minion.ball_type = "fog_minion"
						minion.hp = 40.0
						if not "max_hp" in minion:
							minion.set_meta("max_hp", 40.0)
						else:
							minion.max_hp = 40.0
						minion.speed = 90.0
						minion.damage = 15.0
						if not "balls" in world: world.balls = []
						world.balls.append(minion)
						if world.has_method("add_event"):
							world.add_event("minion_spawn", {"type": "minion_spawn", "message": "A Fog Phantom materialized!"})

			if weather == "wind":
				if randf() < 0.1 * delta:
					var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
					var x = randf_range(100.0, world.arena.width - 100.0)
					var y = randf_range(100.0, world.arena.height - 100.0)
					var tornado = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 40.0, "tornado", 20.0)
					tornado.set_meta("duration", 5.0)
					tornado.set_meta("vx", randf_range(-100.0, 100.0))
					tornado.set_meta("vy", randf_range(-100.0, 100.0))
					world.arena.hazards.append(tornado)
			elif weather == "blizzard":
				if randf() < 0.1 * delta:
					var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
					var x = randf_range(100.0, world.arena.width - 100.0)
					var y = randf_range(100.0, world.arena.height - 100.0)
					var ice = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 80.0, "ice_patch", 0.0)
					ice.set_meta("duration", 10.0)
					ice.set_meta("vx", randf_range(-50.0, 50.0))
					ice.set_meta("vy", randf_range(-50.0, 50.0))
					world.arena.hazards.append(ice)
			elif weather in ["snow", "blizzard"]:
				if typeof(b) == TYPE_OBJECT: b.set("cosmetic", "snow_goggles")
				elif typeof(b) == TYPE_DICTIONARY: b["cosmetic"] = "snow_goggles"
				var b_type = ""
				if typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b["ball_type"]
				elif typeof(b) == TYPE_OBJECT and "ball_type" in b: b_type = b.ball_type
				if b_type == "snow_yeti":
					if "speed" in b: b.speed = base_spd * 1.5
					if "damage" in b: b.damage = base_dmg * 1.5
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
					if "attack_accuracy" in b: b.attack_accuracy = 1.0
				else:
					if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.6
					elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.6
					else: b.perception_radius = 250.0 * 0.6
					if "speed" in b: b.speed = base_spd * 0.5
					if "damage" in b: b.damage = base_dmg * 1.2
					var sk_s = ""
					if "SKILL" in b: sk_s = b.SKILL
					elif b.has_method("has_meta") and b.has_meta("SKILL"): sk_s = b.get_meta("SKILL")
					if sk_s == "iceball" or sk_s == "elemental_burst":
						if "speed" in b: b.speed = base_spd * 1.2
						if "damage" in b: b.damage = base_dmg * 1.5
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
					if b.has_method("set_meta") and b.has_method("get_meta"):
						var stacks = 0.0
						if b.has_meta("chill_stacks"): stacks = b.get_meta("chill_stacks")
						stacks += delta
						if stacks >= 3.0:
							stacks = 0.0
							b.set_meta("stutter_timer", 1.0)
						b.set_meta("chill_stacks", stacks)
					if "attack_accuracy" in b: b.attack_accuracy = 0.9
				elif weather == "wind":
					if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.55
					elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.55
					else: b.perception_radius = 250.0 * 0.55
					if "speed" in b:
						if is_air: b.speed = base_spd * 1.5
						else: b.speed = base_spd
					if "damage" in b: b.damage = base_dmg
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
				elif weather == "thunderstorm":
					if typeof(b) == TYPE_OBJECT: b.set("cosmetic", "lightning_rod")
					elif typeof(b) == TYPE_DICTIONARY: b["cosmetic"] = "lightning_rod"
					if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.8
					elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.8
					else: b.perception_radius = 250.0 * 0.8
					if "speed" in b: b.speed = base_spd * 1.1
					if "damage" in b: b.damage = base_dmg * 1.5
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
				elif weather == "sandstorm":
					if typeof(b) == TYPE_OBJECT: b.set("cosmetic", "dust_mask")
					elif typeof(b) == TYPE_DICTIONARY: b["cosmetic"] = "dust_mask"
					var b_type = ""
					if typeof(b) == TYPE_DICTIONARY and b.has("ball_type"): b_type = b["ball_type"]
					elif typeof(b) == TYPE_OBJECT and "ball_type" in b: b_type = b.ball_type
					if b_type == "sand_elemental":
						if "speed" in b: b.speed = base_spd * 1.2
						if "damage" in b: b.damage = base_dmg
						if b.has_method("set_meta"):
							b.set_meta("dash_range_mult", 1.0)
							b.set_meta("steering_mult", 1.0)
						if "attack_accuracy" in b: b.attack_accuracy = 1.0
					else:
						if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
						elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
						else: b.perception_radius = 250.0 * 0.3
						if "speed" in b: b.speed = base_spd * 0.7
						if "damage" in b: b.damage = base_dmg
						if b.has_method("set_meta"):
							b.set_meta("dash_range_mult", 0.5)
							b.set_meta("steering_mult", 0.5)
						var bt = b_type
						if bt in ["trickster", "phantom", "mimic"]:
							if b.has_method("set_meta") and b.has_method("get_meta"):
								var mtimer = 0.0
								if b.has_meta("mirage_timer"): mtimer = b.get_meta("mirage_timer")
								mtimer += delta
								if mtimer >= 5.0: mtimer = 0.0
								b.set_meta("mirage_timer", mtimer)
						if b.has_method("set_meta") and b.has_method("get_meta"):
							var sand_timer = 0.0
							if b.has_meta("sandstorm_timer"): sand_timer = b.get_meta("sandstorm_timer")
							sand_timer += delta
							if sand_timer >= 1.0:
								sand_timer = 0.0
								if "hp" in b: b.hp -= 1.0
							b.set_meta("sandstorm_timer", sand_timer)
						if randf() < 0.05 * delta:
							if "hp" in b: b.hp -= 20.0
						if "attack_accuracy" in b: b.attack_accuracy = 0.5
				elif weather == "heatwave":
					if typeof(b) == TYPE_OBJECT: b.set("cosmetic", "sunglasses")
					elif typeof(b) == TYPE_DICTIONARY: b["cosmetic"] = "sunglasses"
					if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.7
					elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.7
					else: b.perception_radius = 250.0 * 0.7
					if "speed" in b: b.speed = base_spd * 0.9
					if "damage" in b: b.damage = base_dmg
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			if b.alive and b.ball_type != "spectator":
				alive.append(b)

		if alive.size() == 0:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return "Draw"

		var teams_alive = {}
		for b in alive:
			var t = b.ball_type
			if "team" in b:
				t = b.team
			teams_alive[t] = true

		if teams_alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return teams_alive.keys()[0]

		return null

class DominationMode extends GameMode:
    var points = []

    func _init() -> void:
        name = "Domination"
        description = "Capture points to gain global buffs for your team."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        var mid = balls.size() / 2
        for i in range(balls.size()):
            var b = balls[i]
            if b.ball_type != "spectator":
                if i < mid:
                    b.team = "Red"
                else:
                    b.team = "Blue"

        points = []
        points.append({"id": "A", "x": 300, "y": 500, "radius": 150.0, "capture_progress": 0.0, "owner": null, "held_time": 0.0, "is_danger_zone": false})
        points.append({"id": "B", "x": 500, "y": 500, "radius": 150.0, "capture_progress": 0.0, "owner": null, "held_time": 0.0, "is_danger_zone": false})
        points.append({"id": "C", "x": 700, "y": 500, "radius": 150.0, "capture_progress": 0.0, "owner": null, "held_time": 0.0, "is_danger_zone": false})


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        for pt in points:
            var red_count = 0
            var blue_count = 0
            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var dist_sq = (b.x - pt.x) * (b.x - pt.x) + (b.y - pt.y) * (b.y - pt.y)
                    if dist_sq <= pt.radius * pt.radius:
                        if b.get("team") == "Red":
                            red_count += 1
                        elif b.get("team") == "Blue":
                            blue_count += 1

            if red_count > blue_count:
                pt.capture_progress += 10.0 * delta
                for b in balls:
                    var b_type = null
                    if "ball_type" in b: b_type = b.ball_type
                    if ("alive" in b) and b.alive and b_type != "spectator":
                        var team = ""
                        if "team" in b: team = b.team
                        if team == "Red":
                            var dist_sq = (b.x - pt.x)*(b.x - pt.x) + (b.y - pt.y)*(b.y - pt.y)
                            if dist_sq <= pt.radius*pt.radius:
                                if not ("experience" in b): b.experience = 0.0
                                if not ("level" in b): b.level = 1
                                b.experience += 5.0 * delta
                                while b.experience >= 100 * b.level:
                                    b.experience -= 100 * b.level
                                    b.level += 1
                                    var rng = randf()
                                    var stat = "max_hp"
                                    if rng > 0.66: stat = "damage"
                                    elif rng > 0.33: stat = "speed"

                                    if stat == "max_hp":
                                        if "max_hp" in b: b.max_hp *= 1.1
                                        else: b.max_hp = 110.0
                                        if "hp" in b: b.hp += b.max_hp * 0.1
                                        else: b.hp = b.max_hp
                                        if b.hp > b.max_hp: b.hp = b.max_hp
                                    elif stat == "damage":
                                        if "damage" in b: b.damage *= 1.1
                                        else: b.damage = 11.0
                                        if "base_damage" in b: b.base_damage *= 1.1
                                    elif stat == "speed":
                                        if "speed" in b: b.speed *= 1.1
                                        else: b.speed = 110.0
                                        if "base_speed" in b: b.base_speed *= 1.1

            elif blue_count > red_count:
                pt.capture_progress -= 10.0 * delta
                for b in balls:
                    var b_type = null
                    if "ball_type" in b: b_type = b.ball_type
                    if ("alive" in b) and b.alive and b_type != "spectator":
                        var team = ""
                        if "team" in b: team = b.team
                        if team == "Blue":
                            var dist_sq = (b.x - pt.x)*(b.x - pt.x) + (b.y - pt.y)*(b.y - pt.y)
                            if dist_sq <= pt.radius*pt.radius:
                                if not ("experience" in b): b.experience = 0.0
                                if not ("level" in b): b.level = 1
                                b.experience += 5.0 * delta
                                while b.experience >= 100 * b.level:
                                    b.experience -= 100 * b.level
                                    b.level += 1
                                    var rng = randf()
                                    var stat = "max_hp"
                                    if rng > 0.66: stat = "damage"
                                    elif rng > 0.33: stat = "speed"

                                    if stat == "max_hp":
                                        if "max_hp" in b: b.max_hp *= 1.1
                                        else: b.max_hp = 110.0
                                        if "hp" in b: b.hp += b.max_hp * 0.1
                                        else: b.hp = b.max_hp
                                        if b.hp > b.max_hp: b.hp = b.max_hp
                                    elif stat == "damage":
                                        if "damage" in b: b.damage *= 1.1
                                        else: b.damage = 11.0
                                        if "base_damage" in b: b.base_damage *= 1.1
                                    elif stat == "speed":
                                        if "speed" in b: b.speed *= 1.1
                                        else: b.speed = 110.0
                                        if "base_speed" in b: b.base_speed *= 1.1

            pt.capture_progress = clamp(pt.capture_progress, -100.0, 100.0)

            var new_owner = null
            if pt.capture_progress >= 100.0:
                new_owner = "Red"
            elif pt.capture_progress <= -100.0:
                new_owner = "Blue"

            if new_owner != null and new_owner != pt.owner:
                pt.owner = new_owner
                if pt.has("held_time"):
                    pt.held_time = 0.0
                if pt.has("is_danger_zone"):
                    pt.is_danger_zone = false
                # Apply global buff
                for b in balls:
                    if b.alive and b.get("team") == new_owner:
                        # Give buff
                        if b.get("damage") != null:
                            b.damage += 5.0
                        if b.get("max_hp") != null:
                            b.max_hp += 20.0
                            b.hp += 20.0

            if pt.get("owner") != null:
                if pt.has("held_time"):
                    pt.held_time += delta
                    if pt.held_time >= 15.0:
                        pt.is_danger_zone = true

                if pt.get("is_danger_zone", false):
                    for b in balls:
                        if b.alive and b.ball_type != "spectator":
                            var dist_sq = (b.x - pt.x)*(b.x - pt.x) + (b.y - pt.y)*(b.y - pt.y)
                            if dist_sq <= pt.radius * pt.radius:
                                if b.get("hp") != null:
                                    b.hp -= 20.0 * delta
                                    if b.hp <= 0:
                                        b.alive = false
                                        if b.has_method("set"):
                                            b.killer = "Danger Zone"


    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var t = b.get("team")
            if t == null: t = b.ball_type
            teams_alive[t] = true

        if teams_alive.size() == 1:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if has_method("_award_skill_points"): call("_award_skill_points")
            return alive[0].ball_type

        return null


class MovingZoneMode extends GameMode:
    var tick_timer = 0.0
    var zone_x = 500.0
    var zone_y = 500.0
    var zone_radius = 150.0
    var zone_target_x = 500.0
    var zone_target_y = 500.0

    func _init() -> void:
        name = "Moving Zone"
        description = "Maintain position in the moving zone to score points for your team."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if b.ball_type != "spectator":
                b.set_meta("score", 0)
        var arena_width = 1000.0
        var arena_height = 1000.0
        if world != null and "arena" in world and world.arena != null:
            if "width" in world.arena: arena_width = float(world.arena.width)
            if "height" in world.arena: arena_height = float(world.arena.height)
        zone_x = arena_width / 2.0
        zone_y = arena_height / 2.0
        zone_target_x = zone_x
        zone_target_y = zone_y


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        tick_timer += delta
        var arena_width = 1000.0
        var arena_height = 1000.0
        if world != null and "arena" in world and world.arena != null:
            if "width" in world.arena: arena_width = float(world.arena.width)
            if "height" in world.arena: arena_height = float(world.arena.height)

        var dx = zone_target_x - zone_x
        var dy = zone_target_y - zone_y
        var dist = sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            zone_x += (dx / dist) * 20.0 * delta
            zone_y += (dy / dist) * 20.0 * delta
        else:
            zone_target_x = zone_radius + randf() * (arena_width - 2.0 * zone_radius)
            zone_target_y = zone_radius + randf() * (arena_height - 2.0 * zone_radius)

        if tick_timer >= 0.5:
            tick_timer = 0.0
            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var bdx = b.x - zone_x
                    var bdy = b.y - zone_y
                    if bdx*bdx + bdy*bdy <= zone_radius * zone_radius:
                        var s = 0
                        if b.has_meta("score"): s = b.get_meta("score")
                        b.set_meta("score", s + 1)

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        for b in balls:
            if b.ball_type != "spectator":
                var score = 0
                if b.has_meta("score"): score = b.get_meta("score")
                if score >= 100:
                    if "team" in b: return b.team
                    return b.ball_type

        return null



class ReverseEventMode extends GameMode:
	var event_timer: float = 0.0
	var event_active: bool = false
	var event_duration: float = 0.0

	func _init() -> void:
		name = "Reverse Event"
		description = "A random event reverses movement logic for 10 seconds."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not event_active:
			event_timer += delta

		if not event_active and event_timer > 20.0:
			if randf() < 0.1:  # 10% chance every 20 seconds to trigger
				event_active = true
				event_duration = 10.0
				event_timer = 0.0
				print("REVERSE EVENT TRIGGERED!")
			else:
				event_timer = 0.0

		if event_active:
			event_duration -= delta
			if event_duration <= 0:
				event_active = false
				event_timer = 0.0
				print("REVERSE EVENT ENDED!")

			# Apply reverse logic directly to balls
			for b in balls:
				if b.alive:
					var vx = 0.0
					var vy = 0.0
					if "vx" in b: vx = b.vx
					if "vy" in b: vy = b.vy
					b.x -= vx * delta * 2 # Reverse the velocity applied in action.gd
					b.y -= vy * delta * 2


class MemoryTrapsMode extends GameMode:
	var traps = []

	func _init() -> void:
		name = "Memory Traps"
		description = "The arena is littered with invisible traps. Memorize their locations!"

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		var arena_width = 1000.0
		var arena_height = 1000.0
		if world != null and "arena" in world and world.arena != null:
			if "width" in world.arena: arena_width = float(world.arena.width)
			if "height" in world.arena: arena_height = float(world.arena.height)

		traps.clear()
		for i in range(50):
			var x = randf() * (arena_width - 100.0) + 50.0
			var y = randf() * (arena_height - 100.0) + 50.0
			traps.append({"x": x, "y": y, "radius": 40.0, "cooldowns": {}})

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			if not b.alive:
				if not world.get_meta("dead_balls").has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if b.has_method("get_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

			if not b.alive or b.ball_type == "spectator":
				continue

			var b_id = str(b.get_instance_id()) if b.has_method("get_instance_id") else str(b)

			for trap in traps:
				if trap.cooldowns.has(b_id):
					trap.cooldowns[b_id] -= delta
					if trap.cooldowns[b_id] <= 0:
						trap.cooldowns.erase(b_id)

				if not trap.cooldowns.has(b_id):
					var dx = b.x - trap.x
					var dy = b.y - trap.y
					var dist_sq = dx*dx + dy*dy
					if dist_sq < trap.radius * trap.radius:
						if "hp" in b:
							b.hp -= 20.0
							trap.cooldowns[b_id] = 1.0
							if b.hp <= 0:
								b.alive = false

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			if b.alive and b.ball_type != "spectator":
				alive.append(b)

		if alive.size() == 0:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return "Draw"

		var teams_alive = {}
		for b in alive:
			var t = b.get("team")
			if t == null: t = b.ball_type
			teams_alive[t] = true

		if teams_alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return teams_alive.keys()[0]

		if alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return alive[0].ball_type

		return null

class CustomMatchMode extends GameMode:

	var mutators = []
	var mutators_active = false

	func _init() -> void:
		name = "Custom Match"
		description = "Custom match with mutator options if Prestige Level >= 5."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		var pm = null
		if world != null and "profile_manager" in world:
			pm = world.profile_manager

		var mutators_unlocked = false
		if pm != null and pm.has_method("are_mutators_unlocked"):
			mutators_unlocked = pm.are_mutators_unlocked()
		elif pm != null and "data" in pm:
			if pm.data.get("prestige_level", 0) >= 5 or pm.data.get("prestige_upgrades", {}).get("mutator_unlocked", 0) > 0:
				mutators_unlocked = true

		mutators_active = mutators_unlocked and mutators.size() > 0

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			if not b.alive:
				if not world.get_meta("dead_balls").has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if b.has_method("get_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)




		if mutators_active:
			var trigger_reroll = false
			if mutators.has("boss"):
				if not has_meta("boss_mutator_timer"):
					set_meta("boss_mutator_timer", 0.0)

				var active_boss = null
				for b in balls:
					if b.has_meta("_is_boss_mutator") and b.get_meta("_is_boss_mutator"):
						active_boss = b
						break

				if active_boss != null:
					var b_dur = active_boss.get_meta("_boss_mutator_duration") - delta
					active_boss.set_meta("_boss_mutator_duration", b_dur)
					if b_dur <= 0 or not active_boss.alive:
						active_boss.set_meta("_is_boss_mutator", false)
						if active_boss.has_meta("_original_radius"):
							if "radius" in active_boss:
								active_boss.radius = active_boss.get_meta("_original_radius")
							else:
								active_boss.set_meta("radius", active_boss.get_meta("_original_radius"))
						if active_boss.has_meta("_original_max_hp"):
							active_boss.max_hp = active_boss.get_meta("_original_max_hp")
						if active_boss.has_meta("_original_damage"):
							active_boss.damage = active_boss.get_meta("_original_damage")
						if active_boss.has_meta("_original_base_damage"):
							active_boss.base_damage = active_boss.get_meta("_original_base_damage")
						if active_boss.has_meta("_original_team"):
							active_boss.team = active_boss.get_meta("_original_team")

						if active_boss.alive:
							var orig_hp = active_boss.get_meta("_original_max_hp") if active_boss.has_meta("_original_max_hp") else 100.0
							var hp_pct = active_boss.hp / (orig_hp * 3.0) if orig_hp > 0 else 1.0
							active_boss.hp = orig_hp * hp_pct

						for b in balls:
							if b != active_boss and b.has_meta("_original_team"):
								b.team = b.get_meta("_original_team")

						set_meta("boss_mutator_timer", delta)
				else:
					var b_timer = get_meta("boss_mutator_timer") + delta
					if b_timer >= 10.0:
						b_timer = 0.0
						var valid_bosses = []
						for b in balls:
							if b.alive and b.get("ball_type", "") != "spectator":
								valid_bosses.append(b)
						if valid_bosses.size() > 0:
							var new_boss = valid_bosses[randi() % valid_bosses.size()]
							new_boss.set_meta("_is_boss_mutator", true)
							new_boss.set_meta("_boss_mutator_duration", 15.0)

							var orig_rad = 15.0
							if "radius" in new_boss:
								orig_rad = new_boss.radius
								new_boss.radius = orig_rad * 2.0
							elif new_boss.has_meta("radius"):
								orig_rad = new_boss.get_meta("radius")
								new_boss.set_meta("radius", orig_rad * 2.0)
							new_boss.set_meta("_original_radius", orig_rad)

							var orig_max_hp = new_boss.get("max_hp", 100.0)
							new_boss.set_meta("_original_max_hp", orig_max_hp)
							new_boss.max_hp = orig_max_hp * 3.0

							var hp_pct = new_boss.get("hp", 100.0) / orig_max_hp if orig_max_hp > 0 else 1.0
							new_boss.hp = new_boss.max_hp * hp_pct

							var orig_dmg = new_boss.get("damage", 10.0)
							new_boss.set_meta("_original_damage", orig_dmg)
							new_boss.damage = orig_dmg * 2.0

							if "base_damage" in new_boss:
								new_boss.set_meta("_original_base_damage", new_boss.base_damage)
								new_boss.base_damage = new_boss.get_meta("_original_base_damage") * 2.0

							new_boss.set_meta("_original_team", new_boss.get("team", new_boss.get("ball_type", "solo")))
							new_boss.team = "Boss_Mutator"

							for b in balls:
								if b != new_boss and b.get("ball_type", "") != "spectator":
									if not b.has_meta("_original_team"):
										b.set_meta("_original_team", b.get("team", b.get("ball_type", "solo")))
									b.team = "Hunters"

							if world != null and world.has_method("add_event"):
								world.add_event("boss_mutator", {"message": "A player has become a Juggernaut Boss!"})

					set_meta("boss_mutator_timer", b_timer)

					set_meta("boss_mutator_timer", b_timer)

			var trigger_reroll = false			var trigger_reroll = false
			var types = ['time_mage', 'paladin', 'assassin', 'ninja', 'warrior', 'guardian', 'chaos', 'bomber', 'templar', 'necromancer', 'vampire', 'sniper', 'king', 'easy', 'phantom', 'warlock', 'mimic', 'juggernaut', 'tank', 'berserker', 'druid', 'hard', 'scout', 'brawler', 'medium', 'neural', 'ranger', 'healer', 'rogue', 'drone', 'swarm', 'conjurer', 'monk', 'mage', 'elementalist', 'trickster']
			if mutators.has("random_reroll"):
				if not has_meta("random_reroll_timer"):
					set_meta("random_reroll_timer", 0.0)
				var timer = get_meta("random_reroll_timer") + delta
				if timer >= 10.0:
					trigger_reroll = true
					timer = 0.0
				set_meta("random_reroll_timer", timer)

			for b in balls:
				if not b.alive: continue

				if mutators.has("double_speed"):
					if "base_speed" in b and not b.has_meta("_double_speed_applied"):
						b.speed = b.base_speed * 2.0
						b.set_meta("_double_speed_applied", true)

				if trigger_reroll:
					if b.get("ball_type", "") != "spectator":
						b.ball_type = types[randi() % types.size()]
						b.max_hp = randf_range(50.0, 200.0)
						b.hp = b.max_hp
						b.base_speed = randf_range(50.0, 200.0)
						b.speed = b.base_speed
						if "base_damage" in b:
							b.base_damage = randf_range(5.0, 25.0)
							b.damage = b.base_damage




class EcholocationMode extends GameMode:
	var flash_timer = 0.0
	var flash_interval = 10.0
	var is_flashing = false
	var flash_duration = 0.5
	var current_flash_time = 0.0

	func _init() -> void:
		name = "Echolocation"
		description = "The arena is completely dark except for a small ring of light around each ball. Echolocation cues and occasional lightning flashes reveal the map."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		flash_timer = 0.0
		is_flashing = false
		current_flash_time = 0.0

		if world != null and "arena" in world and world.arena != null:
			world.arena.is_night = true

		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		for b in balls:
			if b.ball_type != "spectator":
				var base_perc = 250.0
				if "perception_radius" in b:
					base_perc = float(b.perception_radius)
				if b.has_method("set_meta"):
					b.set_meta("base_perception_radius", base_perc)
				b.perception_radius = 60.0
				if not "team" in b:
					b.team = b.ball_type

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		for b in balls:
			if not b.alive:
				if not world.get_meta("dead_balls").has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if b.has_method("get_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

		flash_timer += delta

		if is_flashing:
			current_flash_time += delta
			if current_flash_time >= flash_duration:
				is_flashing = false
				if world != null and "arena" in world and world.arena != null:
					world.arena.is_night = true
				for b in balls:
					if b.alive and b.ball_type != "spectator":
						b.perception_radius = 60.0
		else:
			if flash_timer >= flash_interval:
				flash_timer = 0.0
				is_flashing = true
				current_flash_time = 0.0
				if world != null and "arena" in world and world.arena != null:
					world.arena.is_night = false

				if world != null and world.has_method("add_event"):
					world.add_event("weather_warning", {"type": "weather_warning", "message": "Lightning flash reveals the arena!"})

				for b in balls:
					if b.alive and b.ball_type != "spectator":
						b.perception_radius = 1000.0

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			if b.alive and b.ball_type != "spectator":
				alive.append(b)

		if alive.size() == 0:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return "Draw"

		var teams_alive = {}
		for b in alive:
			var t = b.ball_type
			if "team" in b:
				t = b.team
			teams_alive[t] = true

		if teams_alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return teams_alive.keys()[0]

		if alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return alive[0].ball_type

		return null


class PitchBlackMode extends GameMode:
	func _init() -> void:
		name = "Pitch Black"
		description = "The screen is completely dark. AI relies entirely on a narrow cone of light matching its perception radius."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if world != null and "arena" in world and world.arena != null:
			world.arena.is_night = true
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			if b.ball_type != "spectator":
				var base_perc = 250.0
				if "perception_radius" in b:
					base_perc = float(b.perception_radius)
				if b.has_method("set_meta"):
					b.set_meta("base_perception_radius", base_perc)
				b.perception_radius = base_perc
				if not "team" in b:
					b.team = b.ball_type

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			if not b.alive:
				if not world.get_meta("dead_balls").has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if b.has_method("get_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

		for b in balls:
			if b.alive and b.ball_type != "spectator":
				var base_perc = 250.0
				if b.has_method("get_meta") and b.has_meta("base_perception_radius"):
					base_perc = b.get_meta("base_perception_radius")
				b.perception_radius = base_perc

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			if b.alive and b.ball_type != "spectator":
				alive.append(b)

		if alive.size() == 0:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return "Draw"

		var teams_alive = {}
		for b in alive:
			var t = b.get("team")
			if t == null: t = b.ball_type
			teams_alive[t] = true

		if teams_alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return teams_alive.keys()[0]

		if alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return alive[0].ball_type

		return null

class VisionReducedMode extends GameMode:
	var pulse_timer: float = 0.0

	func _init() -> void:
		name = "Vision Reduced"
		description = "Visibility is severely reduced. AI relies on narrow cones of light or sonar-like pulses."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			if b.ball_type != "spectator":
				var base_perc = 250.0
				if "perception_radius" in b:
					base_perc = float(b.perception_radius)
				if b.has_method("set_meta"):
					b.set_meta("base_perception_radius", base_perc)
				b.perception_radius = 50.0
				if not "team" in b:
					b.team = b.ball_type

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			if not b.alive:
				if not world.get_meta("dead_balls").has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if b.has_method("get_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

		pulse_timer += delta
		var is_pulse_active = false
		if pulse_timer >= 3.0:
			if pulse_timer >= 3.5:
				pulse_timer = 0.0
			else:
				is_pulse_active = true

		for b in balls:
			if b.alive and b.ball_type != "spectator":
				if is_pulse_active:
					var base_perc = 250.0
					if b.has_method("get_meta") and b.has_meta("base_perception_radius"):
						base_perc = b.get_meta("base_perception_radius")
					b.perception_radius = base_perc * 1.5
				else:
					b.perception_radius = 50.0

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			if b.alive and b.ball_type != "spectator":
				alive.append(b)

		if alive.size() == 0:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return "Draw"

		var teams_alive = {}
		for b in alive:
			var t = b.get("team")
			if t == null: t = b.ball_type
			teams_alive[t] = true

		if teams_alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return teams_alive.keys()[0]

		if alive.size() == 1:
			if has_method("_award_skill_points"): call("_award_skill_points")
			return alive[0].ball_type

		return null

class EMPBurstMode extends GameMode:
	var spawn_timer: float = 0.0

	func _init():
		super._init()
		name = "EMP Burst"
		description = "Periodic EMP bursts scramble AI targeting!"

	func setup(world, balls):
		super.setup(world, balls)
		if not "hazards" in world.arena:
			world.arena.hazards = []
		spawn_timer = 0.0

	func tick(world, balls, delta: float = 0.016):
		super.tick(world, balls, delta)
		spawn_timer += delta
		if spawn_timer >= 5.0:
			spawn_timer = 0.0
			var ProceduralArena = load("res://src/arena/procedural_arena.gd")
			if ProceduralArena != null:
				var x = rng.randf_range(100.0, world.arena.width - 100.0)
				var y = rng.randf_range(100.0, world.arena.height - 100.0)
				var new_hazard = ProceduralArena.Hazard.new(world.arena.hazards.size() + rng.randi_range(1000, 9999), x, y, 150.0, "emp_burst", 0.0)
				if new_hazard.has_method("set_meta"):
					new_hazard.set_meta("duration", 1.0)
				else:
					new_hazard.duration = 1.0
				world.arena.hazards.append(new_hazard)

class DynamicHazardsMode extends GameMode:
	var spawn_timer = 0.0
	var rng = RandomNumberGenerator.new()

	func _init():
		super()
		name = "Dynamic Hazards"
		description = "Dynamic map hazards like spikes, fire, and ice traps spawn, move, or change severity."

	func setup(world, balls):
		super.setup(world, balls)
		if not "hazards" in world.arena:
			world.arena.hazards = []

	func tick(world, balls, delta = 0.016):
		super.tick(world, balls, delta)

		spawn_timer += delta
		var max_hazards = 15
		if spawn_timer >= 3.0:
			spawn_timer = 0.0

			var active_dynamic = 0
			for h in world.arena.hazards:
				if h.has_method("has_meta") and h.has_meta("vx") and h.has_meta("vy"):
					active_dynamic += 1

			if active_dynamic < max_hazards:
				var x = 0.0 if rng.randf() < 0.5 else world.arena.width
				var y = rng.randf_range(0.0, world.arena.height)
				var vx = rng.randf_range(50.0, 200.0) if x == 0.0 else rng.randf_range(-200.0, -50.0)
				var vy = rng.randf_range(-50.0, 50.0)

				var types = [
					{"kind": "lava", "damage": 25.0, "radius": 40.0},
					{"kind": "spikes", "damage": 15.0, "radius": 30.0},
					{"kind": "ice_patch", "damage": 5.0, "radius": 50.0},
					{"kind": "poison_cloud", "damage": 10.0, "radius": 45.0}
				]
				var h_type = types[rng.randi() % types.size()]

				var current_tick = world.get("current_tick") if "current_tick" in world else 0
				var time_factor = 1.0 + (current_tick / 60.0) / 100.0
				var radius_mult = min(2.0, time_factor)
				var damage_mult = min(3.0, time_factor)

				var base_radius = h_type["radius"] * radius_mult
				var base_damage = h_type["damage"] * damage_mult
				var ProceduralArena = load("res://src/arena/procedural_arena.gd")
				var new_hazard = ProceduralArena.Hazard.new(
					world.arena.hazards.size() + rng.randi_range(1000, 9999),
					x, y, base_radius,
					h_type["kind"], base_damage
				)

				if new_hazard.has_method("set_meta"):
					new_hazard.set_meta("vx", vx)
					new_hazard.set_meta("vy", vy)
					new_hazard.set_meta("base_radius", base_radius)
					new_hazard.set_meta("base_damage", base_damage)

				world.arena.hazards.append(new_hazard)

		var hazards_to_keep = []
		var current_tick = world.get("current_tick") if "current_tick" in world else 0
		var current_time = current_tick * delta

		for hazard in world.arena.hazards:
			if hazard.has_method("has_meta") and hazard.has_meta("vx") and hazard.has_meta("vy"):
				hazard.x += hazard.get_meta("vx") * delta
				hazard.y += hazard.get_meta("vy") * delta

				if hazard.has_meta("base_radius"):
					hazard.radius = hazard.get_meta("base_radius") + sin(current_time * 2.0) * 5.0
					hazard.target_radius = hazard.radius

				if hazard.has_meta("base_damage"):
					hazard.damage = hazard.get_meta("base_damage") * (1.0 + sin(current_time) * 0.5)

				var margin = 200.0
				if hazard.x >= -margin and hazard.x <= world.arena.width + margin and \
				   hazard.y >= -margin and hazard.y <= world.arena.height + margin:
					hazards_to_keep.append(hazard)
			else:
				hazards_to_keep.append(hazard)

		world.arena.hazards = hazards_to_keep


class PortalNodeMode extends GameMode:
    var portal_timer: float = 0.0
    var portal_x: float = 500.0
    var portal_y: float = 500.0
    var capture_radius: float = 100.0
    var drain_rate: float = 5.0
    var team_scores: Dictionary = {}

    func _init() -> void:
        name = "Portal Node"
        description = "Capture and hold the moving portal node."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        team_scores.clear()
        for b in balls:
            var team = "Solo"
            if "team" in b:
                team = b.team
            if not team_scores.has(team):
                team_scores[team] = 1000.0

        var arena_w = 1000.0
        var arena_h = 1000.0
        if "arena" in world and world.arena != null:
            if "width" in world.arena:
                arena_w = float(world.arena.width)
            if "height" in world.arena:
                arena_h = float(world.arena.height)
        portal_x = arena_w / 2.0
        portal_y = arena_h / 2.0
        portal_timer = 0.0

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        super.tick(world, balls, delta)

        portal_timer += delta
        if portal_timer >= 10.0:
            portal_timer = 0.0
            var arena_w = 1000.0
            var arena_h = 1000.0
            if "arena" in world and world.arena != null:
                if "width" in world.arena:
                    arena_w = float(world.arena.width)
                if "height" in world.arena:
                    arena_h = float(world.arena.height)
            portal_x = randf_range(100.0, max(100.0, arena_w - 100.0))
            portal_y = randf_range(100.0, max(100.0, arena_h - 100.0))
            print("Portal moved to ", portal_x, ", ", portal_y)

        # Count balls in portal radius per team
        var teams_in_radius: Dictionary = {}
        for b in balls:
            if not b.alive:
                continue
            var dx = b.position.x - portal_x
            var dy = b.position.y - portal_y
            var dist = sqrt(dx*dx + dy*dy)
            if dist <= capture_radius:
                var team = "Solo"
                if "team" in b:
                    team = b.team
                if not teams_in_radius.has(team):
                    teams_in_radius[team] = 0
                teams_in_radius[team] += 1

        # If exactly one team is in the radius, they capture it and drain others
        if teams_in_radius.size() == 1:
            var controlling_team = teams_in_radius.keys()[0]
            for t in team_scores.keys():
                if t != controlling_team:
                    team_scores[t] -= drain_rate * delta
                    if team_scores[t] < 0:
                        team_scores[t] = 0.0




class MovingSafeZoneMode extends GameMode:
    var zone_x: float = 500.0
    var zone_y: float = 500.0
    var zone_radius: float = 500.0
    var min_zone_radius: float = 50.0
    var shrink_rate: float = 10.0
    var outside_damage_per_second: float = 15.0
    var zone_target_x: float = 500.0
    var zone_target_y: float = 500.0
    var move_speed: float = 30.0
    var tick_timer: float = 0.0
    var collapse_triggered: bool = false

    func _init() -> void:
        name = "Moving Safe Zone"
        description = "A dynamic battle royale where the safe zone not only shrinks but also moves around the map, forcing intense combat."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        collapse_triggered = false
        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena:
            if "width" in world.arena:
                arena_width = float(world.arena.width)
            if "height" in world.arena:
                arena_height = float(world.arena.height)

        zone_x = arena_width / 2.0
        zone_y = arena_height / 2.0
        zone_target_x = zone_x
        zone_target_y = zone_y
        zone_radius = min(arena_width, arena_height) / 2.0
        min_zone_radius = 50.0
        zone_target_x = zone_x
        zone_target_y = zone_y

        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = false
            else:
                b.team = b.ball_type

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena:
            if "width" in world.arena:
                arena_width = float(world.arena.width)
            if "height" in world.arena:
                arena_height = float(world.arena.height)

        # Move safe zone
        var dx = zone_target_x - zone_x
        var dy = zone_target_y - zone_y
        var dist = sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            zone_x += (dx / dist) * move_speed * delta
            zone_y += (dy / dist) * move_speed * delta
        else:
            # Pick a new target
            # Ensuring it drifts in a random direction and doesn't just converge on a single static point
            var buffer = max(100.0, zone_radius * 0.5)
            var rng = RandomNumberGenerator.new()
            rng.randomize()
            zone_target_x = rng.randf_range(buffer, arena_width - buffer)
            zone_target_y = rng.randf_range(buffer, arena_height - buffer)

        # Shrink safe zone
        if zone_radius > min_zone_radius:
            zone_radius -= shrink_rate * delta
            if zone_radius <= min_zone_radius:
                zone_radius = min_zone_radius
                if not collapse_triggered:
                    collapse_triggered = true
                    if world.has_method("add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif collapse_triggered:
            if zone_radius > 0:
                zone_radius -= shrink_rate * delta
                if zone_radius < 0:
                    zone_radius = 0.0

            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var b_x = b.get("position").x if b.get("position") != null else b.get("x")
                    var b_y = b.get("position").y if b.get("position") != null else b.get("y")
                    var dx = zone_x - b_x
                    var dy = zone_y - b_y
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        var pull_strength = 2000.0
                        if not "vx" in b: b.vx = 0.0
                        if not "vy" in b: b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
                continue

            var bx = b.position.x if "position" in b else b.x
            var by = b.position.y if "position" in b else b.y
            var bdx = bx - zone_x
            var bdy = by - zone_y
            var bdist = sqrt(bdx*bdx + bdy*bdy)

            if bdist > zone_radius:
                if "hp" in b:
                    var damage = outside_damage_per_second * (10.0 if collapse_triggered else 1.0) * delta
                    b.hp -= damage

                    var effect_timer = 0.0
                    if b.has_method("get_meta") and b.has_meta("danger_effect_timer"):
                        effect_timer = b.get_meta("danger_effect_timer")
                    effect_timer += delta
                    if effect_timer > 0.5:
                        effect_timer = 0.0
                        world.add_event("danger_zone_damage", {
                            "x": bx,
                            "y": by
                        })
                    if b.has_method("set_meta"):
                        b.set_meta("danger_effect_timer", effect_timer)

                    if b.hp <= 0:
                        b.alive = false
                        b.killer = "Danger Zone"
                        world.add_event("danger_zone_death", {"message": b.ball_type.capitalize() + " succumbed to the danger zone!"})

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var t = b.team if "team" in b else b.ball_type
            teams_alive[t] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        return null



class ShrinkingDangerZoneMode extends GameMode:
    var zone_x: float = 500.0
    var zone_y: float = 500.0
    var zone_radius: float = 500.0
    var min_zone_radius: float = 50.0
    var shrink_rate: float = 15.0
    var outside_damage_per_second: float = 20.0
    var collapse_triggered: bool = false
    var zone_target_x: float = 500.0
    var zone_target_y: float = 500.0

    func _init() -> void:
        name = "Shrinking Danger Zone"
        description = "A shrinking danger zone mode where the safe area slowly decreases, forcing players into close-quarters combat."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        collapse_triggered = false
        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena:
            if "width" in world.arena:
                arena_width = float(world.arena.width)
            if "height" in world.arena:
                arena_height = float(world.arena.height)

        zone_x = arena_width / 2.0
        zone_y = arena_height / 2.0
        zone_radius = min(arena_width, arena_height) / 2.0
        min_zone_radius = 50.0
        zone_target_x = zone_x
        zone_target_y = zone_y

        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = false
            else:
                b.team = b.ball_type

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        # Drift the safe zone
        var ddx = zone_target_x - zone_x
        var ddy = zone_target_y - zone_y
        var ddist = sqrt(ddx*ddx + ddy*ddy)
        if ddist > 5.0:
            var d_move_speed = 10.0
            zone_x += (ddx / ddist) * d_move_speed * delta
            zone_y += (ddy / ddist) * d_move_speed * delta
        else:
            var arena_width = 1000.0
            var arena_height = 1000.0
            if world != null and "arena" in world and world.arena:
                if "width" in world.arena:
                    arena_width = float(world.arena.width)
                if "height" in world.arena:
                    arena_height = float(world.arena.height)
            var buffer = max(100.0, zone_radius * 0.5)
            var rng = RandomNumberGenerator.new()
            rng.randomize()
            zone_target_x = rng.randf_range(buffer, arena_width - buffer)
            zone_target_y = rng.randf_range(buffer, arena_height - buffer)

        # Shrink the safe zone
        if zone_radius > min_zone_radius:
            zone_radius -= shrink_rate * delta
            if zone_radius <= min_zone_radius:
                zone_radius = min_zone_radius
                if not collapse_triggered:
                    collapse_triggered = true
                    if world.has_method("add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif collapse_triggered:
            if zone_radius > 0:
                zone_radius -= shrink_rate * delta
                if zone_radius < 0:
                    zone_radius = 0.0

            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var b_x = b.get("position").x if b.get("position") != null else b.get("x")
                    var b_y = b.get("position").y if b.get("position") != null else b.get("y")
                    var dx = zone_x - b_x
                    var dy = zone_y - b_y
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        var pull_strength = 2000.0
                        if not "vx" in b: b.vx = 0.0
                        if not "vy" in b: b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        # Apply continuous damage outside the safe zone
        var damage_this_tick = outside_damage_per_second * (10.0 if collapse_triggered else 1.0) * delta
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                var dx = b.x - zone_x
                var dy = b.y - zone_y
                var dist = sqrt(dx*dx + dy*dy)

                if dist > zone_radius:
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = false
                        b.hp = 0

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.get("alive", false) and b.get("ball_type", "") != "spectator":
                alive.append(b)
        if alive.is_empty():
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var team = b.get("team") if b.get("team") != null else b.get("ball_type")
            teams_alive[team] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        if alive.size() == 1:
            return alive[0].get("team", alive[0].get("ball_type"))

        return null

class ModifierZonesSafeZoneMode extends GameMode:
    var zone_x: float = 500.0
    var zone_y: float = 500.0
    var zone_radius: float = 500.0
    var min_zone_radius: float = 50.0
    var shrink_rate: float = 10.0
    var outside_damage_per_second: float = 10.0
    var zone_target_x: float = 500.0
    var zone_target_y: float = 500.0
    var collapse_triggered: bool = false
    var zones: Array = []

    func _init() -> void:
        name = "Modifier Zones Safe Zone"
        description = "The safe zone shrinks, and modifier zones spawn near its center, forcing players to fight for buffs."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        collapse_triggered = false
        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena:
            if "width" in world.arena:
                arena_width = float(world.arena.width)
            if "height" in world.arena:
                arena_height = float(world.arena.height)

        zone_x = arena_width / 2.0
        zone_y = arena_height / 2.0
        zone_target_x = zone_x
        zone_target_y = zone_y
        zone_radius = min(arena_width, arena_height) / 2.0
        min_zone_radius = 50.0

        zones = [
            {"id": "zone_speed", "x": zone_x - 100, "y": zone_y - 100, "radius": 75.0, "type": "speed"},
            {"id": "zone_damage", "x": zone_x + 100, "y": zone_y - 100, "radius": 75.0, "type": "damage"},
            {"id": "zone_heal", "x": zone_x, "y": zone_y + 100, "radius": 75.0, "type": "heal"},
            {"id": "zone_debuff", "x": zone_x, "y": zone_y, "radius": 75.0, "type": "debuff"}
        ]

        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = false
            else:
                b.team = b.ball_type

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        var dx = zone_target_x - zone_x
        var dy = zone_target_y - zone_y
        var dist_zone = sqrt(dx*dx + dy*dy)
        if dist_zone > 5.0:
            var move_speed = 15.0
            zone_x += (dx / dist_zone) * move_speed * delta
            zone_y += (dy / dist_zone) * move_speed * delta
        else:
            var arena_width = 1000.0
            var arena_height = 1000.0
            if world != null and "arena" in world and world.arena:
                if "width" in world.arena:
                    arena_width = float(world.arena.width)
                if "height" in world.arena:
                    arena_height = float(world.arena.height)
            var buffer = max(100.0, zone_radius * 0.5)
            zone_target_x = randf_range(buffer, arena_width - buffer)
            zone_target_y = randf_range(buffer, arena_height - buffer)

        if zone_radius > min_zone_radius:
            zone_radius -= shrink_rate * delta
            if zone_radius <= min_zone_radius:
                zone_radius = min_zone_radius
                if not collapse_triggered:
                    collapse_triggered = true
                    if world.has_method("add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif collapse_triggered:
            if zone_radius > 0:
                zone_radius -= shrink_rate * delta
                if zone_radius < 0:
                    zone_radius = 0.0

            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var b_x = b.get("position").x if b.get("position") != null else b.get("x")
                    var b_y = b.get("position").y if b.get("position") != null else b.get("y")
                    var dx_pull = zone_x - b_x
                    var dy_pull = zone_y - b_y
                    var dist_pull = sqrt(dx_pull*dx_pull + dy_pull*dy_pull)
                    if dist_pull > 0:
                        var pull_strength = 2000.0
                        if not "vx" in b: b.vx = 0.0
                        if not "vy" in b: b.vy = 0.0
                        b.vx += (dx_pull / dist_pull) * pull_strength * delta
                        b.vy += (dy_pull / dist_pull) * pull_strength * delta

        if zones.size() >= 4:
            zones[0]["x"] = zone_x - 100
            zones[0]["y"] = zone_y - 100
            zones[1]["x"] = zone_x + 100
            zones[1]["y"] = zone_y - 100
            zones[2]["x"] = zone_x
            zones[2]["y"] = zone_y + 100
            zones[3]["x"] = zone_x
            zones[3]["y"] = zone_y

        var damage_this_tick = outside_damage_per_second * (10.0 if collapse_triggered else 1.0) * delta

        for b in balls:
            if not b.alive or b.ball_type == "spectator":
                continue

            if not b.has_meta("base_speed"):
                b.set_meta("base_speed", b.get("speed") if b.get("speed") != null else 100.0)
            if not b.has_meta("base_damage"):
                b.set_meta("base_damage", b.get("damage") if b.get("damage") != null else 10.0)

            var in_speed_zone = false
            var in_damage_zone = false
            var in_heal_zone = false
            var in_debuff_zone = false

            var b_x = b.get("position").x if b.get("position") != null else b.get("x")
            var b_y = b.get("position").y if b.get("position") != null else b.get("y")

            for zone in zones:
                var dx_z = b_x - zone["x"]
                var dy_z = b_y - zone["y"]
                var dist_z = sqrt(dx_z*dx_z + dy_z*dy_z)

                if dist_z <= zone["radius"]:
                    if zone["type"] == "speed":
                        in_speed_zone = true
                    elif zone["type"] == "damage":
                        in_damage_zone = true
                    elif zone["type"] == "heal":
                        in_heal_zone = true
                    elif zone["type"] == "debuff":
                        in_debuff_zone = true

            if in_speed_zone:
                b.speed = b.get_meta("base_speed") * 1.5
                b.set_meta("zone_modifier_speed", true)
            else:
                if b.has_meta("zone_modifier_speed"):
                    b.speed = b.get_meta("base_speed")
                    b.remove_meta("zone_modifier_speed")

            if in_damage_zone:
                b.damage = b.get_meta("base_damage") * 1.5
                b.set_meta("zone_modifier_damage", true)
            else:
                if b.has_meta("zone_modifier_damage"):
                    b.damage = b.get_meta("base_damage")
                    b.remove_meta("zone_modifier_damage")

            if in_debuff_zone:
                if not b.has_meta("base_max_hp"):
                    b.set_meta("base_max_hp", b.get("max_hp") if b.get("max_hp") != null else 100.0)
                b.max_hp = b.get_meta("base_max_hp") * 0.5
                if b.get("hp", 0) > b.max_hp:
                    b.hp = b.max_hp
                b.set_meta("zone_modifier_debuff", true)
            else:
                if b.has_meta("zone_modifier_debuff"):
                    if b.has_meta("base_max_hp"):
                        b.max_hp = b.get_meta("base_max_hp")
                    b.remove_meta("zone_modifier_debuff")

            if in_heal_zone:
                if "hp" in b and "max_hp" in b:
                    b.hp = min(b.get("max_hp") if b.get("max_hp") != null else 100.0, b.hp + 20.0 * delta)

            var dx_s = b_x - zone_x
            var dy_s = b_y - zone_y
            var dist_s = sqrt(dx_s*dx_s + dy_s*dy_s)
            if dist_s > zone_radius:
                b.hp -= damage_this_tick
                if b.hp <= 0:
                    b.alive = false
                    b.hp = 0

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            if self.has_method("_award_skill_points"):
                self.call("_award_skill_points")
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var team = b.ball_type
            if b.has_method("get") or "team" in b:
                team = b.team
            teams_alive[team] = true

        if teams_alive.size() == 1:
            if self.has_method("_award_skill_points"):
                self.call("_award_skill_points")
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if self.has_method("_award_skill_points"):
                self.call("_award_skill_points")
            var ret = alive[0].ball_type
            if alive[0].has_method("get") or "team" in alive[0]:
                ret = alive[0].team
            return ret

        return null


class SafeZoneMode extends GameMode:
    var zone_x: float = 500.0
    var zone_y: float = 500.0
    var zone_radius: float = 500.0
    var min_zone_radius: float = 50.0
    var shrink_rate: float = 10.0
    var outside_damage_per_second: float = 10.0
    var zone_target_x: float = 500.0
    var zone_target_y: float = 500.0
    var collapse_triggered: bool = false

    func _init() -> void:
        name = "Safe Zone"
        description = "A battle royale mode where the safe zone gradually shrinks, and balls take continuous damage outside of it."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        collapse_triggered = false
        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena:
            if "width" in world.arena:
                arena_width = float(world.arena.width)
            if "height" in world.arena:
                arena_height = float(world.arena.height)

        zone_x = arena_width / 2.0
        zone_y = arena_height / 2.0
        zone_target_x = zone_x
        zone_target_y = zone_y
        zone_radius = min(arena_width, arena_height) / 2.0
        min_zone_radius = 50.0
        zone_target_x = zone_x
        zone_target_y = zone_y

        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = false
            else:
                b.team = b.ball_type

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        # Move the safe zone
        var dx = zone_target_x - zone_x
        var dy = zone_target_y - zone_y
        var dist = sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            var move_speed = 15.0 # pixels per second
            zone_x += (dx / dist) * move_speed * delta
            zone_y += (dy / dist) * move_speed * delta
        else:
            # Pick a new target
            # Ensuring it drifts in a random direction and doesn't just converge on a single static point
            var arena_width = 1000.0
            var arena_height = 1000.0
            if world != null and "arena" in world and world.arena:
                if "width" in world.arena:
                    arena_width = float(world.arena.width)
                if "height" in world.arena:
                    arena_height = float(world.arena.height)
            var buffer = max(100.0, zone_radius * 0.5)
            zone_target_x = randf_range(buffer, arena_width - buffer)
            zone_target_y = randf_range(buffer, arena_height - buffer)

        # Shrink the safe zone
        if zone_radius > min_zone_radius:
            zone_radius -= shrink_rate * delta
            if zone_radius <= min_zone_radius:
                zone_radius = min_zone_radius
                if not collapse_triggered:
                    collapse_triggered = true
                    if world.has_method("add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif collapse_triggered:
            if zone_radius > 0:
                zone_radius -= shrink_rate * delta
                if zone_radius < 0:
                    zone_radius = 0.0

            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var b_x = b.get("position").x if b.get("position") != null else b.get("x")
                    var b_y = b.get("position").y if b.get("position") != null else b.get("y")
                    var dx = zone_x - b_x
                    var dy = zone_y - b_y
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        var pull_strength = 2000.0
                        if not "vx" in b: b.vx = 0.0
                        if not "vy" in b: b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        # Apply continuous damage outside the safe zone
        var damage_this_tick = outside_damage_per_second * (10.0 if collapse_triggered else 1.0) * delta
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                var dx = b.x - zone_x
                var dy = b.y - zone_y
                var dist = sqrt(dx*dx + dy*dy)

                # If outside safe zone, take damage
                if dist > zone_radius:
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = false
                        b.hp = 0

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            _award_skill_points()
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var team = b.ball_type
            if b.has_method("get") or "team" in b:
                team = b.team
            teams_alive[team] = true

        if teams_alive.size() == 1:
            _award_skill_points()
            return teams_alive.keys()[0]

        return null

    func _award_skill_points():
        pass



class MirrorMatchMode extends GameMode:
	func _init() -> void:
		name = "Mirror Match"
		description = "Every player spawns with an exact AI clone of themselves on the opposite side of the map. Clones mimic their creator's stats and skills."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)

		var arena_width = 2000.0
		var arena_height = 2000.0
		if "arena" in world and world.arena != null:
			if "width" in world.arena: arena_width = world.arena.width
			if "height" in world.arena: arena_height = world.arena.height

		var new_clones = []
		for b in balls:
			if b.has_method("duplicate"):
				var clone = b.duplicate()
				var next_id = randi() % 90000 + 10000
				if "next_id" in world:
					next_id = world.next_id
					world.next_id += 1
				if "id" in clone: clone.id = next_id

				if "x" in clone and "x" in b: clone.x = arena_width - b.x
				if "y" in clone and "y" in b: clone.y = arena_height - b.y

				if clone.has_method("set_meta"):
					clone.set_meta("is_clone", true)
					if "id" in b: clone.set_meta("clone_owner", b.id)

				if "team" in clone and "team" in b:
					clone.team = "mirror_team_" + str(b.team)

				new_clones.append(clone)

		if "balls" in world:
			for c in new_clones:
				world.balls.append(c)


class VolatileClonesMode extends GameMode:
	var clone_timer = 0.0

	func _init() -> void:
		name = "Volatile Clones"
		description = "Similar to Clone Chaos, but when a clone's HP drops to 0, it explodes dealing small area-of-effect damage."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		for b in balls:
			if b.has_method("set_meta"):
				b.set_meta("skill", "clone")
				b.set_meta("active_skill", "clone")
				b.set_meta("skill_cooldown", 1.0)
				b.set_meta("skill_timer", 0.0)
			if "skill" in b: b.skill = "clone"
			if "active_skill" in b: b.active_skill = "clone"
			if "skill_cooldown" in b: b.skill_cooldown = 1.0
			if "skill_timer" in b: b.skill_timer = 0.0

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)
		clone_timer += delta
		if clone_timer > 3.0:
			clone_timer = 0.0
			for b in balls:
				var alive = true
				if "alive" in b: alive = b.alive
				var skill_timer = 0.0
				if "skill_timer" in b: skill_timer = b.skill_timer
				if alive and skill_timer <= 0:
					if "skill_timer" in b: b.skill_timer = 1.0
					var num_clones = randi() % 3 + 1
					for i in range(num_clones):
						if b.has_method("duplicate"):
							var clone = b.duplicate()
							var next_id = randi() % 90000 + 10000
							if "next_id" in world:
								next_id = world.next_id
								world.next_id += 1
							if "id" in clone: clone.id = next_id
							if "x" in clone: clone.x += randf_range(-30.0, 30.0)
							if "y" in clone: clone.y += randf_range(-30.0, 30.0)
							if "hp" in b and "hp" in clone: clone.hp = b.hp
							if "max_hp" in b and "max_hp" in clone: clone.max_hp = b.max_hp
							if clone.has_method("set_meta"):
								clone.set_meta("is_clone", true)
								if "id" in b: clone.set_meta("clone_owner", b.id)
								clone.set_meta("is_decoy", true)
								clone.set_meta("decoy_type", "explosive")
								clone.set_meta("decoy_timer", 9999.0)
							if "alive" in clone: clone.alive = true
							if "speed" in clone: clone.speed = 0.0
							if "damage" in clone: clone.damage = 0.0
							if "is_decoy" in clone: clone.is_decoy = true
							if "decoy_type" in clone: clone.decoy_type = "explosive"
							if "decoy_timer" in clone: clone.decoy_timer = 9999.0
							if "traits" in clone:
								clone.traits = ["volatile_decoy"]
							elif clone.has_method("set_meta"):
								clone.set_meta("traits", ["volatile_decoy"])
							if "skill_timer" in clone: clone.skill_timer = 9999.0
							if "skill" in clone: clone.skill = ""
							if clone.has_method("set_meta"): clone.set_meta("skill", "")

							if "balls" in world:
								world.balls.append(clone)

class CloneChaosMode extends GameMode:
	var clone_timer = 0.0

	func _init() -> void:
		name = "Clone Chaos"
		description = "Every ball starts with the 'clone' skill with very low cooldown. The arena is quickly filled with static copies, causing mass confusion."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		for b in balls:
			if b.has_method("set_meta"):
				b.set_meta("skill", "clone")
				b.set_meta("active_skill", "clone")
				b.set_meta("skill_cooldown", 1.0)
				b.set_meta("skill_timer", 0.0)
			if "skill" in b: b.skill = "clone"
			if "active_skill" in b: b.active_skill = "clone"
			if "skill_cooldown" in b: b.skill_cooldown = 1.0
			if "skill_timer" in b: b.skill_timer = 0.0

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)
		clone_timer += delta
		if clone_timer > 3.0:
			clone_timer = 0.0
			for b in balls:
				var alive = true
				if "alive" in b: alive = b.alive
				var skill_timer = 0.0
				if "skill_timer" in b: skill_timer = b.skill_timer
				if alive and skill_timer <= 0:
					if "skill_timer" in b: b.skill_timer = 1.0
					var num_clones = randi() % 3 + 1
					for i in range(num_clones):
						if b.has_method("duplicate"):
							var clone = b.duplicate()
							var next_id = randi() % 90000 + 10000
							if "next_id" in world:
								next_id = world.next_id
								world.next_id += 1
							if "id" in clone: clone.id = next_id
							if "x" in clone: clone.x += randf_range(-30.0, 30.0)
							if "y" in clone: clone.y += randf_range(-30.0, 30.0)
							if "hp" in b and "hp" in clone: clone.hp = b.hp
							if "max_hp" in b and "max_hp" in clone: clone.max_hp = b.max_hp
							if clone.has_method("set_meta"):
								clone.set_meta("is_clone", true)
								if "id" in b: clone.set_meta("clone_owner", b.id)
							if "alive" in clone: clone.alive = true
							if "speed" in clone: clone.speed = 0.0
							if "damage" in clone: clone.damage = 0.0
							if "skill_timer" in clone: clone.skill_timer = 9999.0
							if "skill" in clone: clone.skill = ""
							if clone.has_method("set_meta"): clone.set_meta("skill", "")
							if "balls" in world:
								world.balls.append(clone)

class BumperBallsMode extends GameMode:
    func _init() -> void:
        name = "Bumper Balls"
        description = "Balls deal zero damage but bounce each other with much higher knockback. Try to push opponents off the arena!"

    func setup(world, balls: Array) -> void:
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            var sponsor = ""
            if "sponsor" in b:
                sponsor = b.sponsor
            elif b.has_method("get_meta") and b.has_meta("sponsor"):
                sponsor = b.get_meta("sponsor")

            if sponsor == "aggressor":
                if "max_hp" in b:
                    b.max_hp *= 0.8
                    if "hp" in b: b.hp = min(b.hp, b.max_hp)
            elif sponsor == "juggernaut":
                if "speed" in b: b.speed *= 0.8
                if "base_speed" in b: b.base_speed *= 0.8
                elif b.has_method("set_meta") and b.has_meta("base_speed"):
                    b.set_meta("base_speed", float(b.get_meta("base_speed")) * 0.8)
            elif sponsor == "vampiric":
                if "max_hp" in b:
                    b.max_hp *= 0.9
                    if "hp" in b: b.hp = min(b.hp, b.max_hp)
        for b in balls:
            b.damage = 0.0
            if not b.has_meta("mutators"):
                b.set_meta("mutators", [])
            var mutators = b.get_meta("mutators")
            if not mutators.has("bumper_balls"):
                mutators.append("bumper_balls")
                b.set_meta("mutators", mutators)

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena != null:
            if "width" in world.arena:
                arena_width = world.arena.width
            if "height" in world.arena:
                arena_height = world.arena.height
        elif "width" in world:
            arena_width = world.width
            arena_height = world.height

        for b in balls:
            if not b.get("alive", false) or b.get("ball_type", "") == "spectator":
                continue

            var radius = b.get("radius", 10.0)
            if b.x < -radius or b.x > arena_width + radius or b.y < -radius or b.y > arena_height + radius:
                if b.has_method("set"):
                    b.set("alive", false)
                else:
                    b.alive = false

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        if alive.size() == 1:
            if "team" in alive[0]:
                return alive[0].team
            return alive[0].ball_type

        return null


class TournamentMode extends GameMode:
    var tick_timer: float = 0.0

    func _init() -> void:
        name = "Tournament"
        description = "Monthly or seasonal tournament where players compete for exclusive cosmetic ball skins and unique status effects."

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        if alive.size() == 1:
            if "team" in alive[0]:
                return alive[0].team
            return alive[0].ball_type

        return null

class ToxicEnvironmentMode extends GameMode:
    var spawn_timer = 0.0

    func _init() -> void:
        name = "Toxic Environment"
        description = "Balls take constant damage over time. Collect temporary immune boosters to survive."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "boosters" in world:
            world.boosters = []
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        if not "boosters" in world:
            world.boosters = []

        spawn_timer += delta
        if spawn_timer >= 1.0:
            spawn_timer = 0.0
            var immune_boosters = 0
            for b in world.boosters:
                if typeof(b) == TYPE_DICTIONARY and b.has("is_immunity") and b.get("is_immunity") == true and b.has("active") and b.get("active") == true:
                    immune_boosters += 1
            if immune_boosters < 5:
                var x = randf_range(100.0, 900.0)
                var y = randf_range(100.0, 900.0)
                var b_id = randi() % 90000 + 10000
                if "next_id" in world:
                    b_id = world.next_id
                    world.next_id += 1
                world.boosters.append({
                    "id": b_id,
                    "x": x,
                    "y": y,
                    "ball_type": "booster",
                    "active": true,
                    "is_immunity": true,
                    "radius": 15.0
                })

        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
                continue

            var imm_timer = 0.0
            if b.has_method("get_meta") and b.has_meta("immunity_timer"):
                imm_timer = b.get_meta("immunity_timer")
            elif "immunity_timer" in b:
                imm_timer = b.immunity_timer

            if imm_timer > 0:
                if b.has_method("set_meta"):
                    b.set_meta("immunity_timer", imm_timer - delta)
                elif "immunity_timer" in b:
                    b.immunity_timer = imm_timer - delta
            else:
                if b.has_method("set_meta"):
                    b.set_meta("immunity_timer", 0.0)
                elif "immunity_timer" in b:
                    b.immunity_timer = 0.0
                if b.has_method("take_damage"):
                    b.take_damage(5.0 * delta)

            var to_remove = []
            for booster in world.boosters:
                if typeof(booster) == TYPE_DICTIONARY and booster.has("is_immunity") and booster.get("is_immunity") == true and booster.has("active") and booster.get("active") == true:
                    var bx = booster.get("x")
                    var by = booster.get("y")
                    var dist = sqrt(pow(b.x - bx, 2) + pow(b.y - by, 2))
                    var b_rad = 10.0
                    if "radius" in b:
                        b_rad = b.radius
                    elif b.has_method("get_meta") and b.has_meta("radius"):
                        b_rad = b.get_meta("radius")
                    var booster_rad = 15.0
                    if booster.has("radius"):
                        booster_rad = booster.get("radius")

                    if dist < b_rad + booster_rad:
                        if b.has_method("set_meta"):
                            b.set_meta("immunity_timer", 5.0)
                        elif "immunity_timer" in b:
                            b.immunity_timer = 5.0
                        booster["active"] = false
                        to_remove.append(booster)

            for booster in to_remove:
                world.boosters.erase(booster)

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        if alive.size() == 1:
            if "team" in alive[0]:
                return alive[0].team
            return alive[0].ball_type

        return null



class ModifierZonesMode extends GameMode:
	var zones: Array = []

	func _init():
		name = "Modifier Zones"
		description = "Fight over zones that provide different temporary buffs."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)

		var arena_width = 1000.0
		var arena_height = 1000.0
		if world.get("arena") != null:
			arena_width = world.arena.get("width", 1000.0)
			arena_height = world.arena.get("height", 1000.0)

		zones = [
			{"id": "zone_speed", "x": arena_width * 0.25, "y": arena_height * 0.25, "radius": 150.0, "type": "speed"},
			{"id": "zone_damage", "x": arena_width * 0.75, "y": arena_height * 0.25, "radius": 150.0, "type": "damage"},
			{"id": "zone_heal", "x": arena_width * 0.5, "y": arena_height * 0.75, "radius": 150.0, "type": "heal"},
			{"id": "zone_debuff", "x": arena_width * 0.5, "y": arena_height * 0.25, "radius": 150.0, "type": "debuff"}
		]

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		for b in balls:
			if not b.get("alive", false) or b.get("ball_type", "") == "spectator":
				continue

			if not b.has_meta("base_speed"):
				b.set_meta("base_speed", b.get("speed") if b.get("speed") != null else 100.0)
			if not b.has_meta("base_damage"):
				b.set_meta("base_damage", b.get("damage") if b.get("damage") != null else 10.0)

			var in_speed_zone = false
			var in_damage_zone = false
			var in_heal_zone = false
			var in_debuff_zone = false

			for zone in zones:
				var dx = b.x - zone["x"]
				var dy = b.y - zone["y"]
				var dist = sqrt(dx*dx + dy*dy)

				if dist <= zone["radius"]:
					if zone["type"] == "speed":
						in_speed_zone = true
					elif zone["type"] == "damage":
						in_damage_zone = true
					elif zone["type"] == "heal":
						in_heal_zone = true
					elif zone["type"] == "debuff":
						in_debuff_zone = true

			if in_speed_zone:
				b.speed = b.get_meta("base_speed") * 1.5
				b.set_meta("zone_modifier_speed", true)
			else:
				if b.has_meta("zone_modifier_speed"):
					b.speed = b.get_meta("base_speed")
					b.remove_meta("zone_modifier_speed")

			if in_damage_zone:
				b.damage = b.get_meta("base_damage") * 1.5
				b.set_meta("zone_modifier_damage", true)
			else:
				if b.has_meta("zone_modifier_damage"):
					b.damage = b.get_meta("base_damage")
					b.remove_meta("zone_modifier_damage")

			if in_debuff_zone:
				if not b.has_meta("base_max_hp"):
					b.set_meta("base_max_hp", b.get("max_hp") if b.get("max_hp") != null else 100.0)
				b.max_hp = b.get_meta("base_max_hp") * 0.5
				if "hp" in b and b.hp > b.max_hp:
					b.hp = b.max_hp
				b.set_meta("zone_modifier_debuff", true)
			else:
				if b.has_meta("zone_modifier_debuff"):
					if b.has_meta("base_max_hp"):
						b.max_hp = b.get_meta("base_max_hp")
					b.remove_meta("zone_modifier_debuff")

			if in_heal_zone:
				var max_hp = b.get("max_hp") if b.get("max_hp") != null else 100.0
				b.hp = min(max_hp, b.hp + 20.0 * delta)

	func check_winner(world, balls: Array):
		var alive = []
		for b in balls:
			if b.get("alive", false) and b.get("ball_type", "") != "spectator":
				alive.append(b)
		if alive.is_empty():
			return "Draw"

		var teams_alive = {}
		for b in alive:
			var team = b.get("team") if b.get("team") != null else b.get("ball_type")
			teams_alive[team] = true

		if teams_alive.size() == 1:
			return teams_alive.keys()[0]

		if alive.size() == 1:
			return alive[0].get("team", alive[0].get("ball_type"))

		return null



class WindstormMode extends GameMode:
    var push_timer = 3.0
    var push_duration = 0.0
    var push_dir_x = 0.0
    var push_dir_y = 0.0
    var push_strength = 600.0

    func _init() -> void:
        name = "Windstorm"
        description = "Periodically pushes all balls in a random direction, forcing them to constantly adjust movement to stay on target."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if b.ball_type != "spectator":
                b.team = b.ball_type
                if not "base_speed" in b:
                    b.base_speed = b.get("speed") if b.get("speed") != null else 100.0
                if not "base_damage" in b:
                    b.base_damage = b.get("damage") if b.get("damage") != null else 10.0


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        push_timer -= delta
        if push_timer <= 0:
            if push_duration <= 0:
                var angle = randf_range(0.0, 2.0 * PI)
                if world != null and world.has_method("add_event"):
                    world.add_event("weather_warning", {"type": "weather_warning", "message": "Windstorm is pushing!"})
                push_dir_x = cos(angle)
                push_dir_y = sin(angle)
                push_duration = randf_range(1.0, 2.0)
            else:
                push_duration -= delta
                if push_duration <= 0:
                    push_timer = randf_range(2.0, 4.0)

        if push_duration > 0:
            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    if not "vx" in b:
                        b.vx = 0.0
                    if not "vy" in b:
                        b.vy = 0.0
                    var is_kite = false
                    if "cosmetic" in b:
                        is_kite = str(b.cosmetic).to_lower().replace(" ", "_") == "kite"
                    elif b.has_method("get_meta") and b.has_meta("cosmetic"):
                        is_kite = str(b.get_meta("cosmetic")).to_lower().replace(" ", "_") == "kite"

                    var strength = push_strength
                    if is_kite:
                        if "base_speed" in b:
                            b.speed = b.base_speed * 1.5
                        elif b.has_method("get_meta") and b.has_meta("base_speed"):
                            if "speed" in b: b.speed = b.get_meta("base_speed") * 1.5
                        strength = push_strength * 1.5

                    b.vx += push_dir_x * strength * delta
                    b.vy += push_dir_y * strength * delta

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.get("alive", false) and b.get("ball_type", "") != "spectator":
                alive.append(b)
        if alive.is_empty():
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var team = b.get("team") if b.get("team") != null else b.get("ball_type")
            teams_alive[team] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        if alive.size() == 1:
            return alive[0].get("team", alive[0].get("ball_type"))

        return null



class BlackoutMode extends GameMode:
	var timer: float = 0.0
	var is_blackout: bool = false

	func _init() -> void:
		name = "Blackout"
		description = "Periodically, the arena goes completely dark, reducing vision drastically for all balls."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		timer = 0.0
		is_blackout = false
		for b in balls:
			if b.ball_type != "spectator":
				var base_perc = 250.0
				if "perception_radius" in b:
					base_perc = float(b.perception_radius)
				if b.has_method("set_meta"):
					b.set_meta("base_perception_radius", base_perc)
				if not "team" in b:
					b.team = b.ball_type

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		timer += delta
		if timer >= 5.0:
			timer = 0.0
			is_blackout = not is_blackout
			if world.has_method("add_event"):
				var msg = "The arena went dark!" if is_blackout else "Vision restored!"
				world.add_event("weather_warning", {"type": "weather_warning", "message": msg})

		for b in balls:
			if b.alive and b.ball_type != "spectator":
				if is_blackout:
					b.perception_radius = 50.0
				else:
					var base_perc = 250.0
					if b.has_method("get_meta") and b.has_meta("base_perception_radius"):
						base_perc = float(b.get_meta("base_perception_radius"))
					b.perception_radius = base_perc


class BountyHuntMode extends GameMode:
    var bounties = {}
    var buffed_teams = {}

    func _init() -> void:
        name = "Bounty Hunt"
        description = "One ball on each team is the Bounty. Destroying the enemy Bounty grants a massive buff and extra skill points."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        var red_team = []
        var blue_team = []

        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        var mid = valid_balls.size() / 2
        for i in range(valid_balls.size()):
            var b = valid_balls[i]
            if i < mid:
                b.team = "Red"
                red_team.append(b)
            else:
                b.team = "Blue"
                blue_team.append(b)

        bounties.clear()
        buffed_teams.clear()

        if red_team.size() > 0:
            var red_bounty = red_team[randi() % red_team.size()]
            red_bounty.set_meta("is_bounty", true)
            red_bounty.set_meta("bounty_timer", 0)
            bounties["Red"] = red_bounty

        if blue_team.size() > 0:
            var blue_bounty = blue_team[randi() % blue_team.size()]
            blue_bounty.set_meta("is_bounty", true)
            blue_bounty.set_meta("bounty_timer", 0)
            bounties["Blue"] = blue_bounty

    func tick(world, balls: Array, delta: float) -> void:
        super.tick(world, balls, delta)

        for team in bounties.keys():
            var bounty = bounties[team]
            if not bounty.alive and not buffed_teams.has(team):
                buffed_teams[team] = true
                var enemy_team = "Blue" if team == "Red" else "Red"

                for b in balls:
                    if b.alive and b.get("team") == enemy_team:
                        var bd = b.get("base_damage")
                        if bd != null: b.base_damage = bd * 2.0
                        var bs = b.get("base_speed")
                        if bs != null: b.base_speed = bs * 1.5
                        var mhp = b.get("max_hp")
                        if mhp != null:
                            b.max_hp = mhp * 1.5
                            b.hp = b.max_hp
                        var su = b.get("skill_uses")
                        if su != null:
                            b.skill_uses = su + 3
                        else:
                            b.set_meta("skill_uses", 3)

                if has_method("_award_skill_points"):
                    call("_award_skill_points")
                    call("_award_skill_points")
                    call("_award_skill_points")

                if world.has_method("add_event"):
                    world.add_event("bounty_destroyed", {"message": team + " Bounty destroyed! " + enemy_team + " gets massive buff!"})

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            var t = b.get("team")
            if t == null: t = b.ball_type
            teams_alive[t] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]
        return null

class EarthquakeMode extends GameMode:
	var timer: float = 0.0
	var is_shaking: bool = false
	var shake_timer: float = 0.0

	func _init():
		name = "Earthquake"
		description = "Periodically shakes the screen and applies random impulses to all entities."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		for b in balls:
			var alive = false
			if typeof(b) == TYPE_DICTIONARY:
				alive = b.get("alive", false)
			else:
				alive = b.alive if "alive" in b else false

			if not alive:
				if not b in world.dead_balls:
					if typeof(b) == TYPE_DICTIONARY:
						b["time_since_death"] = 0.0
					elif "time_since_death" in b:
						b.time_since_death = 0.0
					world.get_meta("dead_balls").append(b)
				else:
					if typeof(b) == TYPE_DICTIONARY:
						b["time_since_death"] = b.get("time_since_death", 0.0) + delta
					elif "time_since_death" in b:
						b.time_since_death += delta

		if is_shaking:
			shake_timer -= delta
			if shake_timer <= 0.0:
				is_shaking = false
			else:
				for b in balls:
					var hp = 0
					if typeof(b) == TYPE_DICTIONARY:
						hp = b.get("hp", 0)
					else:
						hp = b.hp if "hp" in b else 0
					if hp > 0:
						if typeof(b) == TYPE_DICTIONARY:
							b["x"] = b.get("x", 0.0) + randf_range(-50.0, 50.0) * delta
							b["y"] = b.get("y", 0.0) + randf_range(-50.0, 50.0) * delta
							if b.has("vx"):
								b["vx"] += randf_range(-50.0, 50.0)
							if b.has("vy"):
								b["vy"] += randf_range(-50.0, 50.0)
						else:
							if "x" in b: b.x += randf_range(-50.0, 50.0) * delta
							if "y" in b: b.y += randf_range(-50.0, 50.0) * delta
							if "vx" in b: b.vx += randf_range(-50.0, 50.0)
							if "vy" in b: b.vy += randf_range(-50.0, 50.0)

				if world != null and "arena" in world and world.arena != null:
					if "hazards" in world.arena:
						for hazard in world.arena.hazards:
							if typeof(hazard) == TYPE_DICTIONARY:
								hazard["x"] = hazard.get("x", 0.0) + randf_range(-20.0, 20.0) * delta
								hazard["y"] = hazard.get("y", 0.0) + randf_range(-20.0, 20.0) * delta
							else:
								if "x" in hazard: hazard.x += randf_range(-20.0, 20.0) * delta
								if "y" in hazard: hazard.y += randf_range(-20.0, 20.0) * delta
					if "items" in world.arena:
						for item in world.arena.items:
							if typeof(item) == TYPE_DICTIONARY:
								item["x"] = item.get("x", 0.0) + randf_range(-20.0, 20.0) * delta
								item["y"] = item.get("y", 0.0) + randf_range(-20.0, 20.0) * delta
							else:
								if "x" in item: item.x += randf_range(-20.0, 20.0) * delta
								if "y" in item: item.y += randf_range(-20.0, 20.0) * delta
		else:
			timer += delta
			if timer > 10.0 and randf() < 0.2 * delta:
				timer = 0.0
				is_shaking = true
				shake_timer = randf_range(2.0, 5.0)
				if world != null and world.has_method("add_event"):
					world.add_event("earthquake", {"type": "earthquake", "intensity": shake_timer / 2.0})


class ShiftingMazeMode extends GameMode:
	var walls: Array = []
	var maze_scale: float = 1.0
	var shrink_rate: float = 0.01
	var wall_damage_per_second: float = 50.0

	func _init() -> void:
		super._init()
		name = "Shifting Maze"
		description = "The arena starts as a complex maze that slowly shifts and shrinks. Walls deal damage."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		var arena_width = 1000.0
		var arena_height = 1000.0
		if "arena" in world and world.arena != null:
			if "width" in world.arena: arena_width = float(world.arena.width)
			if "height" in world.arena: arena_height = float(world.arena.height)

		maze_scale = 1.0
		walls.clear()

		var cell_size = 200.0
		var cols = int(arena_width / cell_size)
		var rows = int(arena_height / cell_size)

		for c in range(cols):
			for r in range(rows):
				if randf() > 0.5:
					walls.append({
						"x": c * cell_size,
						"y": r * cell_size,
						"width": cell_size,
						"height": 20.0,
						"dx": randf_range(-10.0, 10.0),
						"dy": randf_range(-10.0, 10.0)
					})
				else:
					walls.append({
						"x": c * cell_size,
						"y": r * cell_size,
						"width": 20.0,
						"height": cell_size,
						"dx": randf_range(-10.0, 10.0),
						"dy": randf_range(-10.0, 10.0)
					})

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		if maze_scale > 0.2:
			maze_scale -= shrink_rate * delta

		var arena_width = 1000.0
		var arena_height = 1000.0
		if "arena" in world and world.arena != null:
			if "width" in world.arena: arena_width = float(world.arena.width)
			if "height" in world.arena: arena_height = float(world.arena.height)

		var center_x = arena_width / 2.0
		var center_y = arena_height / 2.0

		for w in walls:
			w["x"] += w["dx"] * delta
			w["y"] += w["dy"] * delta

		for b in balls:
			if not b.alive:
				continue

			var bx = 0.0
			var by = 0.0
			if "x" in b: bx = float(b.x)
			if "y" in b: by = float(b.y)
			var br = 20.0
			if "radius" in b: br = float(b.radius)

			var touching_wall = false
			for w in walls:
				var wx = center_x + (w["x"] - center_x) * maze_scale
				var wy = center_y + (w["y"] - center_y) * maze_scale
				var ww = max(5.0, w["width"] * maze_scale)
				var wh = max(5.0, w["height"] * maze_scale)

				var nearest_x = clamp(bx, wx, wx + ww)
				var nearest_y = clamp(by, wy, wy + wh)

				var dist_sq = (bx - nearest_x) * (bx - nearest_x) + (by - nearest_y) * (by - nearest_y)
				if dist_sq < br * br:
					touching_wall = true
					break

			if touching_wall:
				var dmg = wall_damage_per_second * delta
				if b.has_method("take_damage"):
					b.take_damage(dmg, "maze_wall")
				else:
					if "hp" in b:
						b.hp -= dmg

				if "hp" in b and b.hp <= 0:
					b.alive = false

	func check_winner(world, balls: Array):
		var alive_count = 0
		var last_alive = null
		for b in balls:
			if b.alive:
				alive_count += 1
				last_alive = b

		if alive_count == 1:
			if "ball_type" in last_alive:
				return last_alive.ball_type
			return "Unknown"
		elif alive_count == 0:
			return "Draw"

		return null


class GravityWellMode extends GameMode:
    var spawn_timer = 0.0

    func _init():
        name = "Gravity Well"
        description = "Random gravity wells spawn in the arena, pulling nearby balls towards their center and slightly damaging them over time."

    func setup(world, balls):
        super.setup(world, balls)
        if not "hazards" in world.arena:
            world.arena.hazards = []
        spawn_timer = 0.0

    func tick(world, balls, delta = 0.016):
        super.tick(world, balls, delta)

        spawn_timer += delta
        if spawn_timer >= 5.0:
            spawn_timer = 0.0

            var arena_width = 2000.0
            var arena_height = 2000.0
            if "width" in world.arena:
                arena_width = world.arena.width
            if "height" in world.arena:
                arena_height = world.arena.height

            var x = randf_range(200.0, arena_width - 200.0)
            var y = randf_range(200.0, arena_height - 200.0)

            var h_id = 9000 + world.arena.hazards.size() + (randi() % 1000)

            var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
            var gw = Hazard.new(h_id, x, y, randf_range(150.0, 300.0), "gravity_well", 10.0)
            world.arena.hazards.append(gw)

            var gw_hazards = []
            for h in world.arena.hazards:
                if h.kind == "gravity_well":
                    gw_hazards.append(h)

            if gw_hazards.size() > 5:
                var oldest_gw = gw_hazards[0]
                world.arena.hazards.erase(oldest_gw)


class SupernovaMode extends GameMode:
    var supernova_radius = 50.0
    var supernova_exploded = false
    var explosion_timer = 0.0
    var heat_multiplier = 1.0

    func _init() -> void:
        name = "Supernova"
        description = "Balls take rapidly scaling heat damage as they approach the center. Eventually, the supernova explodes, knocking survivors away."


    func tick(world, balls: Array, delta: float = 0.016) -> void:
        # Evaluate crowd system
        if world != null and world.has_method("get_node") and world.has_node("CrowdSystem"):
            var crowd = world.get_node("CrowdSystem")
            var kill_log = []
            if "kill_log" in world:
                kill_log = world.kill_log
            var current_tick = 0
            if "tick" in world:
                current_tick = world.tick
            crowd.tick(balls, kill_log, current_tick)

        if not "dead_balls" in world:
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
        for b in balls:
            if not b.alive:
                if not world.get_meta("dead_balls").has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.get_meta("dead_balls").append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        var arena_width = 1000.0
        var arena_height = 1000.0
        if world != null and "arena" in world and world.arena != null:
            if "width" in world.arena:
                arena_width = world.arena.width
            if "height" in world.arena:
                arena_height = world.arena.height

        var center_x = arena_width / 2.0
        var center_y = arena_height / 2.0

        if not supernova_exploded:
            supernova_radius += 2.0 * delta
            explosion_timer += delta

            # Explosion triggers at e.g. 20 seconds
            if explosion_timer >= 20.0:
                supernova_exploded = true
                explosion_timer = 0.0
                # Trigger knockback for all alive balls
                for b in balls:
                    if b.alive and b.ball_type != "spectator":
                        var dx = b.x - center_x
                        var dy = b.y - center_y
                        var dist = sqrt(dx * dx + dy * dy)
                        if dist > 0:
                            # Massive outward knockback force
                            var knockback = 50000.0 / max(dist, 10.0)
                            if "vx" in b:
                                b.vx += (dx / dist) * knockback
                            if "vy" in b:
                                b.vy += (dy / dist) * knockback

        for b in balls:
            if b.alive and b.ball_type != "spectator":
                var dx = center_x - b.x
                var dy = center_y - b.y
                var dist = sqrt(dx * dx + dy * dy)

                if not supernova_exploded:
                    # Pull towards center
                    if dist > 0:
                        var pull_strength = 20000.0 / (dist * dist)
                        var radius_multiplier = supernova_radius / 50.0
                        pull_strength *= radius_multiplier
                        pull_strength = min(pull_strength, 150.0 * radius_multiplier)

                        b.x += (dx / dist) * pull_strength * delta
                        b.y += (dy / dist) * pull_strength * delta

                    # Heat damage
                    var max_dist = max(arena_width, arena_height) / 2.0
                    if dist < max_dist:
                        var damage_intensity = (max_dist - dist) / max_dist
                        var heat_damage = 5.0 * pow(damage_intensity, 3) * heat_multiplier * delta
                        if "hp" in b:
                            b.hp -= heat_damage
                            if b.hp <= 0:
                                b.hp = 0
                                b.alive = false

    func check_winner(world, balls: Array):
        var alive = []
        for b in balls:
            if b.alive and b.ball_type != "spectator":
                alive.append(b)

        if alive.size() == 0:
            return "Draw"

        var teams_alive = {}
        for b in alive:
            if "team" in b:
                teams_alive[b.team] = true
            else:
                teams_alive[b.ball_type] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        if alive.size() == 1:
            return alive[0].ball_type

        return null


class DayNightMode extends GameMode:
    var timer = 0.0
    var phase_duration = 10.0

    func _init():
        super._init()
        name = "Day/Night Cycle"
        description = "Periodically toggles day and night, affecting ball behavior and visibility."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if world != null and "arena" in world:
            world.arena.is_night = false
        timer = 0.0

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if world != null and "arena" in world:
            timer += delta
            if timer >= phase_duration:
                timer = 0.0
                if "is_night" in world.arena:
                    world.arena.is_night = not world.arena.is_night
                else:
                    world.arena.is_night = true


class GuildVsGuildMode extends GameMode:
    var guilds = {}
    var control_points = []
    var territory_captured = false

    func _init():
        name = "gvg"
        desc = "Guild vs Guild territory battle"

    func setup(world_ref, balls_ref: Array):
        super.setup(world_ref, balls_ref)
        guilds = {}
        control_points = [
            {"x": 200, "y": 200, "radius": 50, "owner": null, "progress": 0},
            {"x": 800, "y": 800, "radius": 50, "owner": null, "progress": 0},
            {"x": 500, "y": 500, "radius": 80, "owner": null, "progress": 0}
        ]
        territory_captured = false

        if balls.size() >= 2:
            var mid = balls.size() / 2
            var g1 = []
            var g2 = []
            for i in range(mid):
                g1.append(balls[i].get_meta("id") if balls[i].has_method("get_meta") and balls[i].has_meta("id") else balls[i].id)
            for i in range(mid, balls.size()):
                g2.append(balls[i].get_meta("id") if balls[i].has_method("get_meta") and balls[i].has_meta("id") else balls[i].id)
            guilds["GuildA"] = g1
            guilds["GuildB"] = g2

    func _tick(delta: float):
        super._tick(delta)
        if territory_captured:
            return

        for cp in control_points:
            var guild_counts = {}
            for guild in guilds.keys():
                var count = 0
                for ball in world.balls:
                    var bid = ball.get_meta("id") if ball.has_method("get_meta") and ball.has_meta("id") else ball.id
                    var balive = ball.get_meta("alive") if ball.has_method("get_meta") and ball.has_meta("alive") else ball.alive
                    if guilds[guild].has(bid) and balive:
                        var bx = ball.get_meta("x") if ball.has_method("get_meta") and ball.has_meta("x") else ball.x
                        var by = ball.get_meta("y") if ball.has_method("get_meta") and ball.has_meta("y") else ball.y
                        var dx = bx - cp["x"]
                        var dy = by - cp["y"]
                        if sqrt(dx*dx + dy*dy) <= cp["radius"]:
                            count += 1
                guild_counts[guild] = count

            var dominating_guild = null
            var max_count = 0
            for guild in guild_counts.keys():
                var count = guild_counts[guild]
                if count > max_count:
                    max_count = count
                    dominating_guild = guild
                elif count == max_count and count > 0:
                    dominating_guild = null

            if dominating_guild != null:
                if cp["owner"] != dominating_guild:
                    cp["progress"] += delta * 10
                    if cp["progress"] >= 100:
                        cp["owner"] = dominating_guild
                        cp["progress"] = 100
            else:
                cp["progress"] = max(0, cp["progress"] - delta * 5)

        var owners = []
        for cp in control_points:
            if cp["owner"] != null:
                owners.append(cp["owner"])

        var unique_owners = {}
        for o in owners:
            unique_owners[o] = true

        if owners.size() == control_points.size() and unique_owners.size() == 1:
            var winner = owners[0]
            _end_match(winner)

    func _end_match(winner_guild: String):
        territory_captured = true
        var GuildManager = load("res://src/system/guild.gd")
        if GuildManager:
            var gm = GuildManager.new()
            gm.capture_territory(winner_guild, "GvG_Arena")
            var loser = "GuildB" if winner_guild == "GuildA" else "GuildA"
            gm.record_gvg_match(winner_guild, loser, winner_guild)


class MagneticCollisionsMode extends GameMode:
	var polarity_flip_timer = 0.0

	func _init() -> void:
		name = "Magnetic Collisions"
		description = "Invisible magnetic fields pull or push balls depending on their assigned polarities. Every 10 seconds, polarities randomly flip, causing sudden tactical shifts and chaotic collisions."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)

		# Setup magnetic fields as invisible hazards
		if "arena" in world and world.arena != null:
			if not "hazards" in world.arena:
				world.arena.hazards = []

			var arena_width = 1000.0
			var arena_height = 1000.0
			if "width" in world.arena:
				arena_width = world.arena.width
			if "height" in world.arena:
				arena_height = world.arena.height

			var HazardClass = load("res://src/arena/procedural_arena.gd").Hazard if ResourceLoader.exists("res://src/arena/procedural_arena.gd") else null

			for i in range(5):
				var x = randf_range(200.0, arena_width - 200.0)
				var y = randf_range(200.0, arena_height - 200.0)
				var radius = randf_range(150.0, 300.0)
				var kind = "magnetic_field_positive" if randf() > 0.5 else "magnetic_field_negative"

				if HazardClass != null:
					var h = HazardClass.new(20000 + i, x, y, radius, kind, 0.0)
					if "invisible" in h: h.invisible = true
					elif h.has_method("set_meta"): h.set_meta("invisible", true)
					world.arena.hazards.append(h)
				else:
					var h = {"id": 20000 + i, "x": x, "y": y, "radius": radius, "kind": kind, "damage": 0.0, "invisible": true}
					world.arena.hazards.append(h)

		# Assign random polarities to balls
		for b in balls:
			var is_dict = typeof(b) == TYPE_DICTIONARY
			var b_alive = b.get("alive", true) if is_dict else b.alive
			var b_type = b.get("ball_type", "") if is_dict else b.ball_type

			if b_alive and b_type != "spectator":
				var start_polarity = "positive" if randf() > 0.5 else "negative"
				if is_dict:
					b["polarity"] = start_polarity
				else:
					if b.has_method("set_meta"): b.set_meta("polarity", start_polarity)
					elif "polarity" in b: b.polarity = start_polarity

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		polarity_flip_timer += delta
		if polarity_flip_timer >= 10.0:
			polarity_flip_timer = 0.0
			for b in balls:
				var is_dict = typeof(b) == TYPE_DICTIONARY
				var b_alive = b.get("alive", true) if is_dict else b.alive
				var b_type = b.get("ball_type", "") if is_dict else b.ball_type

				if b_alive and b_type != "spectator":
					var current_polarity = b.get("polarity", "positive") if is_dict else (b.get_meta("polarity") if b.has_method("get_meta") and b.has_meta("polarity") else (b.polarity if "polarity" in b else "positive"))
					var new_polarity = "negative" if current_polarity == "positive" else "positive"

					if is_dict:
						b["polarity"] = new_polarity
					else:
						if b.has_method("set_meta"): b.set_meta("polarity", new_polarity)
						elif "polarity" in b: b.polarity = new_polarity

			if world != null and world.has_method("add_event"):
				world.add_event("polarity_flip", {"message": "Polarities have flipped!"})

		# Apply magnetic forces
		if "arena" in world and world.arena != null and "hazards" in world.arena:
			for h in world.arena.hazards:
				var h_kind = h.get("kind", "") if typeof(h) == TYPE_DICTIONARY else h.kind
				if h_kind == "magnetic_field_positive" or h_kind == "magnetic_field_negative":
					var h_polarity = "positive" if "positive" in h_kind else "negative"
					var hx = h.get("x", 0.0) if typeof(h) == TYPE_DICTIONARY else h.x
					var hy = h.get("y", 0.0) if typeof(h) == TYPE_DICTIONARY else h.y
					var hr = h.get("radius", 0.0) if typeof(h) == TYPE_DICTIONARY else h.radius

					for b in balls:
						var is_dict = typeof(b) == TYPE_DICTIONARY
						var b_alive = b.get("alive", true) if is_dict else b.alive
						var b_type = b.get("ball_type", "") if is_dict else b.ball_type

						if not b_alive or b_type == "spectator":
							continue

						var b_polarity = b.get("polarity", "positive") if is_dict else (b.get_meta("polarity") if b.has_method("get_meta") and b.has_meta("polarity") else (b.polarity if "polarity" in b else "positive"))

						var bx = b.get("x", 0.0) if is_dict else b.x
						var by = b.get("y", 0.0) if is_dict else b.y

						var dx = hx - bx
						var dy = hy - by
						var dist = sqrt(dx*dx + dy*dy)

						if dist > 0 and dist < hr:
							var force = (hr - dist) / hr * 200.0 * delta

							if h_polarity != b_polarity:
								# Attract
								if is_dict:
									b["x"] = bx + (dx / dist) * force
									b["y"] = by + (dy / dist) * force
								else:
									b.x += (dx / dist) * force
									b.y += (dy / dist) * force
							else:
								# Repel
								if is_dict:
									b["x"] = bx - (dx / dist) * force
									b["y"] = by - (dy / dist) * force
								else:
									b.x -= (dx / dist) * force
									b.y -= (dy / dist) * force


class StaminaRegenMode extends GameMode:
    func _init() -> void:
        name = "Stamina Regen modifier"
        description = "A game mode modifier where stamina regenerates twice as fast, allowing more frequent use of stamina-based skills."

class ZeroGravityMode extends GameMode:
    func _init() -> void:
        name = "Zero Gravity"
        description = "Friction and gravity are drastically reduced, causing balls to slide around effortlessly and collisions to produce massive knockback."


class PinballMode extends GameMode:
	func _init() -> void:
		name = "Pinball Mode"
		description = "Lots of bouncy bumpers and physics-based knockback logic to push balls around the arena."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if "arena" in world and world.arena != null:
			if not "hazards" in world.arena:
				world.arena.hazards = []
			var arena_width = 1000.0
			var arena_height = 1000.0
			if "width" in world.arena:
				arena_width = world.arena.width
			if "height" in world.arena:
				arena_height = world.arena.height

			var HazardClass = load("res://src/arena/procedural_arena.gd").Hazard if ResourceLoader.exists("res://src/arena/procedural_arena.gd") else null
			for i in range(20):
				var x = randf_range(100.0, arena_width - 100.0)
				var y = randf_range(100.0, arena_height - 100.0)
				var radius = randf_range(30.0, 60.0)
				if HazardClass != null:
					var h = HazardClass.new(10000 + i, x, y, radius, "bumper", 0.0)
					world.arena.hazards.append(h)
				else:
					var h = {"id": 10000 + i, "x": x, "y": y, "radius": radius, "kind": "bumper", "damage": 0.0}
					world.arena.hazards.append(h)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)


class MirrorWallsMode extends GameMode:
    func _init():
        super._init()
        name = "Mirror Walls"
        description = "An arena event where all projectiles are reflected infinitely across mirror walls."

    func tick(world: Variant, balls: Array, delta: float = 0.016) -> void:
        super.tick(world, balls, delta)


class GeometricZoneMode extends GameMode:
	var collapse_triggered = false
	var zone_x = 500.0
	var zone_y = 500.0
	var zone_radius = 500.0
	var min_zone_radius = 50.0
	var shrink_rate = 15.0
	var outside_damage_per_second = 20.0
	var zone_target_x = 500.0
	var zone_target_y = 500.0

	var shape_timer = 0.0
	var current_shape = "circle"
	var shapes = ["circle", "rectangle", "triangle", "split"]
	var split_zones = []
	var rng = RandomNumberGenerator.new()

	func _init():
		super._init()
		rng.randomize()
		name = "Geometric Zone"
		description = "The safe zone shrinks into varied geometric shapes or splits temporarily to disrupt camping."

	func setup(world, balls):
		super.setup(world, balls)
		collapse_triggered = false

		var arena_width = 1000
		var arena_height = 1000
		if "arena" in world and world.arena:
			if "width" in world.arena: arena_width = world.arena.width
			if "height" in world.arena: arena_height = world.arena.height

		zone_x = arena_width / 2.0
		zone_y = arena_height / 2.0
		zone_target_x = zone_x
		zone_target_y = zone_y
		zone_radius = min(arena_width, arena_height) / 2.0
		min_zone_radius = 50.0

		current_shape = shapes[rng.randi() % 3]

		var valid_balls = []
		for b in balls:
			var b_type = b.ball_type if "ball_type" in b else null
			if b_type != "spectator":
				valid_balls.append(b)

		for i in range(valid_balls.size()):
			var b = valid_balls[i]
			if i >= 20:
				b.ball_type = "spectator"
				b.alive = false
			else:
				b.team = b.ball_type

		if not ("dead_balls" in world):
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

	func sign_tri(p1x, p1y, p2x, p2y, p3x, p3y):
		return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)

	func is_inside_zone(b_x, b_y, cx, cy, radius, shape):
		if shape == "circle":
			var dx = b_x - cx
			var dy = b_y - cy
			return sqrt(dx*dx + dy*dy) <= radius
		elif shape == "rectangle":
			var dx = abs(b_x - cx)
			var dy = abs(b_y - cy)
			return dx <= radius and dy <= radius
		elif shape == "triangle":
			var v0x = cx
			var v0y = cy - radius
			var v1x = cx - radius * 0.866
			var v1y = cy + radius * 0.5
			var v2x = cx + radius * 0.866
			var v2y = cy + radius * 0.5

			var d1 = sign_tri(b_x, b_y, v0x, v0y, v1x, v1y)
			var d2 = sign_tri(b_x, b_y, v1x, v1y, v2x, v2y)
			var d3 = sign_tri(b_x, b_y, v2x, v2y, v0x, v0y)

			var has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
			var has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
			return not (has_neg and has_pos)
		return true

	func tick(world, balls, delta=0.016):
		if not ("dead_balls" in world):
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		for b in balls:
			if not (b.alive if "alive" in b else false):
				if not (b in world.dead_balls):
					b.time_since_death = 0.0
					world.get_meta("dead_balls").append(b)
				else:
					b.time_since_death += delta

		shape_timer += delta
		if shape_timer > 15.0:
			shape_timer = 0.0
			current_shape = shapes[rng.randi() % shapes.size()]
			if current_shape == "split":
				var offset = max(100.0, zone_radius * 0.5)
				split_zones = [
					{"x": zone_x - offset, "y": zone_y, "radius": zone_radius * 0.6},
					{"x": zone_x + offset, "y": zone_y, "radius": zone_radius * 0.6}
				]
			if "add_event" in world and world.has_method("add_event"):
				world.add_event("zone_shape_change", {"type": "zone_shape_change", "message": "The zone shifts to " + current_shape + "!"})

		var dx = zone_target_x - zone_x
		var dy = zone_target_y - zone_y
		var dist = sqrt(dx*dx + dy*dy)
		if dist > 5.0:
			var move_speed = 10.0
			zone_x += (dx / dist) * move_speed * delta
			zone_y += (dy / dist) * move_speed * delta
		else:
			var arena_width = 1000
			var arena_height = 1000
			if "arena" in world and world.arena:
				if "width" in world.arena: arena_width = world.arena.width
				if "height" in world.arena: arena_height = world.arena.height
			var buffer = max(100.0, zone_radius * 0.5)
			zone_target_x = rng.randf_range(buffer, arena_width - buffer)
			zone_target_y = rng.randf_range(buffer, arena_height - buffer)

		if zone_radius > min_zone_radius:
			zone_radius -= shrink_rate * delta
			if zone_radius <= min_zone_radius:
				zone_radius = min_zone_radius
				if not collapse_triggered:
					collapse_triggered = true
					if "add_event" in world and world.has_method("add_event"):
						world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
		elif collapse_triggered:
			if zone_radius > 0:
				zone_radius -= shrink_rate * delta
				if zone_radius < 0:
					zone_radius = 0.0

			for b in balls:
				if (b.alive if "alive" in b else false) and (b.ball_type if "ball_type" in b else null) != "spectator":
					var b_dx = zone_x - b.x
					var b_dy = zone_y - b.y
					var b_dist = sqrt(b_dx*b_dx + b_dy*b_dy)
					if b_dist > 0:
						var pull_strength = 2000.0
						if not ("vx" in b): b.vx = 0.0
						if not ("vy" in b): b.vy = 0.0
						b.vx += (b_dx / b_dist) * pull_strength * delta
						b.vy += (b_dy / b_dist) * pull_strength * delta

		if current_shape == "split":
			for i in range(split_zones.size()):
				split_zones[i]["radius"] -= shrink_rate * 0.6 * delta
				if split_zones[i]["radius"] < 20.0:
					split_zones[i]["radius"] = 20.0

		if "arena" in world and world.arena and "danger_grid" in world.arena:
			var current_tick = world.current_tick if "current_tick" in world else 0
			var last_tick = get_meta("last_danger_tick") if has_meta("last_danger_tick") else -1
			if current_tick != last_tick:
				set_meta("last_danger_tick", current_tick)
				if current_tick % 10 == 0:
					world.arena.danger_grid.clear()

					var grid_w = int(world.arena.width / 100) + 1 if "width" in world.arena else 11
					var grid_h = int(world.arena.height / 100) + 1 if "height" in world.arena else 11

					for i in range(grid_w):
						for j in range(grid_h):
							var cx = i * 100 + 50
							var cy = j * 100 + 50
							var key = Vector2(i, j)

							var safe = false
							if current_shape == "split":
								for sz in split_zones:
									if is_inside_zone(cx, cy, sz["x"], sz["y"], sz["radius"], "circle"):
										safe = true
										break
							else:
								if is_inside_zone(cx, cy, zone_x, zone_y, zone_radius, current_shape):
									safe = true

							if not safe:
								var current = 0.0
								if world.arena.danger_grid.has(key):
									current = world.arena.danger_grid[key]
								world.arena.danger_grid[key] = current + (outside_damage_per_second / 10.0)

		var mult = 10.0 if collapse_triggered else 1.0
		var damage_this_tick = outside_damage_per_second * mult * delta
		for b in balls:
			if (b.alive if "alive" in b else false) and (b.ball_type if "ball_type" in b else null) != "spectator":
				var safe = false
				if current_shape == "split":
					for sz in split_zones:
						if is_inside_zone(b.x, b.y, sz["x"], sz["y"], sz["radius"], "circle"):
							safe = true
							break
				else:
					if is_inside_zone(b.x, b.y, zone_x, zone_y, zone_radius, current_shape):
						safe = true

				if not safe:
					b.hp -= damage_this_tick
					if b.hp <= 0:
						b.alive = false
						b.hp = 0
						b.killer = "Geometric Zone"


class BodySwapMode extends GameMode:
	var swap_timer: float = 0.0
	var swap_interval: float = 10.0

	func _init() -> void:
		name = "Body Swap"
		description = "Periodically swaps player controls/positions to add confusion."

	func setup(world, balls: Array) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		for b in balls:
			var alive = false
			if "alive" in b: alive = b.alive
			elif b.has_method("get_meta") and b.has_meta("alive"): alive = b.get_meta("alive")

			if not alive:
				if not b in world.dead_balls:
					if "time_since_death" in b: b.time_since_death = 0.0
					elif b.has_method("set_meta"): b.set_meta("time_since_death", 0.0)
					world.get_meta("dead_balls").append(b)
				else:
					if "time_since_death" in b: b.time_since_death += delta
					elif b.has_method("set_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

		swap_timer += delta
		if swap_timer >= swap_interval:
			swap_timer = 0.0
			var alive_balls = []
			for b in balls:
				var alive = false
				if "alive" in b: alive = b.alive
				elif b.has_method("get_meta") and b.has_meta("alive"): alive = b.get_meta("alive")
				if alive:
					alive_balls.append(b)

			if alive_balls.size() >= 2:
				alive_balls.shuffle()
				var i = 0
				while i < alive_balls.size() - 1:
					var b1 = alive_balls[i]
					var b2 = alive_balls[i+1]

					var temp_x = b1.x
					var temp_y = b1.y
					b1.x = b2.x
					b1.y = b2.y
					b2.x = temp_x
					b2.y = temp_y

					var vx1 = 0.0; var vy1 = 0.0
					var vx2 = 0.0; var vy2 = 0.0
					if "vx" in b1: vx1 = b1.vx; vy1 = b1.vy
					elif b1.has_method("get_meta") and b1.has_meta("vx"): vx1 = b1.get_meta("vx"); vy1 = b1.get_meta("vy")
					if "vx" in b2: vx2 = b2.vx; vy2 = b2.vy
					elif b2.has_method("get_meta") and b2.has_meta("vx"): vx2 = b2.get_meta("vx"); vy2 = b2.get_meta("vy")

					if "vx" in b1: b1.vx = vx2; b1.vy = vy2
					elif b1.has_method("set_meta"): b1.set_meta("vx", vx2); b1.set_meta("vy", vy2)

					if "vx" in b2: b2.vx = vx1; b2.vy = vy1
					elif b2.has_method("set_meta"): b2.set_meta("vx", vx1); b2.set_meta("vy", vy1)

					if world.has_method("add_event"):
						world.add_event("body_swap", {"type": "body_swap", "message": "Body Swap! Players swap places!"})
					i += 2

class TugOfWarMode extends GameMode:
	var payload = null
	var red_goal_x: float = 100.0
	var blue_goal_x: float = 900.0
	var timer: float = 180.0

	func _init() -> void:
		name = "Tug of War"
		description = "A single payload is centered. Both teams fight to push/pull the payload to the opposing team's goal."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

		var valid_balls = []
		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				if b.get("ball_type", "") != "spectator":
					valid_balls.append(b)
			else:
				if b.ball_type != "spectator":
					valid_balls.append(b)

		var mid = valid_balls.size() / 2
		for i in range(valid_balls.size()):
			var b = valid_balls[i]
			if typeof(b) == TYPE_DICTIONARY:
				b["team"] = "Red" if i < mid else "Blue"
			else:
				b.team = "Red" if i < mid else "Blue"

		var arena_width = 1000.0
		var arena_height = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
			else:
				arena_width = world.arena.get("width")
				arena_height = world.arena.get("height")

		red_goal_x = 100.0
		blue_goal_x = arena_width - 100.0

		payload = {
			"ball_type": "payload",
			"is_payload": true,
			"is_invulnerable": true,
			"speed": 0.0,
			"base_speed": 0.0,
			"damage": 0.0,
			"base_damage": 0.0,
			"max_hp": 10000.0,
			"hp": 10000.0,
			"x": arena_width / 2.0,
			"y": arena_height / 2.0,
			"alive": true,
			"team": "Neutral",
			"radius": 20.0
		}
		balls.append(payload)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if timer > 0.0:
			timer -= delta

		var arena_width = 1000.0
		if "arena" in world and world.arena:
			if typeof(world.arena) == TYPE_DICTIONARY:
				arena_width = world.arena.get("width", 1000.0)
			else:
				arena_width = world.arena.get("width")

		if payload != null:
			var is_alive = payload.get("alive", false) if typeof(payload) == TYPE_DICTIONARY else payload.alive
			if is_alive:
				var red_count = 0
				var blue_count = 0

				var px = payload.get("x", 0) if typeof(payload) == TYPE_DICTIONARY else payload.x
				var py = payload.get("y", 0) if typeof(payload) == TYPE_DICTIONARY else payload.y

				for b in balls:
					if typeof(b) == TYPE_DICTIONARY and b == payload:
						continue
					elif typeof(b) != TYPE_DICTIONARY and b == payload:
						continue

					var b_alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
					var b_type = b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else b.ball_type

					if not b_alive or b_type == "spectator":
						continue

					var bx = b.get("x", 0) if typeof(b) == TYPE_DICTIONARY else b.x
					var by = b.get("y", 0) if typeof(b) == TYPE_DICTIONARY else b.y

					var dx = bx - px
					var dy = by - py
					var dist = sqrt(dx * dx + dy * dy)

					if dist < 150.0:
						var team = b.get("team", "") if typeof(b) == TYPE_DICTIONARY else b.team
						if team == "Red":
							red_count += 1
						elif team == "Blue":
							blue_count += 1

				var move_speed = 50.0

				if red_count > blue_count:
					if typeof(payload) == TYPE_DICTIONARY:
						payload["x"] += move_speed * delta * (red_count - blue_count)
					else:
						payload.x += move_speed * delta * (red_count - blue_count)
				elif blue_count > red_count:
					if typeof(payload) == TYPE_DICTIONARY:
						payload["x"] -= move_speed * delta * (blue_count - red_count)
					else:
						payload.x -= move_speed * delta * (blue_count - red_count)

				px = payload.get("x", 0) if typeof(payload) == TYPE_DICTIONARY else payload.x
				if px < 50.0:
					if typeof(payload) == TYPE_DICTIONARY: payload["x"] = 50.0
					else: payload.x = 50.0
				elif px > arena_width - 50.0:
					if typeof(payload) == TYPE_DICTIONARY: payload["x"] = arena_width - 50.0
					else: payload.x = arena_width - 50.0

	func check_winner(world, balls: Array):
		if payload == null:
			return null

		var px = payload.get("x", 0) if typeof(payload) == TYPE_DICTIONARY else payload.x

		if px <= red_goal_x:
			return "Blue"
		elif px >= blue_goal_x:
			return "Red"

		if timer <= 0.0:
			var arena_width = 1000.0
			if "arena" in world and world.arena:
				if typeof(world.arena) == TYPE_DICTIONARY:
					arena_width = world.arena.get("width", 1000.0)
				else:
					arena_width = world.arena.get("width")

			var center_x = arena_width / 2.0

			if px > center_x:
				return "Red"
			elif px < center_x:
				return "Blue"
			else:
				return "Draw"

		return null



class UnstablePortalsEventMode extends GameMode:
	var portals: Array = []
	var spawn_timer: float = 0.0

	func _init() -> void:
		name = "Unstable Portals Event"
		description = "Unstable portals spawn randomly. They occasionally collapse, releasing a shockwave that damages and knocks back nearby players."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		spawn_timer += delta
		if spawn_timer > 5.0:
			spawn_timer = 0.0
			if randf() < 0.5:
				var arena_w = 800.0
				var arena_h = 600.0
				if world != null and "arena" in world:
					if "width" in world.arena: arena_w = world.arena.width
					if "height" in world.arena: arena_h = world.arena.height
				portals.append({
					"x": 100.0 + randf() * (arena_w - 200.0),
					"y": 100.0 + randf() * (arena_h - 200.0),
					"timer": 3.0 + randf() * 4.0,
					"active": true
				})
				if world != null and world.has_method("add_event"):
					world.add_event("portal_spawn", {"message": "An unstable portal has appeared!"})

		for p in portals:
			if not p["active"]:
				continue
			p["timer"] -= delta
			if p["timer"] <= 0:
				p["active"] = false
				if world != null and world.has_method("add_event"):
					world.add_event("portal_collapse", {"message": "A portal collapsed!", "x": p["x"], "y": p["y"]})
					world.add_event("explosion", {"x": p["x"], "y": p["y"], "radius": 150.0, "damage": 30.0})

				var arena_w = 800.0
				var arena_h = 600.0
				if world != null and "arena" in world:
					if "width" in world.arena: arena_w = float(world.arena.width)
					if "height" in world.arena: arena_h = float(world.arena.height)

				for b in balls:
					var alive = false
					if typeof(b) == TYPE_DICTIONARY:
						alive = b.get("alive", false)
					else:
						alive = b.alive

					if not alive:
						continue

					var bx = 0.0
					var by = 0.0

					if typeof(b) == TYPE_DICTIONARY:
						bx = float(b.get("x", 0.0))
						by = float(b.get("y", 0.0))
					else:
						bx = float(b.x)
						by = float(b.y)

					var dx = bx - p["x"]
					var dy = by - p["y"]
					var dist = sqrt(dx * dx + dy * dy)

					if dist < 150.0:
						var damage = 30.0
						if typeof(b) == TYPE_DICTIONARY:
							if b.has("hp"):
								b["hp"] -= damage
						else:
							if b.has_method("take_damage"):
								b.take_damage(damage)
							elif "hp" in b:
								b.hp -= damage

						if dist > 0.0001:
							var nx = dx / dist
							var ny = dy / dist
							var knockback = 500.0 * (1.0 - dist / 150.0)

							var new_x = max(0.0, min(arena_w, bx + nx * knockback * delta))
							var new_y = max(0.0, min(arena_h, by + ny * knockback * delta))

							if typeof(b) == TYPE_DICTIONARY:
								b["x"] = new_x
								b["y"] = new_y
							else:
								b.x = new_x
								b.y = new_y

		var new_portals = []
		for p in portals:
			if p["active"]:
				new_portals.append(p)
		portals = new_portals


class MinefieldEventMode extends GameMode:
	var event_timer: float = 0.0
	var event_active: bool = false
	var event_duration: float = 0.0
	var mines: Array = []

	func _init() -> void:
		name = "Minefield Event"
		description = "A random event where multiple mines appear, detonating on contact."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not event_active:
			event_timer += delta

		if not event_active and event_timer > 20.0:
			if randf() < 0.2:  # 20% chance every 20 seconds to trigger
				event_active = true
				event_duration = 15.0
				event_timer = 0.0
				mines = []
				# Spawn some mines
				var num_mines = (randi() % 6) + 5 # 5 to 10 mines
				for i in range(num_mines):
					mines.append({
						"x": 100.0 + randf() * 600.0,
						"y": 100.0 + randf() * 400.0,
						"radius": 15.0,
						"damage": 50.0,
						"active": true,
						"visible": randf() > 0.5
					})
				if world != null and world.has_method("add_event"):
					world.add_event("minefield_event", {"message": "MINEFIELD EVENT! Watch your step!"})
			else:
				event_timer = 0.0

		if event_active:
			event_duration -= delta
			if event_duration <= 0:
				event_active = false
				event_timer = 0.0
				mines = []
				if world != null and world.has_method("add_event"):
					world.add_event("minefield_event_ended", {"message": "Minefield cleared!"})

			for b in balls:
				var alive = false
				if typeof(b) == TYPE_DICTIONARY:
					alive = b.get("alive", false)
				else:
					alive = b.alive

				if not alive:
					continue

				var bx = 0.0
				var by = 0.0
				var bradius = 0.0

				if typeof(b) == TYPE_DICTIONARY:
					bx = b.get("x", 0.0)
					by = b.get("y", 0.0)
					bradius = b.get("radius", 0.0)
				else:
					bx = b.x
					by = b.y
					bradius = b.radius

				for m in mines:
					if not m["active"]:
						continue
					var dx = bx - m["x"]
					var dy = by - m["y"]
					var dist = sqrt(dx * dx + dy * dy)
					if dist < bradius + m["radius"]:
						m["active"] = false
						if typeof(b) == TYPE_DICTIONARY:
							if b.has("hp"):
								b["hp"] -= m["damage"]
						else:
							if b.has_method("take_damage"):
								b.take_damage(m["damage"])
							elif "hp" in b:
								b.hp -= m["damage"]
						if world != null and world.has_method("add_event"):
							world.add_event("mine_explosion", {"x": m["x"], "y": m["y"]})



class StaminaSpeedMode extends GameMode:
	func _init():
		name = "Stamina Speed"
		description = "Max stamina dictates base speed. Everyone starts with 200 max stamina but taking damage permanently reduces maximum stamina for the rest of the round."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				b["max_stamina"] = 200.0
				b["stamina"] = 200.0
				b["base_speed"] = 200.0
				b["speed"] = 200.0
				b["prev_hp"] = b.get("hp", 100.0)
			else:
				b.set("max_stamina", 200.0)
				b.set("stamina", 200.0)
				b.set("base_speed", 200.0)
				b.set("speed", 200.0)
				b.set_meta("prev_hp", b.get("hp") if "hp" in b else 100.0)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		for b in balls:
			var current_hp = 100.0
			var prev_hp = 100.0
			var max_stam = 200.0

			if typeof(b) == TYPE_DICTIONARY:
				current_hp = b.get("hp", 100.0)
				prev_hp = b.get("prev_hp", current_hp)
				max_stam = b.get("max_stamina", 200.0)

				if current_hp < prev_hp:
					var damage = prev_hp - current_hp
					max_stam = max(10.0, max_stam - damage)
					b["max_stamina"] = max_stam
					b["stamina"] = min(b.get("stamina", max_stam), max_stam)

				b["prev_hp"] = current_hp
				b["base_speed"] = max_stam
			else:
				current_hp = b.get("hp") if "hp" in b else 100.0
				prev_hp = b.get_meta("prev_hp") if b.has_meta("prev_hp") else current_hp
				max_stam = b.get("max_stamina") if "max_stamina" in b else 200.0

				if current_hp < prev_hp:
					var damage = prev_hp - current_hp
					max_stam = max(10.0, max_stam - damage)
					b.set("max_stamina", max_stam)
					var stam = b.get("stamina") if "stamina" in b else max_stam
					b.set("stamina", min(stam, max_stam))

				b.set_meta("prev_hp", current_hp)
				b.set("base_speed", max_stam)



class FactoryMode extends GameMode:
	func _init():
		super._init()
		self.name = "Factory"
		self.description = "Conveyor belts push you around!"
		self.points_for_kill = 10
		self.arena = ArenaTypes.FactoryArena.new()

	func update(world, delta: float):
		super.update(world, delta)

		if not "arena" in world or not world.arena or not "hazards" in world.arena:
			return

		var conveyors = []
		for h in world.arena.hazards:
			if h.kind == "conveyor_belt":
				conveyors.append(h)

		if conveyors.size() == 0:
			return

		for c in conveyors:
			if "items" in world:
				for item in world.items:
					var dx = c.x - item.x
					var dy = c.y - item.y
					if dx*dx + dy*dy < c.radius * c.radius:
						item.x += c.direction_vector[0] * c.speed_magnitude * delta
						item.y += c.direction_vector[1] * c.speed_magnitude * delta

			for h in world.arena.hazards:
				if h == c or h.kind == "conveyor_belt":
					continue
				var dx = c.x - h.x
				var dy = c.y - h.y
				if dx*dx + dy*dy < c.radius * c.radius:
					h.x += c.direction_vector[0] * c.speed_magnitude * delta
					h.y += c.direction_vector[1] * c.speed_magnitude * delta

			if "balls" in world:
				for b in world.balls:
					var dx = c.x - b.x
					var dy = c.y - b.y
					if dx*dx + dy*dy < c.radius * c.radius:
						b.x += c.direction_vector[0] * c.speed_magnitude * delta
						b.y += c.direction_vector[1] * c.speed_magnitude * delta

class HazardBilliardsMode extends GameMode:
	func _init() -> void:
		name = "Hazard Billiards"
		description = "Every ball starts with a reflect shield and no standard attacks work. Players must push map hazards into each other to deal damage!"

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		for b in balls:
			if typeof(b) == TYPE_DICTIONARY:
				b["damage"] = 0.0
				b["reflect_shield_active"] = true
				b["reflect_shield_timer"] = 99999.0
				b["reflect_shield_capacity"] = 99999.0
				if not b.has("mutators"):
					b["mutators"] = []
				if not b["mutators"].has("hazard_billiards"):
					b["mutators"].append("hazard_billiards")
			else:
				if "damage" in b: b.damage = 0.0
				if b.has_method("set_meta"):
					b.set_meta("reflect_shield_active", true)
					b.set_meta("reflect_shield_timer", 99999.0)
					b.set_meta("reflect_shield_capacity", 99999.0)

					var mutators = b.get_meta("mutators") if b.has_meta("mutators") else []
					if not mutators.has("hazard_billiards"):
						mutators.append("hazard_billiards")
					b.set_meta("mutators", mutators)
				if "reflect_shield_active" in b: b.reflect_shield_active = true
				if "reflect_shield_timer" in b: b.reflect_shield_timer = 99999.0
				if "reflect_shield_capacity" in b: b.reflect_shield_capacity = 99999.0

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		for b in balls:
			var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
			if not alive: continue

			if typeof(b) == TYPE_DICTIONARY:
				b["reflect_shield_active"] = true
				b["reflect_shield_timer"] = 99999.0
				b["reflect_shield_capacity"] = 99999.0
			else:
				if b.has_method("set_meta"):
					b.set_meta("reflect_shield_active", true)
					b.set_meta("reflect_shield_timer", 99999.0)
					b.set_meta("reflect_shield_capacity", 99999.0)
				if "reflect_shield_active" in b: b.reflect_shield_active = true
				if "reflect_shield_timer" in b: b.reflect_shield_timer = 99999.0
				if "reflect_shield_capacity" in b: b.reflect_shield_capacity = 99999.0

		var hazards = []
		if "arena" in world and world.arena != null:
			if "hazards" in world.arena:
				hazards = world.arena.hazards

		for i in range(hazards.size()):
			var h1 = hazards[i]
			var h1x = h1.get("x", 0.0) if typeof(h1) == TYPE_DICTIONARY else h1.x
			var h1y = h1.get("y", 0.0) if typeof(h1) == TYPE_DICTIONARY else h1.y
			var h1r = h1.get("radius", 10.0) if typeof(h1) == TYPE_DICTIONARY else h1.radius
			var h1vx = h1.get("vx", 0.0) if typeof(h1) == TYPE_DICTIONARY else (h1.vx if "vx" in h1 else 0.0)
			var h1vy = h1.get("vy", 0.0) if typeof(h1) == TYPE_DICTIONARY else (h1.vy if "vy" in h1 else 0.0)

			for j in range(i + 1, hazards.size()):
				var h2 = hazards[j]
				var h2x = h2.get("x", 0.0) if typeof(h2) == TYPE_DICTIONARY else h2.x
				var h2y = h2.get("y", 0.0) if typeof(h2) == TYPE_DICTIONARY else h2.y
				var h2r = h2.get("radius", 10.0) if typeof(h2) == TYPE_DICTIONARY else h2.radius
				var h2vx = h2.get("vx", 0.0) if typeof(h2) == TYPE_DICTIONARY else (h2.vx if "vx" in h2 else 0.0)
				var h2vy = h2.get("vy", 0.0) if typeof(h2) == TYPE_DICTIONARY else (h2.vy if "vy" in h2 else 0.0)

				var dx = h2x - h1x
				var dy = h2y - h1y
				var dist = sqrt(dx * dx + dy * dy)

				if dist < h1r + h2r and dist > 0.0001:
					var overlap = (h1r + h2r) - dist
					var nx = dx / dist
					var ny = dy / dist

					var new_h1x = h1x - nx * (overlap / 2.0)
					var new_h1y = h1y - ny * (overlap / 2.0)
					var new_h2x = h2x + nx * (overlap / 2.0)
					var new_h2y = h2y + ny * (overlap / 2.0)

					if typeof(h1) == TYPE_DICTIONARY:
						h1["x"] = new_h1x
						h1["y"] = new_h1y
					else:
						h1.x = new_h1x
						h1.y = new_h1y

					if typeof(h2) == TYPE_DICTIONARY:
						h2["x"] = new_h2x
						h2["y"] = new_h2y
					else:
						h2.x = new_h2x
						h2.y = new_h2y

					var p = 2.0 * (h1vx * nx + h1vy * ny - h2vx * nx - h2vy * ny) / 2.0
					var new_h1vx = h1vx - p * nx
					var new_h1vy = h1vy - p * ny
					var new_h2vx = h2vx + p * nx
					var new_h2vy = h2vy + p * ny

					if typeof(h1) == TYPE_DICTIONARY:
						h1["vx"] = new_h1vx
						h1["vy"] = new_h1vy
					else:
						if "vx" in h1: h1.vx = new_h1vx
						elif h1.has_method("set"): h1.set("vx", new_h1vx)
						if "vy" in h1: h1.vy = new_h1vy
						elif h1.has_method("set"): h1.set("vy", new_h1vy)

					if typeof(h2) == TYPE_DICTIONARY:
						h2["vx"] = new_h2vx
						h2["vy"] = new_h2vy
					else:
						if "vx" in h2: h2.vx = new_h2vx
						elif h2.has_method("set"): h2.set("vx", new_h2vx)
						if "vy" in h2: h2.vy = new_h2vy
						elif h2.has_method("set"): h2.set("vy", new_h2vy)

					var impact_speed = abs(p)
					if impact_speed > 100.0:
						for b in balls:
							var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
							if not alive: continue

							var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.x
							var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.y

							var bdx = bx - h1x
							var bdy = by - h1y
							var bdist = sqrt(bdx * bdx + bdy * bdy)

							if bdist < h1r + h2r + 100.0:
								if typeof(b) == TYPE_DICTIONARY:
									b["reflect_shield_active"] = false
								else:
									if b.has_method("set_meta"): b.set_meta("reflect_shield_active", false)
									if "reflect_shield_active" in b: b.reflect_shield_active = false

								var damage = (impact_speed / 100.0) * 20.0
								if typeof(b) == TYPE_DICTIONARY:
									if b.has("hp"): b["hp"] -= damage
								else:
									if b.has_method("take_damage"): b.take_damage(damage)
									elif "hp" in b: b.hp -= damage

								if typeof(b) == TYPE_DICTIONARY:
									b["reflect_shield_active"] = true
								else:
									if b.has_method("set_meta"): b.set_meta("reflect_shield_active", true)
									if "reflect_shield_active" in b: b.reflect_shield_active = true

								if world != null and world.has_method("add_event"):
									world.add_event("explosion", {"x": h1x, "y": h1y, "radius": h1r + h2r + 100.0, "damage": damage})

		for b in balls:
			var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
			if not alive: continue

			var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.x
			var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.y
			var br = b.get("radius", 10.0) if typeof(b) == TYPE_DICTIONARY else b.radius

			var base_speed = b.get("base_speed", 200.0) if typeof(b) == TYPE_DICTIONARY else (b.base_speed if "base_speed" in b else 200.0)

			for h in hazards:
				var hx = h.get("x", 0.0) if typeof(h) == TYPE_DICTIONARY else h.x
				var hy = h.get("y", 0.0) if typeof(h) == TYPE_DICTIONARY else h.y
				var hr = h.get("radius", 10.0) if typeof(h) == TYPE_DICTIONARY else h.radius

				var dx = hx - bx
				var dy = hy - by
				var dist = sqrt(dx * dx + dy * dy)

				if dist < br + hr and dist > 0.0001:
					var overlap = (br + hr) - dist
					var nx = dx / dist
					var ny = dy / dist

					var new_hx = hx + nx * overlap
					var new_hy = hy + ny * overlap

					if typeof(h) == TYPE_DICTIONARY:
						h["x"] = new_hx
						h["y"] = new_hy
					else:
						h.x = new_hx
						h.y = new_hy

					var push_speed = base_speed
					var h_vx = h.get("vx", 0.0) if typeof(h) == TYPE_DICTIONARY else (h.vx if "vx" in h else 0.0)
					var h_vy = h.get("vy", 0.0) if typeof(h) == TYPE_DICTIONARY else (h.vy if "vy" in h else 0.0)

					var new_vx = h_vx + nx * push_speed * delta * 5.0
					var new_vy = h_vy + ny * push_speed * delta * 5.0

					if typeof(h) == TYPE_DICTIONARY:
						h["vx"] = new_vx
						h["vy"] = new_vy
					else:
						if "vx" in h: h.vx = new_vx
						elif h.has_method("set"): h.set("vx", new_vx)
						if "vy" in h: h.vy = new_vy
						elif h.has_method("set"): h.set("vy", new_vy)

		for h in hazards:
			var hvx = h.get("vx", 0.0) if typeof(h) == TYPE_DICTIONARY else (h.vx if "vx" in h else 0.0)
			var hvy = h.get("vy", 0.0) if typeof(h) == TYPE_DICTIONARY else (h.vy if "vy" in h else 0.0)

			if abs(hvx) > 0.1 or abs(hvy) > 0.1:
				var hx = h.get("x", 0.0) if typeof(h) == TYPE_DICTIONARY else h.x
				var hy = h.get("y", 0.0) if typeof(h) == TYPE_DICTIONARY else h.y

				var new_hx = hx + hvx * delta
				var new_hy = hy + hvy * delta

				if typeof(h) == TYPE_DICTIONARY:
					h["x"] = new_hx
					h["y"] = new_hy
					h["vx"] = hvx * 0.95
					h["vy"] = hvy * 0.95
				else:
					h.x = new_hx
					h.y = new_hy
					if "vx" in h: h.vx = hvx * 0.95
					elif h.has_method("set"): h.set("vx", hvx * 0.95)
					if "vy" in h: h.vy = hvy * 0.95
					elif h.has_method("set"): h.set("vy", hvy * 0.95)

				var speed = sqrt(hvx * hvx + hvy * hvy)
				if speed > 50.0:
					for b in balls:
						var alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
						if not alive: continue

						var bx = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.x
						var by = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.y
						var br = b.get("radius", 10.0) if typeof(b) == TYPE_DICTIONARY else b.radius

						var hr = h.get("radius", 10.0) if typeof(h) == TYPE_DICTIONARY else h.radius

						var dx = bx - new_hx
						var dy = by - new_hy
						var dist = sqrt(dx * dx + dy * dy)

						if dist < br + hr and dist > 0.0001:
							var damage = (speed / 100.0) * 15.0

							if typeof(b) == TYPE_DICTIONARY:
								b["reflect_shield_active"] = false
							else:
								if b.has_method("set_meta"): b.set_meta("reflect_shield_active", false)
								if "reflect_shield_active" in b: b.reflect_shield_active = false

							if typeof(b) == TYPE_DICTIONARY:
								if b.has("hp"): b["hp"] -= damage
							else:
								if b.has_method("take_damage"): b.take_damage(damage)
								elif "hp" in b: b.hp -= damage

							if typeof(b) == TYPE_DICTIONARY:
								b["reflect_shield_active"] = true
							else:
								if b.has_method("set_meta"): b.set_meta("reflect_shield_active", true)
								if "reflect_shield_active" in b: b.reflect_shield_active = true

							var nx = dx / dist
							var ny = dy / dist
							var new_vx = hvx * -0.5
							var new_vy = hvy * -0.5

							if typeof(h) == TYPE_DICTIONARY:
								h["vx"] = new_vx
								h["vy"] = new_vy
							else:
								if "vx" in h: h.vx = new_vx
								elif h.has_method("set"): h.set("vx", new_vx)
								if "vy" in h: h.vy = new_vy
								elif h.has_method("set"): h.set("vy", new_vy)



class DynamicSafeZoneMode extends GameMode:
    var zone_x: float = 500.0
    var zone_y: float = 500.0
    var zone_radius: float = 500.0
    var min_zone_radius: float = 50.0
    var shrink_rate: float = 10.0
    var outside_damage_per_second: float = 10.0
    var zone_target_x: float = 500.0
    var zone_target_y: float = 500.0
    var collapse_triggered: bool = false
    var buff_zone_radius: float = 75.0
    var buff_type: String = "speed"
    var buff_timer: float = 0.0

    func _init() -> void:
        name = "Dynamic Safe Zone"
        description = "Dynamic safe zones that not only protect from environmental damage but also apply randomized buffs for a short duration, encouraging players to fight for the optimal spot inside the zone."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        collapse_triggered = false
        var arena_width = 1000.0
        var arena_height = 1000.0
        if "arena" in world and world.arena:
            if "width" in world.arena:
                arena_width = float(world.arena.width)
            if "height" in world.arena:
                arena_height = float(world.arena.height)

        zone_x = arena_width / 2.0
        zone_y = arena_height / 2.0
        zone_target_x = zone_x
        zone_target_y = zone_y
        zone_radius = min(arena_width, arena_height) / 2.0
        min_zone_radius = 50.0
        buff_timer = 0.0
        _pick_new_buff()

    func _pick_new_buff() -> void:
        var buffs = ["speed", "damage", "heal", "shield"]
        buff_type = buffs[randi() % buffs.size()]
        buff_timer = randf_range(5.0, 10.0)

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        super.tick(world, balls, delta)

        if world != null and world.has_method("has_meta") and not world.has_meta("dead_balls"):
            world.set_meta("dead_balls", [])

        if world != null and world.has_method("has_meta") and world.has_meta("dead_balls"):
            pass # Keep logic simple
        elif world != null and world.has_method("has_meta") and not world.has_meta("dead_balls"):
            world.set_meta("dead_balls", []) if world.has_method("set_meta") else null

        for b in balls:
            if not b.alive:
                if world != null and world.has_method("has_meta") and world.has_meta("dead_balls"):
                    if not world.get_meta("dead_balls").has(b):
                        if b.has_method("set_meta"):
                            b.set_meta("time_since_death", 0.0)
                        world.get_meta("dead_balls").append(b)
                    else:
                        if b.has_method("get_meta") and b.has_meta("time_since_death"):
                            b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        buff_timer -= delta
        if buff_timer <= 0:
            _pick_new_buff()

        var dx = zone_target_x - zone_x
        var dy = zone_target_y - zone_y
        var dist_zone = sqrt(dx*dx + dy*dy)
        if dist_zone > 5.0:
            var move_speed = 15.0
            zone_x += (dx / dist_zone) * move_speed * delta
            zone_y += (dy / dist_zone) * move_speed * delta
        else:
            var arena_width = 1000.0
            var arena_height = 1000.0
            if world != null and "arena" in world and world.arena:
                if "width" in world.arena:
                    arena_width = float(world.arena.width)
                if "height" in world.arena:
                    arena_height = float(world.arena.height)
            var buffer = max(100.0, zone_radius * 0.5)
            zone_target_x = randf_range(buffer, arena_width - buffer)
            zone_target_y = randf_range(buffer, arena_height - buffer)

        if zone_radius > min_zone_radius:
            zone_radius -= shrink_rate * delta
            if zone_radius <= min_zone_radius:
                zone_radius = min_zone_radius
                if not collapse_triggered:
                    collapse_triggered = true
                    if world.has_method("add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif collapse_triggered:
            if zone_radius > 0:
                zone_radius -= shrink_rate * delta
                if zone_radius < 0:
                    zone_radius = 0.0

            for b in balls:
                if b.alive and b.ball_type != "spectator":
                    var b_x = b.get("position").x if b.get("position") != null else b.get("x")
                    var b_y = b.get("position").y if b.get("position") != null else b.get("y")
                    var dx_pull = zone_x - b_x
                    var dy_pull = zone_y - b_y
                    var dist_pull = sqrt(dx_pull*dx_pull + dy_pull*dy_pull)
                    if dist_pull > 0:
                        var pull_strength = 2000.0
                        if not "vx" in b: b.vx = 0.0
                        if not "vy" in b: b.vy = 0.0
                        b.vx += (dx_pull / dist_pull) * pull_strength * delta
                        b.vy += (dy_pull / dist_pull) * pull_strength * delta

        var damage_this_tick = outside_damage_per_second * (10.0 if collapse_triggered else 1.0) * delta

        for b in balls:
            if not b.alive or b.ball_type == "spectator":
                continue

            if not b.has_meta("base_speed"):
                b.set_meta("base_speed", b.get("speed") if b.get("speed") != null else 100.0)
            if not b.has_meta("base_damage"):
                b.set_meta("base_damage", b.get("damage") if b.get("damage") != null else 10.0)

            var b_x = b.get("position").x if b.get("position") != null else b.get("x")
            var b_y = b.get("position").y if b.get("position") != null else b.get("y")

            var dx_ball = b_x - zone_x
            var dy_ball = b_y - zone_y
            var dist_ball = sqrt(dx_ball*dx_ball + dy_ball*dy_ball)

            var in_buff_zone = dist_ball <= buff_zone_radius

            if in_buff_zone:
                if buff_type == "speed":
                    b.set("speed", b.get_meta("base_speed") * 1.5)
                    b.set_meta("zone_modifier_speed", true)
                elif buff_type == "damage":
                    b.set("damage", b.get_meta("base_damage") * 1.5)
                    b.set_meta("zone_modifier_damage", true)
                elif buff_type == "heal":
                    if "hp" in b and "max_hp" in b:
                        b.hp = min(b.get("max_hp") if b.get("max_hp") != null else 100.0, b.hp + 30.0 * delta)
                elif buff_type == "shield":
                    b.set("shield", b.get("shield") if b.get("shield") != null else 0.0 + 10.0 * delta)
                    if b.get("shield") > 50.0:
                        b.set("shield", 50.0)

            if not in_buff_zone or buff_type != "speed":
                if b.has_meta("zone_modifier_speed") and b.get_meta("zone_modifier_speed"):
                    b.set("speed", b.get_meta("base_speed"))
                    b.remove_meta("zone_modifier_speed")

            if not in_buff_zone or buff_type != "damage":
                if b.has_meta("zone_modifier_damage") and b.get_meta("zone_modifier_damage"):
                    b.set("damage", b.get_meta("base_damage"))
                    b.remove_meta("zone_modifier_damage")

            if dist_ball > zone_radius:
                if "hp" in b:
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = false
                        b.hp = 0


class DailyMutatorMode extends GameMode:
	var mutators: Array = []
	var _rewards_given: bool = false

	func _init():
		name = "Daily Mutator"
		description = "Randomly applies extreme global mutators daily. Surviving grants exclusive rewards."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not world.has("dead_balls"):
			world.dead_balls = []

		var current_day = int(Time.get_unix_time_from_system() / (24.0 * 3600.0))
		var mutator_combinations = [
			["low_gravity", "double_damage"],
			["invisible_hazards"],
			["high_speed", "vampirism"],
			["global_hp", "global_cooldown"]
		]

		mutators = mutator_combinations[current_day % mutator_combinations.size()]

		for b in balls:
			var is_dict = typeof(b) == TYPE_DICTIONARY
			var b_type = b.get("ball_type", "") if is_dict else b.ball_type
			if b_type != "spectator":
				if "low_gravity" in mutators:
					if is_dict:
						b["mass"] = b.get("mass", 1.0) * 0.5
					else:
						b.mass = b.get("mass", 1.0) * 0.5
				if "double_damage" in mutators:
					if is_dict:
						b["base_damage"] = b.get("base_damage", b.get("damage", 10.0)) * 2.0
						b["damage"] = b.get("damage", 10.0) * 2.0
					else:
						b.base_damage = b.get("base_damage", b.get("damage", 10.0)) * 2.0
						b.damage = b.get("damage", 10.0) * 2.0
				if "high_speed" in mutators:
					if is_dict:
						b["base_speed"] = b.get("base_speed", b.get("speed", 100.0)) * 1.5
						b["speed"] = b.get("speed", 100.0) * 1.5
					else:
						b.base_speed = b.get("base_speed", b.get("speed", 100.0)) * 1.5
						b.speed = b.get("speed", 100.0) * 1.5
				if "vampirism" in mutators:
					if is_dict:
						b["lifesteal"] = b.get("lifesteal", 0.0) + 0.5
					else:
						b.lifesteal = b.get("lifesteal", 0.0) + 0.5
				if "global_hp" in mutators:
					if is_dict:
						b["max_hp"] = b.get("max_hp", 100.0) * 0.5
						b["hp"] = b.get("hp", 100.0) * 0.5
					else:
						b.max_hp = b.get("max_hp", 100.0) * 0.5
						b.hp = b.get("hp", 100.0) * 0.5
				if "global_cooldown" in mutators:
					if is_dict:
						b["skill_cooldown"] = b.get("skill_cooldown", 5.0) * 0.5
					else:
						b.skill_cooldown = b.get("skill_cooldown", 5.0) * 0.5

		if "invisible_hazards" in mutators and world.has("arena") and world.arena != null:
			if typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("hazards"):
				for h in world.arena.hazards:
					h["invisible"] = true
			elif typeof(world.arena) == TYPE_OBJECT and world.arena.get("hazards") != null:
				for h in world.arena.hazards:
					if typeof(h) == TYPE_DICTIONARY:
						h["invisible"] = true
					else:
						h.invisible = true

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		var teams_alive = {}
		var balls_alive = []
		for b in balls:
			var is_dict = typeof(b) == TYPE_DICTIONARY
			var b_alive = b.get("alive", true) if is_dict else b.alive
			var b_type = b.get("ball_type", "") if is_dict else b.ball_type
			var b_team = b.get("team", b_type) if is_dict else b.get("team", b_type)

			if b_alive and b_type != "spectator":
				teams_alive[b_team] = true
				balls_alive.append(b)

		if teams_alive.size() <= 1 and balls_alive.size() > 0 and teams_alive.size() > 0 and not _rewards_given:
			_rewards_given = true
			var pm = world.get("profile_manager") if typeof(world) == TYPE_DICTIONARY else world.get("profile_manager")
			if pm != null:
				if pm.has_method("add_cosmetic"):
					pm.call("add_cosmetic", "Daily Survivor Crown")
				for b in balls_alive:
					var is_dict = typeof(b) == TYPE_DICTIONARY
					if is_dict:
						b["skill_points"] = b.get("skill_points", 0) + 10
					else:
						b.skill_points = b.get("skill_points", 0) + 10


class BlackMarketMode extends GameMode:
    var currency_spawn_timer = 0.0

    func _init():
        super._init()
        self.name = "Black Market"
        self.description = "Collect currency to buy upgrades from wandering Black Markets."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "currency_pickups" in world:
            world.currency_pickups = []
        if not "black_markets" in world:
            world.black_markets = []

        var arena_width = 1000.0
        var arena_height = 1000.0
        if world != null and "arena" in world and world.arena != null:
            if "width" in world.arena: arena_width = float(world.arena.width)
            if "height" in world.arena: arena_height = float(world.arena.height)

        for i in range(15):
            world.currency_pickups.append({
                "x": randf_range(50.0, arena_width - 50.0),
                "y": randf_range(50.0, arena_height - 50.0),
                "type": "currency"
            })

        for i in range(2):
            world.black_markets.append({
                "x": randf_range(100.0, arena_width - 100.0),
                "y": randf_range(100.0, arena_height - 100.0),
                "vx": randf_range(-20.0, 20.0),
                "vy": randf_range(-20.0, 20.0),
                "radius": 40.0
            })

        for b in balls:
            if typeof(b) == TYPE_DICTIONARY:
                if b.get("ball_type", "") != "spectator":
                    if not b.has("currency"): b["currency"] = 0
                    if not b.has("team"): b["team"] = b.get("ball_type", "")
                    b["purchase_cooldown"] = 0.0
            else:
                if b.get("ball_type") != "spectator":
                    if not b.has_meta("currency"): b.set_meta("currency", 0)
                    if not b.get("team"): b.set("team", b.get("ball_type"))
                    if not b.has_meta("purchase_cooldown"): b.set_meta("purchase_cooldown", 0.0)

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        super.tick(world, balls, delta)
        var arena_width = 1000.0
        var arena_height = 1000.0
        if world != null and "arena" in world and world.arena != null:
            if "width" in world.arena: arena_width = float(world.arena.width)
            if "height" in world.arena: arena_height = float(world.arena.height)

        currency_spawn_timer += delta
        if currency_spawn_timer >= 2.0:
            currency_spawn_timer = 0.0
            if "currency_pickups" in world and world.currency_pickups.size() < 30:
                world.currency_pickups.append({
                    "x": randf_range(50.0, arena_width - 50.0),
                    "y": randf_range(50.0, arena_height - 50.0),
                    "type": "currency"
                })

        if "black_markets" in world:
            for bm in world.black_markets:
                bm["x"] += bm["vx"] * delta
                bm["y"] += bm["vy"] * delta

                if bm["x"] < bm["radius"] or bm["x"] > arena_width - bm["radius"]:
                    bm["vx"] *= -1
                    bm["x"] = clamp(bm["x"], bm["radius"], arena_width - bm["radius"])
                if bm["y"] < bm["radius"] or bm["y"] > arena_height - bm["radius"]:
                    bm["vy"] *= -1
                    bm["y"] = clamp(bm["y"], bm["radius"], arena_height - bm["radius"])

        for b in balls:
            var alive = false
            var is_spec = false
            var bx = 0.0
            var by = 0.0
            var bradius = 10.0
            var bcurrency = 0
            var bpcooldown = 0.0

            if typeof(b) == TYPE_DICTIONARY:
                alive = b.get("alive", false)
                is_spec = (b.get("ball_type", "") == "spectator")
                bx = float(b.get("x", 0.0))
                by = float(b.get("y", 0.0))
                bradius = float(b.get("radius", 10.0))
                bcurrency = int(b.get("currency", 0))
                bpcooldown = float(b.get("purchase_cooldown", 0.0))
            else:
                alive = b.get("alive")
                is_spec = (b.get("ball_type") == "spectator")
                bx = float(b.get("x"))
                by = float(b.get("y"))
                bradius = float(b.get("radius"))
                bcurrency = int(b.get_meta("currency")) if b.has_meta("currency") else 0
                bpcooldown = float(b.get_meta("purchase_cooldown")) if b.has_meta("purchase_cooldown") else 0.0

            if not alive or is_spec:
                continue

            bpcooldown = max(0.0, bpcooldown - delta)

            if "currency_pickups" in world:
                var pickups_to_remove = []
                for i in range(world.currency_pickups.size()):
                    var c = world.currency_pickups[i]
                    var dx = bx - float(c["x"])
                    var dy = by - float(c["y"])
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist <= bradius + 15.0:
                        bcurrency += 1
                        pickups_to_remove.append(i)

                pickups_to_remove.sort_custom(func(a, b): return a > b)
                for idx in pickups_to_remove:
                    if idx < world.currency_pickups.size():
                        world.currency_pickups.remove_at(idx)

            if bpcooldown <= 0.0 and bcurrency >= 5 and "black_markets" in world:
                for bm in world.black_markets:
                    var dx = bx - float(bm["x"])
                    var dy = by - float(bm["y"])
                    var dist = sqrt(dx*dx + dy*dy)
                    if dist <= bradius + float(bm["radius"]):
                        bcurrency -= 5
                        bpcooldown = 5.0

                        var upgrades = ["max_hp", "speed", "damage"]
                        var upgrade_type = upgrades[randi() % upgrades.size()]

                        if typeof(b) == TYPE_DICTIONARY:
                            if upgrade_type == "max_hp":
                                if not b.has("base_max_hp"): b["base_max_hp"] = float(b.get("max_hp", 100.0))
                                b["base_max_hp"] += 20.0
                                b["max_hp"] = b["base_max_hp"]
                                b["hp"] = min(float(b.get("hp", 100.0)) + 20.0, float(b["max_hp"]))
                            elif upgrade_type == "speed":
                                if not b.has("base_speed"): b["base_speed"] = float(b.get("speed", 100.0))
                                b["base_speed"] += 15.0
                                b["speed"] = b["base_speed"]
                            elif upgrade_type == "damage":
                                if not b.has("base_damage"): b["base_damage"] = float(b.get("damage", 10.0))
                                b["base_damage"] += 5.0
                                b["damage"] = b["base_damage"]
                        else:
                            if upgrade_type == "max_hp":
                                var cur_base_mhp = b.get_meta("base_max_hp") if b.has_meta("base_max_hp") else float(b.get("max_hp"))
                                b.set_meta("base_max_hp", cur_base_mhp + 20.0)
                                b.set("max_hp", cur_base_mhp + 20.0)
                                b.set("hp", min(float(b.get("hp")) + 20.0, float(b.get("max_hp"))))
                            elif upgrade_type == "speed":
                                var cur_base_spd = b.get_meta("base_speed") if b.has_meta("base_speed") else float(b.get("speed"))
                                b.set_meta("base_speed", cur_base_spd + 15.0)
                                b.set("speed", cur_base_spd + 15.0)
                            elif upgrade_type == "damage":
                                var cur_base_dmg = b.get_meta("base_damage") if b.has_meta("base_damage") else float(b.get("damage"))
                                b.set_meta("base_damage", cur_base_dmg + 5.0)
                                b.set("damage", cur_base_dmg + 5.0)

                        if world.has_method("add_event"):
                            world.add_event("upgrade_purchased", {"ball": b, "upgrade": upgrade_type})
                        break

            if typeof(b) == TYPE_DICTIONARY:
                b["currency"] = bcurrency
                b["purchase_cooldown"] = bpcooldown
            else:
                b.set_meta("currency", bcurrency)
                b.set_meta("purchase_cooldown", bpcooldown)

class FloorIsLavaMode extends GameMode:
	var lava_radius: float = 2000.0
	var min_lava_radius: float = 0.0
	var shrink_rate: float = 15.0
	var platforms: Array = []
	var platform_timer: float = 0.0
	var bounce_pads: Array = []

	func _init():
		super._init()
		name = "Floor Is Lava"
		description = "The entire arena floor slowly turns into lava starting from the edges. Safe zones are randomly generated platforms that appear for a limited time before submerging. Players must navigate between platforms using bounce pads and careful movement."

	func setup(world, balls):
		super.setup(world, balls)
		var arena_width = 1000.0
		var arena_height = 1000.0
		if typeof(world) == TYPE_DICTIONARY:
			if world.has("arena") and world.arena != null:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
		else:
			if world.get("arena"):
				arena_width = world.arena.width
				arena_height = world.arena.height

		lava_radius = max(arena_width, arena_height)
		platforms.clear()
		bounce_pads.clear()
		platform_timer = 0.0
		_spawn_platform(world, arena_width/2.0, arena_height/2.0)

	func _spawn_platform(world, p_x = null, p_y = null):
		var arena_width = 1000.0
		var arena_height = 1000.0
		if typeof(world) == TYPE_DICTIONARY:
			if world.has("arena") and world.arena != null:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
		else:
			if world.get("arena"):
				arena_width = world.arena.width
				arena_height = world.arena.height

		var x = p_x if p_x != null else randf_range(200.0, arena_width - 200.0)
		var y = p_y if p_y != null else randf_range(200.0, arena_height - 200.0)

		var radius = randf_range(100.0, 200.0)
		var lifetime = randf_range(10.0, 20.0)

		platforms.append({
			"x": x,
			"y": y,
			"radius": radius,
			"timer": lifetime
		})

		var angle = randf_range(0, 2 * PI)
		var pad_x = x + (radius * 0.7) * cos(angle)
		var pad_y = y + (radius * 0.7) * sin(angle)

		bounce_pads.append({
			"x": pad_x,
			"y": pad_y,
			"radius": 40.0,
			"timer": lifetime
		})

	func tick(world, balls, delta = 0.016):
		var arena_width = 1000.0
		var arena_height = 1000.0
		if typeof(world) == TYPE_DICTIONARY:
			if world.has("arena") and world.arena != null:
				arena_width = world.arena.get("width", 1000.0)
				arena_height = world.arena.get("height", 1000.0)
		else:
			if world.get("arena") != null:
				arena_width = world.arena.width
				arena_height = world.arena.height

		var center_x = arena_width / 2.0
		var center_y = arena_height / 2.0

		lava_radius = max(min_lava_radius, lava_radius - shrink_rate * delta)

		platform_timer -= delta
		if platform_timer <= 0:
			_spawn_platform(world)
			platform_timer = randf_range(5.0, 10.0)

		var i = platforms.size() - 1
		while i >= 0:
			var p = platforms[i]
			p["timer"] -= delta
			if p["timer"] <= 0:
				platforms.remove_at(i)
			i -= 1

		i = bounce_pads.size() - 1
		while i >= 0:
			var bp = bounce_pads[i]
			bp["timer"] -= delta
			if bp["timer"] <= 0:
				bounce_pads.remove_at(i)
			i -= 1

		var hazards_array = null
		if typeof(world) == TYPE_DICTIONARY:
			if world.has("arena") and world.arena != null and typeof(world.arena) == TYPE_DICTIONARY:
				if world.arena.has("hazards"):
					hazards_array = world.arena.hazards
		else:
			if world.get("arena") != null:
				hazards_array = world.arena.hazards

		if hazards_array != null:
			var j = hazards_array.size() - 1
			while j >= 0:
				var h = hazards_array[j]
				var h_kind = ""
				if typeof(h) == TYPE_DICTIONARY:
					h_kind = h.get("kind", "")
				else:
					h_kind = h.get("kind")

				if h_kind == "bounce_pad":
					hazards_array.remove_at(j)
				j -= 1

			for idx in range(bounce_pads.size()):
				var bp = bounce_pads[idx]
				var arena_class = null
				if ResourceLoader.exists("res://src/arena/procedural_arena.gd"):
					arena_class = load("res://src/arena/procedural_arena.gd")
				if arena_class != null and arena_class.const_defined("Hazard"):
					var h = arena_class.Hazard.new(99000 + idx, bp["x"], bp["y"], bp["radius"], "bounce_pad", 0.0)
					hazards_array.append(h)
				else:
					var h = {
						"id": 99000 + idx,
						"x": bp["x"],
						"y": bp["y"],
						"radius": bp["radius"],
						"kind": "bounce_pad",
						"damage": 0.0,
						"active": true
					}
					hazards_array.append(h)

		for b in balls:
			var is_alive = b.get("alive", false) if typeof(b) == TYPE_DICTIONARY else b.alive
			var b_type = b.get("ball_type", "") if typeof(b) == TYPE_DICTIONARY else b.ball_type

			if not is_alive or b_type == "spectator":
				continue

			var b_x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.x
			var b_y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.y

			var dist_to_center = sqrt((b_x - center_x) * (b_x - center_x) + (b_y - center_y) * (b_y - center_y))
			var in_lava = dist_to_center > lava_radius

			var on_platform = false
			for p in platforms:
				var pd = sqrt((b_x - p["x"]) * (b_x - p["x"]) + (b_y - p["y"]) * (b_y - p["y"]))
				if pd <= p["radius"]:
					on_platform = true
					break

			if in_lava and not on_platform:
				var hp = b.get("hp", 0.0) if typeof(b) == TYPE_DICTIONARY else b.hp
				hp -= 20.0 * delta
				hp = max(0, hp)

				if typeof(b) == TYPE_DICTIONARY:
					b["hp"] = hp
					if hp <= 0:
						b["alive"] = false
				else:
					b.hp = hp
					if hp <= 0:
						b.alive = false

class MeteorShowerMode extends GameMode:
	var spawn_timer = 0.0
	var rng = RandomNumberGenerator.new()

	func _init():
		super()
		name = "Meteor Shower"
		description = "High damage hazards fall from the sky."

	func setup(world, balls):
		super.setup(world, balls)
		if not "hazards" in world.arena:
			world.arena.hazards = []

	func tick(world, balls, delta = 0.016):
		super.tick(world, balls, delta)

		spawn_timer += delta

		if spawn_timer >= 1.0:
			spawn_timer = 0.0
			var arena_width = world.arena.width if "width" in world.arena else 1000.0
			var arena_height = world.arena.height if "height" in world.arena else 1000.0

			var x = rng.randf_range(50.0, arena_width - 50.0)
			var y = rng.randf_range(50.0, arena_height - 50.0)

			var ProceduralArena = load("res://src/arena/procedural_arena.gd")
			var h_id = 15000 + world.arena.hazards.size() + rng.randi_range(0, 10000)
			var meteor = ProceduralArena.Hazard.new(h_id, x, y, 30.0, "meteor", 200.0)
			meteor.target_radius = 30.0
			meteor.set_meta("duration", 5.0)

			world.arena.hazards.append(meteor)

var GAME_MODES = {
	"meteor_shower": MeteorShowerMode.new(),

	"black_market": BlackMarketMode.new(),
	"floor_is_lava": FloorIsLavaMode.new(),


	"geometric_zone": GeometricZoneMode.new(),
	"daily_mutator": DailyMutatorMode.new(),
	"factory": FactoryMode.new(),
    "mirror_walls": MirrorWallsMode.new(),
    "stamina_regen": StaminaRegenMode.new(),
    "zero_gravity": ZeroGravityMode.new(),
    "magnetic_collisions": MagneticCollisionsMode.new(),
	"day_night_mode": DayNightMode.new(),
	"shifting_maze": ShiftingMazeMode.new(),
	"stamina_speed": StaminaSpeedMode.new(),

	"blackout": BlackoutMode.new(),
	"dual_payload": DualPayloadMode.new(),
	"tug_of_war": TugOfWarMode.new(),
	"escort": EscortMode.new(),
	"windstorm": WindstormMode.new(),
	"modifier_zones": ModifierZonesMode.new(),
	"modifier_zones_safe_zone": ModifierZonesSafeZoneMode.new(),
    "draft_royale": DraftRoyaleMode.new(),
    "tournament": TournamentMode.new(),
    "bumper_balls": BumperBallsMode.new(),
	"pinball": PinballMode.new(),
    "portal_node": PortalNodeMode.new(),
	"memory_traps": MemoryTrapsMode.new(),
	"pitch_black": PitchBlackMode.new(),
	"vision_reduced": VisionReducedMode.new(),
	"emp_burst": EMPBurstMode.new(),
	"dynamic_hazards": DynamicHazardsMode.new(),
	"custom_match": CustomMatchMode.new(),
	"reverse_event": ReverseEventMode.new(),
	"unstable_portals_event": UnstablePortalsEventMode.new(),
	"minefield_event": MinefieldEventMode.new(),
    "weather_chaos": WeatherChaosMode.new(),
    "domination": DominationMode.new(),
    "black_hole": BlackHoleMode.new(),
    "gravity_well": GravityWellMode.new(),
    "king_of_the_hill": KingOfTheHillMode.new(),
    "moving_zone": MovingZoneMode.new(),
    "vampire_royale": VampireRoyaleMode.new(),
    "battle_royale": BattleRoyaleMode.new(),
    "team_deathmatch": TeamDeathmatchMode.new(),
    "zombie_infection": ZombieInfectionMode.new(),
    "boss_fight": BossFightMode.new(),
    "vip_defense": VIPDefenseMode.new(),
    "survival": SurvivalMode.new(),
    "toxic_environment": ToxicEnvironmentMode.new(),
    "capture_the_flag": CaptureTheFlagMode.new(),
    "evolutionary_simulation": EvolutionarySimulationMode.new(),
    "interactive_training": load("res://src/ai/interactive_training.gd").new(),
    "shrinking_danger_zone": ShrinkingDangerZoneMode.new(),
    "safe_zone": SafeZoneMode.new(),
    "dynamic_safe_zone": DynamicSafeZoneMode.new(),
    "moving_safe_zone": MovingSafeZoneMode.new(),
    "bounty_hunt": BountyHuntMode.new(),
    "earthquake": EarthquakeMode.new(),
    "mirror_match": MirrorMatchMode.new(),
	"clone_chaos": CloneChaosMode.new(),
	"volatile_clones": VolatileClonesMode.new(),
    "supernova": SupernovaMode.new(),
	"echolocation": EcholocationMode.new(),
	"body_swap": BodySwapMode.new(),
	"hazard_billiards": HazardBilliardsMode.new()
}
