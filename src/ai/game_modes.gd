class_name GameModes

class GameMode:
    var name: String = "Unknown"
    var description: String = "Base game mode"

    func _init() -> void:
        pass

    func setup(world, balls: Array) -> void:
        if not "dead_balls" in world:
            world.dead_balls = []

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

        for b in balls:
            if b.ball_type != "spectator":
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

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)
        pass


    func check_winner(world, balls: Array):
        return null

class BattleRoyaleMode extends GameMode:
    var dark_phase_timer: float = 0.0
    var is_dark_phase: bool = false
    var weather_timer: float = 0.0
    var weather: String = "clear"

    func _init() -> void:
        name = "Battle Royale"
        description = "Last man standing. Everyone for themselves. Includes periodic dark phases."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.dead_balls = []
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
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        dark_phase_timer += delta

        # Weather logic
        if not "weather_timer" in self:
            self.weather_timer = 0.0
            self.weather = "clear"

        self.weather_timer += delta
        if self.weather_timer > 15.0:
            self.weather_timer = 0.0
            var weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm"]
            self.weather = weathers[randi() % weathers.size()]
            if self.weather == "wind":
                if has_method("set_meta"):
                    set_meta("wind_dx", (randf() * 100.0) - 50.0)
                    set_meta("wind_dy", (randf() * 100.0) - 50.0)

        if world != null and "arena" in world and world.arena != null:
            if self.weather == "fog" or self.weather == "snow":
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
            if self.weather == "snow":
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
            elif self.weather == "rain" or self.weather == "thunderstorm":
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
                    if "speed" in b: b.speed = base_spd * 0.8
                    if "damage" in b: b.damage = base_dmg
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
                elif self.weather == "snow":
                    if "speed" in b: b.speed = base_spd * 0.5
                    if "damage" in b: b.damage = base_dmg * 1.2
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
            world.dead_balls = []
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
            world.dead_balls = []
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
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
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
        description = "Multiple players fight one giant boss."
    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.dead_balls = []
        var valid_balls = []
        for b in balls:
            if b.ball_type != "spectator":
                valid_balls.append(b)

        if valid_balls.size() > 0:
            var boss = valid_balls[0]
            boss.team = "Boss"
            if "max_hp" in boss:
                boss.max_hp *= 10
                boss.hp = boss.max_hp
            if "damage" in boss:
                boss.damage *= 2

            # Position the boss in the center of the arena
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
                boss.base_speed *= 0.8
            elif boss.has_meta("base_speed"):
                boss.set_meta("base_speed", boss.get_meta("base_speed") * 0.8)

            for i in range(1, valid_balls.size()):
                valid_balls[i].team = "Hunters"

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
            world.dead_balls = []
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
            world.dead_balls = []
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


