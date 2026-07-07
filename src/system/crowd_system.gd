extends RefCounted

var world
var excitement_level = 0.0
var max_excitement = 100.0
var team_alive_counts = {}
var last_kill_tick = 0
var kill_streak = {}
var active_vote = null
var vote_timer = 0
var votes = {}
var vote_cooldown = 0
var ball_positions = {}
var camping_time = {}
var underdog_team = null
var match_started = false
var match_ended = false

func _init(p_world):
    world = p_world

func tick(balls: Array, kill_log: Array, current_tick: int):
    _check_bets_and_winner(balls, current_tick)
    _update_excitement(current_tick)
    _check_events(balls, kill_log, current_tick)
    _check_camping(balls, current_tick)
    _throw_buffs_if_needed(balls, current_tick)
    _throw_hazards_if_bored(balls, current_tick)
    _process_votes(balls, current_tick)

func _check_bets_and_winner(balls: Array, current_tick: int):
    if not match_started and balls.size() > 1:
        match_started = true
        var teams = {}
        for b in balls:
            var team = ""
            if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                team = b.get("team")
                if team == null or team == "":
                    team = b.get("ball_type")
            elif typeof(b) == TYPE_DICTIONARY:
                team = b.get("team", b.get("ball_type", ""))

            if team != null and team != "" and team != "spectator":
                if teams.has(team):
                    teams[team] += 1
                else:
                    teams[team] = 1

        if teams.keys().size() > 1:
            var min_count = 999999
            for t in teams.keys():
                if teams[t] < min_count:
                    min_count = teams[t]
                    underdog_team = t

            if world != null and world.has_method("add_event") and underdog_team != null:
                world.add_event("crowd_bet", {"message": "The crowd predicts a tough match for the underdog, " + str(underdog_team) + "!"})

    if match_started and not match_ended:
        var alive_teams = {}
        for b in balls:
            var is_alive = false
            var team = ""
            if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                is_alive = b.get("alive") if b.get("alive") != null else false
                team = b.get("team")
                if team == null or team == "":
                    team = b.get("ball_type")
            elif typeof(b) == TYPE_DICTIONARY:
                is_alive = b.get("alive", false)
                team = b.get("team", b.get("ball_type", ""))

            if is_alive and team != null and team != "" and team != "spectator":
                alive_teams[team] = true

        if alive_teams.keys().size() == 1:
            match_ended = true
            var winner = alive_teams.keys()[0]
            if winner == underdog_team:
                excitement_level += 50.0
                if world != null and world.has_method("add_event"):
                    world.add_event("crowd_cheer", {"message": "The underdog " + str(winner) + " has won! The crowd goes absolutely WILD!", "volume": 1.5})
                    world.add_event("audio_event", {"sound": "epic_crowd_roar", "volume": 1.0})

                if world != null and world.has_method("get_profile_manager"):
                    var pm = world.call("get_profile_manager")
                    if pm != null and typeof(pm) == TYPE_OBJECT and pm.get("data") != null:
                        var pdata = pm.get("data")
                        var cur_tokens = 0
                        if typeof(pdata) == TYPE_DICTIONARY and pdata.has("prestige_tokens"):
                            cur_tokens = pdata["prestige_tokens"]
                        if typeof(pdata) == TYPE_DICTIONARY:
                            pdata["prestige_tokens"] = cur_tokens + 10
                        if pm.has_method("save"):
                            pm.call("save")


func _check_camping(balls: Array, current_tick: int):
    for b in balls:
        var is_alive = false
        var b_type = ""
        var b_id = -1
        var b_x = 0.0
        var b_y = 0.0

        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
            is_alive = b.get("alive") if b.get("alive") != null else false
            b_type = b.get("ball_type") if b.get("ball_type") != null else ""
            b_id = b.get("id") if b.get("id") != null else -1
            b_x = float(b.get("x")) if b.get("x") != null else 0.0
            b_y = float(b.get("y")) if b.get("y") != null else 0.0
        elif typeof(b) == TYPE_DICTIONARY:
            is_alive = b.get("alive", false)
            b_type = b.get("ball_type", "")
            b_id = b.get("id", -1)
            b_x = float(b.get("x", 0.0))
            b_y = float(b.get("y", 0.0))

        if is_alive and b_type != "spectator":
            var id_str = str(b_id)
            if ball_positions.has(id_str):
                var old_pos = ball_positions[id_str]
                var dist_sq = (b_x - old_pos[0]) * (b_x - old_pos[0]) + (b_y - old_pos[1]) * (b_y - old_pos[1])

                if dist_sq < 10.0:
                    if not camping_time.has(id_str):
                        camping_time[id_str] = 0
                    camping_time[id_str] += 1
                else:
                    camping_time[id_str] = 0
                    ball_positions[id_str] = [b_x, b_y]

                if camping_time.has(id_str) and camping_time[id_str] >= 50:
                    if world != null and world.has_method("add_event"):
                        world.add_event("crowd_throw", {"message": "The crowd boos and throws debris at a camper!"})
                        world.add_event("spawn_hazard", {"x": b_x, "y": b_y, "kind": "spike_trap"})
                    camping_time[id_str] = 0
            else:
                ball_positions[id_str] = [b_x, b_y]
                camping_time[id_str] = 0

