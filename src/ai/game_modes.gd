class_name GameModes

class GameMode:
    var name: String = "Unknown"
    var description: String = "Base game mode"

    func _init() -> void:
        pass

    func setup(world, balls: Array) -> void:
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
            return "Draw"

        var teams_alive = {}
        for b in alive:
            if b.has_method("get") or "team" in b:
                teams_alive[b.team] = true
            else:
                teams_alive[b.ball_type] = true

        if teams_alive.size() == 1:
            return teams_alive.keys()[0]

        if alive.size() == 1:
            return alive[0].ball_type

        return null

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

    func tick(world, balls: Array) -> void:
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

var GAME_MODES = {
    "battle_royale": BattleRoyaleMode.new(),
    "team_deathmatch": TeamDeathmatchMode.new(),
    "zombie_infection": ZombieInfectionMode.new(),
    "boss_fight": BossFightMode.new(),
    "vip_defense": VIPDefenseMode.new(),
    "survival": SurvivalMode.new()
}