class CaptureTheFlagMode extends GameMode:
    func _init() -> void:
        name = "Capture The Flag"
        description = "Teams try to steal the enemy's flag and return it to their base."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
        if not "dead_balls" in world:
            world.dead_balls = []
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
            world.dead_balls = []
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
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
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
            world.dead_balls = []
        game_time = 0.0
        for b in balls:
            if b.ball_type != "spectator":
                b.set_meta("score", 0)

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
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
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
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
		name = "Weather Chaos"
		description = "Weather conditions change throughout the match, affecting stats."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		for b in balls:
			if b.ball_type != "spectator":
				b.team = b.ball_type
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
		weather_timer += delta
		if weather_timer > 10.0:
			weather_timer = 0.0
			var weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm"]
			weather = weathers[randi() % weathers.size()]
			if weather == "wind":
				if has_method("set_meta"):
					set_meta("wind_dx", (randf() * 100.0) - 50.0)
					set_meta("wind_dy", (randf() * 100.0) - 50.0)

		if world != null and "arena" in world:
			if weather == "fog" or weather == "snow":
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
			if weather == "snow":
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
			elif weather == "rain" or weather == "thunderstorm":
				var chance = 0.05
				if weather == "thunderstorm":
					chance = 0.2
				if randf() < chance * delta:
					var Hazard = load("res://src/arena/procedural_arena.gd").Hazard
					var x = randf_range(100.0, world.arena.width - 100.0)
					var y = randf_range(100.0, world.arena.height - 100.0)
					var lightning = Hazard.new(world.arena.hazards.size() + (randi() % 9000 + 1000), x, y, 30.0, "lightning_strike", 50.0)
					lightning.set_meta("duration", 1.0)
					world.arena.hazards.append(lightning)

		for b in balls:
			if b.alive and b.ball_type != "spectator":
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

				var base_spd = b.get_meta("base_speed")
				var base_dmg = b.get_meta("base_damage")
				var t = ""
				if "ball_type" in b: t = b.ball_type
				var is_fire = t in ["mage", "bomber", "chaos"]
				var is_water = t in ["elementalist", "healer", "trickster"]
				var is_air = t in ["ninja", "scout", "phantom"]
				var is_earth = t in ["tank", "druid", "juggernaut"]

				if weather == "clear":
					if "speed" in b: b.speed = base_spd
					if "damage" in b:
						if is_fire: b.damage = base_dmg * 1.5
						else: b.damage = base_dmg
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
						b.set_meta("attack_accuracy", 1.0)
				elif weather == "rain":
					if "speed" in b: b.speed = base_spd * 0.8
					if "damage" in b: b.damage = base_dmg
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.5)
						b.set_meta("steering_mult", 0.5)
					if "vx" in b and "vy" in b:
						b.x += b.vx * delta * 0.5
						b.y += b.vy * delta * 0.5
					if b.has_method("set_meta"):
						b.set_meta("attack_accuracy", 0.8)
					if is_water and "hp" in b:
						var m = 100.0
						if "max_hp" in b: m = b.max_hp
						elif b.has_method("has_meta") and b.has_meta("max_hp"): m = b.get_meta("max_hp")
						b.hp = min(m, b.hp + 5.0 * delta)
				elif weather == "fog":
					if "speed" in b: b.speed = base_spd * 0.8
					if "damage" in b: b.damage = base_dmg * 0.9
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
				elif weather == "snow":
					if "speed" in b: b.speed = base_spd * 0.5
					if "damage" in b: b.damage = base_dmg * 1.2
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
				elif weather == "wind":
					if "speed" in b:
						if is_air: b.speed = base_spd * 1.5
						else: b.speed = base_spd
					if "damage" in b: b.damage = base_dmg
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
				elif weather == "thunderstorm":
					if "speed" in b: b.speed = base_spd * 1.1
					if "damage" in b: b.damage = base_dmg * 1.5
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 1.0)
						b.set_meta("steering_mult", 1.0)
				elif weather == "sandstorm":
					if "speed" in b: b.speed = base_spd * 0.7
					if "damage" in b: b.damage = base_dmg
					if b.has_method("set_meta"):
						b.set_meta("dash_range_mult", 0.5)
						b.set_meta("steering_mult", 0.5)
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
						if "hp" in b: b.hp -= 20
					if b.has_method("set_meta"):
						b.set_meta("attack_accuracy", 0.5)

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
            world.dead_balls = []
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
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
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
            elif blue_count > red_count:
                pt.capture_progress -= 10.0 * delta

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
            world.dead_balls = []
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
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
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
			world.dead_balls = []

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
			world.dead_balls = []
		for b in balls:
			if not b.alive:
				if not world.dead_balls.has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.dead_balls.append(b)
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
			world.dead_balls = []

		var pm = null
		if world != null and "profile_manager" in world:
			pm = world.profile_manager

		var mutators_unlocked = false
		if pm != null and pm.has_method("are_mutators_unlocked"):
			mutators_unlocked = pm.are_mutators_unlocked()
		elif pm != null and "data" in pm:
			if pm.data.get("prestige_level", 0) >= 5:
				mutators_unlocked = true

		mutators_active = mutators_unlocked and mutators.size() > 0

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		if not "dead_balls" in world:
			world.dead_balls = []
		for b in balls:
			if not b.alive:
				if not world.dead_balls.has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.dead_balls.append(b)
				else:
					if b.has_method("get_meta") and b.has_meta("time_since_death"):
						b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

		if mutators_active:
			var trigger_reroll = false
			var types = ['paladin', 'assassin', 'ninja', 'warrior', 'guardian', 'chaos', 'bomber', 'templar', 'necromancer', 'vampire', 'sniper', 'king', 'easy', 'phantom', 'warlock', 'mimic', 'juggernaut', 'tank', 'berserker', 'druid', 'hard', 'scout', 'brawler', 'medium', 'neural', 'ranger', 'healer', 'rogue', 'swarm', 'conjurer', 'monk', 'mage', 'elementalist', 'trickster']
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




class VisionReducedMode extends GameMode:
	var pulse_timer: float = 0.0

	func _init() -> void:
		name = "Vision Reduced"
		description = "Visibility is severely reduced. AI relies on narrow cones of light or sonar-like pulses."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if not "dead_balls" in world:
			world.dead_balls = []
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
			world.dead_balls = []
		for b in balls:
			if not b.alive:
				if not world.dead_balls.has(b):
					if b.has_method("set_meta"):
						b.set_meta("time_since_death", 0.0)
					world.dead_balls.append(b)
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