func _update_excitement(current_tick: int):
    if excitement_level > 0:
        excitement_level -= 0.05
    excitement_level = max(0.0, min(excitement_level, max_excitement))

func _check_events(balls: Array, kill_log: Array, current_tick: int):
    if kill_log.is_empty():
        return

    var latest_kill = kill_log[kill_log.size() - 1]
    if typeof(latest_kill) == TYPE_DICTIONARY and latest_kill.has("tick") and latest_kill["tick"] > last_kill_tick:
        last_kill_tick = latest_kill["tick"]
        _handle_kill(latest_kill, current_tick, balls)

    if excitement_level >= 50.0 and current_tick % 200 == 0:
        var alive_teams = {}
        for b in balls:
            if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive"):
                if b.get("ball_type") != "spectator":
                    var team = b.get("team")
                    if team == null or team == "":
                        team = b.get("ball_type")
                    if alive_teams.has(team):
                        alive_teams[team] += 1
                    else:
                        alive_teams[team] = 1
            elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"]:
                if b.get("ball_type") != "spectator":
                    var team = b.get("team")
                    if team == null or team == "":
                        team = b.get("ball_type")
                    if alive_teams.has(team):
                        alive_teams[team] += 1
                    else:
                        alive_teams[team] = 1

        if not alive_teams.is_empty():
            var leading_team = ""
            var max_count = -1
            for t in alive_teams.keys():
                if alive_teams[t] > max_count:
                    max_count = alive_teams[t]
                    leading_team = t

            if max_count >= 2 and world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "Let's go Team %s! Let's go!" % leading_team, "volume": 1.0})
                world.add_event("audio_event", {"sound": "team_chant", "volume": 0.8})

func _handle_kill(kill_info: Dictionary, current_tick: int, balls: Array):
    if not kill_info.has("killer_id"):
        return

    var killer_id = kill_info["killer_id"]

    if not kill_streak.has(killer_id):
        kill_streak[killer_id] = 1
    else:
        kill_streak[killer_id] += 1

    var streak = kill_streak[killer_id]

    if streak >= 3:
        excitement_level += 20.0
        if world != null and world.has_method("add_event"):
            var chant_msg = "The crowd goes wild for Ball %s's %d-kill streak!" % [str(killer_id), streak]
            var killer_obj = null
            for b in balls:
                var b_id = -1
                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    b_id = b.get("id")
                elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
                    b_id = b["id"]
                if str(b_id) == str(killer_id):
                    killer_obj = b
                    break

            if killer_obj != null:
                var k_type = ""
                var k_x = 0.0
                var k_y = 0.0
                if typeof(killer_obj) == TYPE_OBJECT and killer_obj.has_method("get"):
                    k_type = killer_obj.get("ball_type")
                    k_x = float(killer_obj.get("x")) if killer_obj.get("x") != null else 0.0
                    k_y = float(killer_obj.get("y")) if killer_obj.get("y") != null else 0.0
                elif typeof(killer_obj) == TYPE_DICTIONARY:
                    k_type = killer_obj.get("ball_type", "")
                    k_x = float(killer_obj.get("x", 0.0))
                    k_y = float(killer_obj.get("y", 0.0))

                if k_type != null and k_type != "" and k_type.to_lower() != "spectator":
                    k_type = k_type.capitalize()
                    chant_msg = "%s! %s! %s" % [k_type, k_type, chant_msg]

                world.add_event("spawn_booster", {
                    "x": k_x,
                    "y": k_y,
                    "kind": "speed",
                    "value": 30.0
                })

            world.add_event("crowd_cheer", {"message": chant_msg, "volume": 1.0 + (streak * 0.1)})
            world.add_event("audio_event", {"sound": "epic_crowd_roar", "volume": 1.0})

    var alive_teams = {}
    for b in balls:
        if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive"):
            if b.get("ball_type") != "spectator":
                var team = b.get("team")
                if team == null or team == "":
                    team = b.get("ball_type")
                if alive_teams.has(team):
                    alive_teams[team] += 1
                else:
                    alive_teams[team] = 1
        elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"]:
            if b.get("ball_type") != "spectator":
                var team = b.get("team")
                if team == null or team == "":
                    team = b.get("ball_type")
                if alive_teams.has(team):
                    alive_teams[team] += 1
                else:
                    alive_teams[team] = 1

    var killer = null
    for b in balls:
        var b_id = -1
        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
            b_id = b.get("id")
        elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
            b_id = b["id"]

        if str(b_id) == str(killer_id):
            killer = b
            break

    if killer != null:
        var killer_team = ""
        if typeof(killer) == TYPE_OBJECT and killer.has_method("get"):
            killer_team = killer.get("team")
            if killer_team == null or killer_team == "":
                killer_team = killer.get("ball_type")
        elif typeof(killer) == TYPE_DICTIONARY:
            killer_team = killer.get("team", killer.get("ball_type", ""))

        var killer_team_count = 0
        if alive_teams.has(killer_team):
            killer_team_count = alive_teams[killer_team]

        var total_enemies = 0
        for t in alive_teams.keys():
            if t != killer_team:
                total_enemies += alive_teams[t]

        if killer_team_count > 0 and total_enemies >= killer_team_count * 3:
            excitement_level += 30.0
            if world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "The crowd roars for an incredible comeback attempt!", "volume": 1.2})
                world.add_event("audio_event", {"sound": "comeback_cheer", "volume": 1.0})

    var victim_id = kill_info.get("victim_id")
    var victim = null
    if victim_id != null:
        for b in balls:
            var b_id = -1
            if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                b_id = b.get("id")
            elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
                b_id = b["id"]

            if str(b_id) == str(victim_id):
                victim = b
                break

        if victim != null:
            var victim_team = ""
            if typeof(victim) == TYPE_OBJECT and victim.has_method("get"):
                victim_team = victim.get("team")
                if victim_team == null or victim_team == "":
                    victim_team = victim.get("ball_type")
            elif typeof(victim) == TYPE_DICTIONARY:
                victim_team = victim.get("team", victim.get("ball_type", ""))

            var victim_team_count = 0
            if alive_teams.has(victim_team):
                victim_team_count = alive_teams[victim_team]

            if victim_team_count == 0:
                excitement_level += 25.0
                if world != null and world.has_method("add_event"):
                    world.add_event("crowd_cheer", {"message": "The crowd gasps as team " + str(victim_team) + " is wiped out!", "volume": 1.1})
                    world.add_event("audio_event", {"sound": "team_wipe_gasp", "volume": 1.0})


