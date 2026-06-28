class_name GameModes

class GameMode:
    var name: String = "Unknown"
    var description: String = "Base game mode"

    func _init() -> void:
        pass

    func setup(world, balls: Array) -> void:
        pass

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        pass


    func check_winner(world, balls: Array):
        return null

class BattleRoyaleMode extends GameMode:
    func _init() -> void:
        name = "Battle Royale"
        description = "Last man standing. Everyone for themselves."

    func setup(world, balls: Array) -> void:
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
            if has_method("_award_skill_points"): _award_skill_points()
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if has_method("_award_skill_points"): _award_skill_points()
            return alive[0].ball_type

        return null


class KingOfTheHillMode extends GameMode:
    var tick_timer = 0.0

    func _init() -> void:
        name = "King of the Hill"
        description = "Stay in the center area to earn points. First to 100 points wins."

    func setup(world, balls: Array) -> void:
        for b in balls:
            if b.ball_type != "spectator":
                b.set_meta("score", 0)

    func tick(world, balls: Array, delta: float = 0.016) -> void:
        tick_timer += delta
        if tick_timer >= 0.5:
            tick_timer = 0.0

            var arena_width = 1000
            var arena_height = 1000
            if world != null and "arena" in world and world.arena != null:
                if "width" in world.arena:
                    arena_width = world.arena.width
                if "height" in world.arena:
                    arena_height = world.arena.height

            var center_x = arena_width / 2.0
            var center_y = arena_height / 2.0
            var zone_radius = min(arena_width, arena_height) * 0.2

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
                    # Cap max pull to avoid crazy speeds
                    pull_strength = min(pull_strength, 150.0)

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
            if has_method("_award_skill_points"): _award_skill_points()
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if has_method("_award_skill_points"): _award_skill_points()
            return alive[0].ball_type

        return null


class MinefieldMode extends GameMode:
    func _init() -> void:
        name = "Minefield"
        description = "The arena is littered with invisible traps. Memory and caution are your best friends."

    func setup(world, balls: Array) -> void:
        for b in balls:
            if b.ball_type != "spectator":
                if not "team" in b:
                    b.team = b.ball_type

        if world != null and "arena" in world and world.arena != null:
            var arena_width = 1000.0
            var arena_height = 1000.0
            if "width" in world.arena:
                arena_width = world.arena.width
            if "height" in world.arena:
                arena_height = world.arena.height

            for i in range(50):
                var x = 50.0 + randf() * (arena_width - 100.0)
                var y = 50.0 + randf() * (arena_height - 100.0)
                var radius = 15.0 + randf() * 15.0
                var h_id = 20000 + i
                var trap = ProceduralArena.Hazard.new()
                trap.id = h_id
                trap.x = x
                trap.y = y
                trap.radius = radius
                trap.kind = "trap"
                trap.damage = 20.0
                trap.set_meta("is_invisible", true)
                trap.set_meta("duration", 9999.0)

                if "hazards" in world.arena:
                    world.arena.hazards.append(trap)

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
            if has_method("_award_skill_points"): _award_skill_points()
            return teams_alive.keys()[0]

        if alive.size() == 1:
            if has_method("_award_skill_points"): _award_skill_points()
            return alive[0].ball_type

        return null

var GAME_MODES = {
    "minefield": MinefieldMode.new(),
    "black_hole": BlackHoleMode.new(),
    "king_of_the_hill": KingOfTheHillMode.new(),
    "vampire_royale": VampireRoyaleMode.new(),
    "battle_royale": BattleRoyaleMode.new(),
    "team_deathmatch": TeamDeathmatchMode.new(),
    "zombie_infection": ZombieInfectionMode.new(),
    "boss_fight": BossFightMode.new(),
    "vip_defense": VIPDefenseMode.new(),
    "survival": SurvivalMode.new(),
    "capture_the_flag": CaptureTheFlagMode.new(),
    "evolutionary_simulation": EvolutionarySimulationMode.new()
}