class DynamicHazardsMode extends GameMode:
	var spawn_timer = 0.0
	var rng = RandomNumberGenerator.new()

	func _init():
		super()
		name = "Dynamic Hazards"
		description = "Watch out for moving hazards that traverse the arena!"

	func setup(world, balls):
		super.setup(world, balls)
		if not "hazards" in world.arena:
			world.arena.hazards = []

	func tick(world, balls, delta = 0.016):
		super.tick(world, balls, delta)

		spawn_timer += delta
		if spawn_timer >= 5.0:
			spawn_timer = 0.0

			var x = 0.0 if rng.randf() < 0.5 else world.arena.width
			var y = rng.randf_range(0.0, world.arena.height)
			var vx = rng.randf_range(50.0, 150.0) if x == 0.0 else rng.randf_range(-150.0, -50.0)
			var vy = rng.randf_range(-50.0, 50.0)

			var ProceduralArena = load("res://src/arena/procedural_arena.gd")
			var new_hazard = ProceduralArena.Hazard.new(world.arena.hazards.size() + rng.randi_range(1000, 9999), x, y, 40.0, "lava", 25.0)

			if new_hazard.has_method("set_meta"):
				new_hazard.set_meta("vx", vx)
				new_hazard.set_meta("vy", vy)

			world.arena.hazards.append(new_hazard)

		var hazards_to_keep = []
		for hazard in world.arena.hazards:
			if hazard.has_method("has_meta") and hazard.has_meta("vx") and hazard.has_meta("vy"):
				hazard.x += hazard.get_meta("vx") * delta
				hazard.y += hazard.get_meta("vy") * delta

				if not (hazard.x < -100 or hazard.x > world.arena.width + 100 or hazard.y < -100 or hazard.y > world.arena.height + 100):
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



class SafeZoneMode extends GameMode:
    var zone_x: float = 500.0
    var zone_y: float = 500.0
    var zone_radius: float = 500.0
    var min_zone_radius: float = 50.0
    var shrink_rate: float = 10.0
    var outside_damage_per_second: float = 10.0

    func _init() -> void:
        name = "Safe Zone"
        description = "A battle royale mode where the safe zone gradually shrinks, and balls take continuous damage outside of it."

    func setup(world, balls: Array) -> void:
        super.setup(world, balls)
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
            world.dead_balls = []

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        if not "dead_balls" in world:
            world.dead_balls = []

        for b in balls:
            if not b.alive:
                if not world.dead_balls.has(b):
                    if b.has_method("set_meta"):
                        b.set_meta("time_since_death", 0.0)
                    world.dead_balls.append(b)
                else:
                    if b.has_method("get_meta") and b.has_meta("time_since_death"):
                        b.set_meta("time_since_death", b.get_meta("time_since_death") + delta)

        # Shrink the safe zone
        if zone_radius > min_zone_radius:
            zone_radius -= shrink_rate * delta
            if zone_radius < min_zone_radius:
                zone_radius = min_zone_radius

        # Apply continuous damage outside the safe zone
        var damage_this_tick = outside_damage_per_second * delta
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


class BumperBallsMode extends GameMode:
    func _init() -> void:
        name = "Bumper Balls"
        description = "Balls deal zero damage but bounce each other with much higher knockback. Try to push opponents off the arena!"

    func setup(world, balls: Array) -> void:
        if not "dead_balls" in world:
            world.dead_balls = []
        for b in balls:
            b.damage = 0.0

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

var GAME_MODES = {
    "tournament": TournamentMode.new(),
    "bumper_balls": BumperBallsMode.new(),
    "portal_node": PortalNodeMode.new(),
	"memory_traps": MemoryTrapsMode.new(),
	"vision_reduced": VisionReducedMode.new(),
	"dynamic_hazards": DynamicHazardsMode.new(),
	"custom_match": CustomMatchMode.new(),
	"reverse_event": ReverseEventMode.new(),
    "weather_chaos": WeatherChaosMode.new(),
    "domination": DominationMode.new(),
    "black_hole": BlackHoleMode.new(),
    "king_of_the_hill": KingOfTheHillMode.new(),
    "moving_zone": MovingZoneMode.new(),
    "vampire_royale": VampireRoyaleMode.new(),
    "battle_royale": BattleRoyaleMode.new(),
    "team_deathmatch": TeamDeathmatchMode.new(),
    "zombie_infection": ZombieInfectionMode.new(),
    "boss_fight": BossFightMode.new(),
    "vip_defense": VIPDefenseMode.new(),
    "survival": SurvivalMode.new(),
    "capture_the_flag": CaptureTheFlagMode.new(),
    "evolutionary_simulation": EvolutionarySimulationMode.new(),
    "interactive_training": load("res://src/ai/interactive_training.gd").new(),
    "safe_zone": SafeZoneMode.new()
}