func _throw_buffs_if_needed(balls: Array, current_tick: int):
    if excitement_level < 50.0:
        return

    if randf() < 0.01:
        var alive_balls = []
        for b in balls:
            if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") and b.get("ball_type") != "spectator":
                alive_balls.append(b)
            elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"] and b.get("ball_type") != "spectator":
                alive_balls.append(b)

        if alive_balls.is_empty():
            return

        var losing_ball = alive_balls[0]
        var lowest_hp_pct = 1.0

        for b in alive_balls:
            var hp = 0.0
            var max_hp = 100.0
            if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                hp = float(b.get("hp")) if b.get("hp") != null else 0.0
                max_hp = float(b.get("max_hp")) if b.get("max_hp") != null else 100.0
            elif typeof(b) == TYPE_DICTIONARY:
                hp = float(b.get("hp", 0.0))
                max_hp = float(b.get("max_hp", 100.0))

            var hp_pct = hp / max(1.0, max_hp)
            if hp_pct < lowest_hp_pct:
                lowest_hp_pct = hp_pct
                losing_ball = b

        if world != null and world.has_method("add_event"):
            var b_x = 0.0
            var b_y = 0.0
            if typeof(losing_ball) == TYPE_OBJECT and losing_ball.has_method("get"):
                b_x = float(losing_ball.get("x")) if losing_ball.get("x") != null else 0.0
                b_y = float(losing_ball.get("y")) if losing_ball.get("y") != null else 0.0
            elif typeof(losing_ball) == TYPE_DICTIONARY:
                b_x = float(losing_ball.get("x", 0.0))
                b_y = float(losing_ball.get("y", 0.0))

            world.add_event("spawn_booster", {
                "x": b_x,
                "y": b_y,
                "kind": "speed",
                "value": 30.0
            })
            world.add_event("crowd_throw", {"message": "The crowd throws a speed pad to help a struggling player!"})
            excitement_level -= 10.0

