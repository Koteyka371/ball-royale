extends "res://src/ai/game_modes.gd".GameMode

var team_health = {}
var team_max_health = {}

func _init():
    name = "Shared Health Pool"
    description = "Teams share a single massive health pool. Taking damage drains from the collective pool. When it reaches 0, the entire team is eliminated simultaneously."

func setup(world, balls: Array) -> void:
    .setup(world, balls)
    team_health.clear()
    team_max_health.clear()

    for b in balls:
        var alive = false
        var ball_type = ""
        var team = "unknown"
        var hp = 100.0
        var max_hp = 100.0

        if typeof(b) == TYPE_DICTIONARY:
            alive = b.get("alive", false)
            ball_type = b.get("ball_type", "")
            team = b.get("team", ball_type)
            hp = b.get("hp", 100.0)
            max_hp = b.get("max_hp", 100.0)
        elif typeof(b) == TYPE_OBJECT:
            alive = b.get("alive") if b.get("alive") != null else false
            ball_type = b.get("ball_type") if b.get("ball_type") != null else ""
            team = b.get("team") if b.get("team") != null else ball_type
            hp = b.get("hp") if b.get("hp") != null else 100.0
            max_hp = b.get("max_hp") if b.get("max_hp") != null else 100.0

        if not alive or ball_type == "spectator":
            continue

        if not team_max_health.has(team):
            team_max_health[team] = 0.0
            team_health[team] = 0.0

        team_max_health[team] += max_hp
        team_health[team] += hp

    for b in balls:
        var alive = false
        var ball_type = ""
        var team = "unknown"

        if typeof(b) == TYPE_DICTIONARY:
            alive = b.get("alive", false)
            ball_type = b.get("ball_type", "")
            team = b.get("team", ball_type)
        elif typeof(b) == TYPE_OBJECT:
            alive = b.get("alive") if b.get("alive") != null else false
            ball_type = b.get("ball_type") if b.get("ball_type") != null else ""
            team = b.get("team") if b.get("team") != null else ball_type

        if not alive or ball_type == "spectator":
            continue

        if typeof(b) == TYPE_DICTIONARY:
            b["max_hp"] = team_max_health[team]
            b["hp"] = team_health[team]
        elif typeof(b) == TYPE_OBJECT:
            if b.has_method("set_meta"):
                b.set_meta("max_hp", team_max_health[team])
                b.set_meta("hp", team_health[team])
            else:
                b.set("max_hp", team_max_health[team])
                b.set("hp", team_health[team])

func tick(world, balls: Array, delta: float) -> void:
    var current_team_members = {}

    for b in balls:
        var alive = false
        var ball_type = ""
        var team = "unknown"
        var hp = 0.0

        if typeof(b) == TYPE_DICTIONARY:
            alive = b.get("alive", false)
            ball_type = b.get("ball_type", "")
            team = b.get("team", ball_type)
            hp = b.get("hp", 0.0)
        elif typeof(b) == TYPE_OBJECT:
            alive = b.get("alive") if b.get("alive") != null else false
            ball_type = b.get("ball_type") if b.get("ball_type") != null else ""
            team = b.get("team") if b.get("team") != null else ball_type
            hp = b.get("hp") if b.get("hp") != null else 0.0

        if not alive or ball_type == "spectator":
            continue

        if not current_team_members.has(team):
            current_team_members[team] = []
        current_team_members[team].append(b)

    for team in current_team_members.keys():
        if not team_health.has(team):
            continue

        var members = current_team_members[team]
        var total_damage = 0.0
        var total_healing = 0.0

        for m in members:
            var hp = 0.0
            if typeof(m) == TYPE_DICTIONARY:
                hp = m.get("hp", 0.0)
            elif typeof(m) == TYPE_OBJECT:
                hp = m.get("hp") if m.get("hp") != null else 0.0

            if hp < team_health[team]:
                total_damage += (team_health[team] - hp)
            elif hp > team_health[team]:
                total_healing += (hp - team_health[team])

        if total_damage > 0.0:
            team_health[team] -= total_damage
        elif total_healing > 0.0:
            team_health[team] += total_healing

        if team_health[team] <= 0:
            team_health[team] = 0
            for m in members:
                if typeof(m) == TYPE_DICTIONARY:
                    m["hp"] = 0
                    m["alive"] = false
                elif typeof(m) == TYPE_OBJECT:
                    if m.has_method("set_meta"):
                        m.set_meta("hp", 0)
                        m.set_meta("alive", false)
                    else:
                        m.set("hp", 0)
                        m.set("alive", false)

                var world_has_event = false
                if typeof(world) == TYPE_DICTIONARY:
                    if world.has("add_event"):
                        world_has_event = true
                elif typeof(world) == TYPE_OBJECT:
                    if world.has_method("add_event"):
                        world_has_event = true

                if world_has_event:
                    var m_id = null
                    if typeof(m) == TYPE_DICTIONARY:
                        m_id = m.get("id", null)
                    elif typeof(m) == TYPE_OBJECT:
                        m_id = m.get("id") if m.get("id") != null else null

                    if typeof(world) == TYPE_DICTIONARY:
                        world["add_event"].call("player_died", {"player_id": m_id})
                    else:
                        world.add_event("player_died", {"player_id": m_id})
        else:
            var team_max = team_max_health[team] if team_max_health.has(team) else 100.0
            for m in members:
                if typeof(m) == TYPE_DICTIONARY:
                    m["hp"] = team_health[team]
                    m["max_hp"] = team_max
                elif typeof(m) == TYPE_OBJECT:
                    if m.has_method("set_meta"):
                        m.set_meta("hp", team_health[team])
                        m.set_meta("max_hp", team_max)
                    else:
                        m.set("hp", team_health[team])
                        m.set("max_hp", team_max)