func _throw_hazards_if_bored(balls: Array, current_tick: int):
    if excitement_level >= 20.0:
        return

    if randf() < 0.01:
        var alive_balls = []
        for b in balls:
            if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") and b.get("ball_type") != "spectator":
                alive_balls.append(b)
            elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"] and b.get("ball_type") != "spectator":
                alive_balls.append(b)

        if alive_balls.is_empty():
            return

        var target_ball = alive_balls[randi() % alive_balls.size()]
        var hazard_kinds = ["temporary_wall", "slow_field", "mini_bomb"]
        var hazard_kind = hazard_kinds[randi() % hazard_kinds.size()]

        if world != null and world.has_method("add_event"):
            var b_x = 0.0
            var b_y = 0.0
            if typeof(target_ball) == TYPE_OBJECT and target_ball.has_method("get"):
                b_x = float(target_ball.get("x")) if target_ball.get("x") != null else 0.0
                b_y = float(target_ball.get("y")) if target_ball.get("y") != null else 0.0
            elif typeof(target_ball) == TYPE_DICTIONARY:
                b_x = float(target_ball.get("x", 0.0))
                b_y = float(target_ball.get("y", 0.0))

            world.add_event("spawn_hazard", {
                "x": b_x + (randf() * 100.0 - 50.0),
                "y": b_y + (randf() * 100.0 - 50.0),
                "kind": hazard_kind
            })
            world.add_event("crowd_throw", {"message": "The crowd boos and throws a hazard into the arena!"})
            excitement_level += 5.0

func _process_votes(balls: Array, current_tick: int):
    if vote_cooldown > 0:
        vote_cooldown -= 1

    if active_vote == null:
        if vote_cooldown == 0 and excitement_level >= 30.0 and randf() < 0.001:
            _start_vote(balls)
        return

    vote_timer -= 1

    if randf() < 0.05:
        _simulate_spectator_vote()

    if vote_timer <= 0:
        _resolve_vote(balls)

func _start_vote(balls: Array):
    var vote_types = [
        {"type": "spawn_hazard", "options": ["lava_pit", "spike_trap", "poison_cloud"]},
        {"type": "player_buff", "options": ["speed", "damage", "shield"]}
    ]
    var chosen_vote = vote_types[randi() % vote_types.size()]

    active_vote = {
        "type": chosen_vote["type"],
        "options": chosen_vote["options"]
    }

    votes = {}
    for opt in chosen_vote["options"]:
        votes[opt] = 0

    vote_timer = 200

    if world != null and world.has_method("add_event"):
        var options_str = ""
        for i in range(chosen_vote["options"].size()):
            options_str += chosen_vote["options"][i]
            if i < chosen_vote["options"].size() - 1:
                options_str += ", "

        world.add_event("vote_started", {
            "message": "A crowd vote has started for: " + chosen_vote["type"] + "! Options: " + options_str
        })
        world.add_event("audio_event", {"sound": "vote_start_chime", "volume": 1.0})

func _simulate_spectator_vote():
    if active_vote == null or votes.is_empty():
        return

    var options = votes.keys()
    if options.size() > 0:
        var chosen = options[randi() % options.size()]
        votes[chosen] += 1

func _resolve_vote(balls: Array):
    if active_vote == null or votes.is_empty():
        active_vote = null
        return

    var winning_option = ""
    var max_votes = -1

    for opt in votes.keys():
        if votes[opt] > max_votes:
            max_votes = votes[opt]
            winning_option = opt

    var vote_type = active_vote["type"]

    if world != null and world.has_method("add_event"):
        world.add_event("vote_ended", {
            "message": "The crowd has spoken! The winner is " + winning_option + " with " + str(max_votes) + " votes!"
        })
        world.add_event("audio_event", {"sound": "vote_end_cheer", "volume": 1.0})

    var alive_balls = []
    for b in balls:
        if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") and b.get("ball_type") != "spectator":
            alive_balls.append(b)
        elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"] and b.get("ball_type") != "spectator":
            alive_balls.append(b)

    if not alive_balls.is_empty():
        var target = alive_balls[randi() % alive_balls.size()]

        var t_x = 0.0
        var t_y = 0.0
        if typeof(target) == TYPE_OBJECT and target.has_method("get"):
            t_x = float(target.get("x")) if target.get("x") != null else 0.0
            t_y = float(target.get("y")) if target.get("y") != null else 0.0
        elif typeof(target) == TYPE_DICTIONARY:
            t_x = float(target.get("x", 0.0))
            t_y = float(target.get("y", 0.0))

        if vote_type == "spawn_hazard":
            if world != null and world.has_method("add_event"):
                world.add_event("spawn_hazard", {
                    "x": t_x,
                    "y": t_y,
                    "kind": winning_option
                })
        elif vote_type == "player_buff":
            if world != null and world.has_method("add_event"):
                world.add_event("spawn_booster", {
                    "x": t_x,
                    "y": t_y,
                    "kind": winning_option,
                    "value": 50.0
                })

    active_vote = null
    votes.clear()
    vote_cooldown = 1000
