extends RefCounted

var world
var excitement_level = 0.0
var corruptibility_level = 0.5
var max_excitement = 100.0
var team_alive_counts = {}
var last_kill_tick = 0
var kill_streak = {}
var active_vote = null
var vote_timer = 0
var votes = {}
var vote_cooldown = 0
var active_global_modifier = null
var global_modifier_timer = 0
var ball_positions = {}
var camping_time = {}
var underdog_team = null
var match_started = false
var match_ended = false
var external_commands = []
var has_real_spectators = false
var viewer_loyalty = {}
var user_votes = {}
var viewer_vote_streaks = {}
var current_vote_participants = []

func _init(p_world):
    world = p_world



func _add_viewer_loyalty(user: String, points: int):
    var current_points = 0
    if viewer_loyalty.has(user):
        current_points = viewer_loyalty[user]
    viewer_loyalty[user] = current_points + points

    if world != null and typeof(world) == TYPE_OBJECT and world.has("leaderboard_manager") and world.leaderboard_manager != null:
        if world.leaderboard_manager.has_method("record_viewer_loyalty"):
            world.leaderboard_manager.record_viewer_loyalty(user, points)
    elif world != null and typeof(world) == TYPE_DICTIONARY and world.has("leaderboard_manager") and world["leaderboard_manager"] != null:
        if world["leaderboard_manager"].has_method("record_viewer_loyalty"):
            world["leaderboard_manager"].record_viewer_loyalty(user, points)

func _get_user_display(user: String) -> String:
    var badge = ""
    if world != null and typeof(world) == TYPE_OBJECT and world.has("leaderboard_manager") and world.leaderboard_manager != null:
        if world.leaderboard_manager.has_method("get_viewer_badge"):
            badge = world.leaderboard_manager.get_viewer_badge(user)
    elif world != null and typeof(world) == TYPE_DICTIONARY and world.has("leaderboard_manager") and world["leaderboard_manager"] != null:
        if world["leaderboard_manager"].has_method("get_viewer_badge"):
            badge = world["leaderboard_manager"].get_viewer_badge(user)
    else:
        var points = 0
        if viewer_loyalty.has(user):
            points = viewer_loyalty[user]
        if points >= 50:
            badge = "👑"
        elif points >= 20:
            badge = "⭐"

    if badge != "":
        return badge + " " + user
    return user

func queue_external_command(user: String, command: String):
    external_commands.append({"user": user, "command": command})
    has_real_spectators = true

func process_external_command(user: String, command: String, balls: Array):
    var parts = command.strip_edges().split(" ", false)
    if parts.size() == 0:
        return

    var cmd = parts[0].to_lower()
    var alive_balls = []
    for b in balls:
        if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") and b.get("ball_type") != "spectator":
            alive_balls.append(b)
        elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"] and b.get("ball_type") != "spectator":
            alive_balls.append(b)

    if cmd == "!spawn" and parts.size() >= 2:
        var hazard_kind = parts[1]
        var target = null
        if parts.size() >= 3:
            var tid = parts[2].to_int()
            for b in alive_balls:
                var b_id = -1
                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    b_id = b.get("id")
                elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
                    b_id = b["id"]
                if b_id == tid:
                    target = b
                    break

        if target == null and not alive_balls.is_empty():
            target = alive_balls[randi() % alive_balls.size()]

        if target != null and world != null and world.has_method("add_event"):
            var t_x = 0.0
            var t_y = 0.0
            if typeof(target) == TYPE_OBJECT and target.has_method("get"):
                t_x = float(target.get("x")) if target.get("x") != null else 0.0
                t_y = float(target.get("y")) if target.get("y") != null else 0.0
            elif typeof(target) == TYPE_DICTIONARY:
                t_x = float(target.get("x", 0.0))
                t_y = float(target.get("y", 0.0))

            world.add_event("spawn_hazard", {
                "x": t_x,
                "y": t_y,
                "kind": hazard_kind
            })
            _add_viewer_loyalty(user, 5)
            world.add_event("crowd_throw", {"message": "Viewer " + _get_user_display(user) + " spawned a " + hazard_kind + "!"})
            excitement_level += 5.0

    elif cmd == "!control" and parts.size() >= 4:
        var hazard_kind = parts[1]
        var target_x = parts[2].to_float()
        var target_y = parts[3].to_float()

        if world != null and world.has_method("get") and world.get("arena") != null:
            var arena = world.get("arena")
            if typeof(arena) == TYPE_OBJECT and arena.has_method("get") and arena.get("hazards") != null:
                var hazards = arena.get("hazards")
                var matching_hazards = []
                for h in hazards:
                    var k = null
                    if typeof(h) == TYPE_OBJECT and h.has_method("get"):
                        k = h.get("kind")
                    elif typeof(h) == TYPE_DICTIONARY and h.has("kind"):
                        k = h["kind"]

                    if k == hazard_kind:
                        matching_hazards.append(h)

                if matching_hazards.size() > 0:
                    var hazard = matching_hazards[randi() % matching_hazards.size()]
                    if typeof(hazard) == TYPE_OBJECT and hazard.has_method("set"):
                        hazard.set("controlled_by", user)
                        hazard.set("control_timer", 10.0)
                        hazard.set("control_target_x", target_x)
                        hazard.set("control_target_y", target_y)
                    elif typeof(hazard) == TYPE_DICTIONARY:
                        hazard["controlled_by"] = user
                        hazard["control_timer"] = 10.0
                        hazard["control_target_x"] = target_x
                        hazard["control_target_y"] = target_y

                    _add_viewer_loyalty(user, 15)
                    if world.has_method("add_event"):
                        world.add_event("crowd_cheer", {"message": "Viewer " + _get_user_display(user) + " took control of a " + hazard_kind + "!"})
                        excitement_level += 10.0

    elif cmd == "!weather" and parts.size() >= 2:
        if excitement_level >= 50.0:
            var weather_type = parts[1].to_lower()
            if weather_type == "hot" or weather_type == "heatwave":
                if typeof(world) == TYPE_OBJECT and "arena" in world and typeof(world.arena) == TYPE_OBJECT and "temperature" in world.arena:
                    world.arena.temperature = 50.0
                elif typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("temperature"):
                    world.arena["temperature"] = 50.0
                if world != null and world.has_method("add_event"):
                    world.add_event("arena_modifier", {"temperature": 50.0})
                    _add_viewer_loyalty(user, 10)
                    world.add_event("crowd_cheer", {"message": "Viewer " + _get_user_display(user) + " made it HOT!"})
            elif weather_type == "cold" or weather_type == "blizzard" or weather_type == "snow":
                if typeof(world) == TYPE_OBJECT and "arena" in world and typeof(world.arena) == TYPE_OBJECT and "temperature" in world.arena:
                    world.arena.temperature = -20.0
                elif typeof(world) == TYPE_DICTIONARY and world.has("arena") and typeof(world.arena) == TYPE_DICTIONARY and world.arena.has("temperature"):
                    world.arena["temperature"] = -20.0
                if world != null and world.has_method("add_event"):
                    world.add_event("arena_modifier", {"temperature": -20.0})
                    _add_viewer_loyalty(user, 10)
                    world.add_event("crowd_cheer", {"message": "Viewer " + _get_user_display(user) + " made it COLD!"})
            else:
                if world != null and world.has_method("add_event"):
                    var target = null
                    if not alive_balls.is_empty():
                        target = alive_balls[randi() % alive_balls.size()]
                    if target != null:
                        var t_x = 0.0
                        var t_y = 0.0
                        if typeof(target) == TYPE_OBJECT and target.has_method("get"):
                            t_x = float(target.get("x")) if target.get("x") != null else 0.0
                            t_y = float(target.get("y")) if target.get("y") != null else 0.0
                        elif typeof(target) == TYPE_DICTIONARY:
                            t_x = float(target.get("x", 0.0))
                            t_y = float(target.get("y", 0.0))
                        world.add_event("spawn_hazard", {
                            "x": t_x,
                            "y": t_y,
                            "kind": weather_type
                        })
                        _add_viewer_loyalty(user, 10)
                        world.add_event("crowd_cheer", {"message": "Viewer " + _get_user_display(user) + " summoned a " + weather_type + "!"})
            excitement_level -= 10.0

    elif cmd == "!drop" and parts.size() >= 2:
        var booster_kind = parts[1]
        var target = null
        if parts.size() >= 3:
            var tid = parts[2].to_int()
            for b in alive_balls:
                var b_id = -1
                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    b_id = b.get("id")
                elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
                    b_id = b["id"]
                if b_id == tid:
                    target = b
                    break

        if target == null and not alive_balls.is_empty():
            target = alive_balls[randi() % alive_balls.size()]

        if target != null and world != null and world.has_method("add_event"):
            var t_x = 0.0
            var t_y = 0.0
            if typeof(target) == TYPE_OBJECT and target.has_method("get"):
                t_x = float(target.get("x")) if target.get("x") != null else 0.0
                t_y = float(target.get("y")) if target.get("y") != null else 0.0
            elif typeof(target) == TYPE_DICTIONARY:
                t_x = float(target.get("x", 0.0))
                t_y = float(target.get("y", 0.0))

            world.add_event("spawn_booster", {
                "x": t_x,
                "y": t_y,
                "kind": booster_kind,
                "value": 30.0
            })
            _add_viewer_loyalty(user, 5)
            world.add_event("crowd_throw", {"message": "Viewer " + _get_user_display(user) + " dropped a " + booster_kind + " booster!"})
            excitement_level += 5.0

    elif cmd == "!emote" and parts.size() >= 2:
        var emote_type = parts[1]
        var target = null
        if parts.size() >= 3:
            var tid = parts[2].to_int()
            for b in alive_balls:
                var b_id = -1
                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    b_id = b.get("id")
                elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
                    b_id = b["id"]
                if b_id == tid:
                    target = b
                    break

        if target == null and not alive_balls.is_empty():
            target = alive_balls[randi() % alive_balls.size()]

        if target != null and world != null and world.has_method("add_event"):
            var t_x = 0.0
            var t_y = 0.0
            if typeof(target) == TYPE_OBJECT:
                t_x = float(target.get("x", 0.0))
                t_y = float(target.get("y", 0.0))
            elif typeof(target) == TYPE_DICTIONARY:
                t_x = float(target.get("x", 0.0))
                t_y = float(target.get("y", 0.0))

            world.add_event("spawn_hazard", {
                "x": t_x,
                "y": t_y,
                "kind": "emote",
                "emoji": emote_type
            })
            _add_viewer_loyalty(user, 5)
            world.add_event("crowd_throw", {"message": "Viewer " + _get_user_display(user) + " spawned a " + emote_type + " emote!"})
            excitement_level += 2.0

    elif cmd == "!vote" and parts.size() >= 2:
        var option = parts[1]
        if active_vote != null and votes.has(option):
            if user_votes.has(user):
                return

            var streak = 0
            if viewer_vote_streaks.has(user):
                streak = viewer_vote_streaks[user]

            var vote_weight = 1 + streak
            user_votes[user] = option

            if not current_vote_participants.has(user):
                current_vote_participants.append(user)

            votes[option] += vote_weight

            if world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "Viewer " + _get_user_display(user) + " voted for " + option + " (Power: " + str(vote_weight) + ")!"})

    elif cmd == "!bounty" and parts.size() >= 2:
        var target_id = parts[1]
        var target = null
        for b in alive_balls:
            var b_id = ""
            if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                b_id = str(b.get("id"))
            elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
                b_id = str(b["id"])
            if b_id == target_id:
                target = b
                break

        if target != null:
            if typeof(target) == TYPE_OBJECT and target.has_method("set"):
                target.set_meta("crowd_bounty_timer", 600)
            elif typeof(target) == TYPE_DICTIONARY:
                target["crowd_bounty_timer"] = 600

            if world != null and world.has_method("add_event"):
                var t_id = -1
                var b_type = "Player"
                if typeof(target) == TYPE_OBJECT and target.has_method("get"):
                    t_id = target.get("id")
                    if target.get("ball_type") != null:
                        b_type = target.get("ball_type")
                elif typeof(target) == TYPE_DICTIONARY:
                    if target.has("id"): t_id = target["id"]
                    if target.has("ball_type"): b_type = target["ball_type"]
                world.add_event("visual_effect", {"type": "bounty_mark", "target_id": t_id})
                world.add_event("crowd_cheer", {"message": "Viewer " + _get_user_display(user) + " placed a bounty on " + b_type + " " + str(target_id) + "!"})
            excitement_level += 10.0

    elif cmd == "!bribe" and parts.size() >= 2:
        var action = parts[1]
        var option = ""
        if parts.size() >= 3:
            option = parts[2]
        player_bribe_vote(user, action, option)

func player_bribe_vote(player_id: String, action: String, option: String = "") -> bool:
    if active_vote == null or votes.is_empty():
        return false

    if action != "cancel" and (action != "skew" or not votes.has(option)):
        return false

    var pm = null
    if world != null and world.has_method("get_profile_manager"):
        pm = world.get_profile_manager()
    elif typeof(world) == TYPE_OBJECT and "profile_manager" in world:
        pm = world.profile_manager
    elif typeof(world) == TYPE_DICTIONARY and world.has("profile_manager"):
        pm = world["profile_manager"]

    if pm == null:
        return false

    var pm_data = null
    if typeof(pm) == TYPE_OBJECT and pm.has_method("get"):
        pm_data = pm.get("data")
    elif typeof(pm) == TYPE_DICTIONARY and pm.has("data"):
        pm_data = pm["data"]
    elif typeof(pm) == TYPE_DICTIONARY:
        pm_data = pm

    if pm_data == null:
        return false

    var currency_type = "skill_points"
    var currency_cost = int(max(10, 50 * (2.0 - corruptibility_level * 1.5)))
    var bid_power = currency_cost

    var current_sp = pm_data.get("skill_points", 0)
    var current_pt = pm_data.get("prestige_tokens", 0)

    if current_sp >= currency_cost:
        pm_data["skill_points"] = current_sp - currency_cost
    elif current_pt >= 1:
        pm_data["prestige_tokens"] = current_pt - 1
        bid_power = 100
        currency_type = "prestige_tokens"
    else:
        return false

    if vote_bids.has(player_id):
        vote_bids[player_id]["amount"] += bid_power
        vote_bids[player_id]["action"] = action
        if option != "":
            vote_bids[player_id]["option"] = option
    else:
        vote_bids[player_id] = {"amount": bid_power, "action": action, "option": option}

    if vote_bids.size() == 1:
        vote_auction_timer = 300
        if world != null and world.has_method("add_event"):
            world.add_event("bribe_attempt", {"message": "Player " + player_id + " is attempting to bribe the vote! 5 seconds to counter-bid!"})
    elif vote_bids.size() >= 2 and not vote_auction_active:
        vote_auction_active = true
        vote_auction_timer = 300
        if world != null and world.has_method("add_event"):
            world.add_event("auction_started", {"message": "Multiple players are bribing! A short auction has started!"})

    return true

func _process_external_commands(balls: Array):
    while external_commands.size() > 0:
        var cmd_info = external_commands.pop_front()
        process_external_command(cmd_info["user"], cmd_info["command"], balls)

func tick(balls: Array, kill_log: Array, current_tick: int):
    _process_external_commands(balls)
    _check_bets_and_winner(balls, current_tick)
    _update_corruptibility(current_tick)
    _update_excitement(current_tick)
    # Decrement bounty timers
    for b in balls:
        var b_timer = 0
        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
            if b.has_method("get_meta") and b.has_meta("crowd_bounty_timer"):
                b_timer = b.get_meta("crowd_bounty_timer")
        elif typeof(b) == TYPE_DICTIONARY and b.has("crowd_bounty_timer"):
            b_timer = b["crowd_bounty_timer"]

        if b_timer > 0:
            if typeof(b) == TYPE_OBJECT and b.has_method("set"):
                if b.has_method("set_meta"): b.set_meta("crowd_bounty_timer", b_timer - 1)
            elif typeof(b) == TYPE_DICTIONARY:
                b["crowd_bounty_timer"] = b_timer - 1

    _check_events(balls, kill_log, current_tick)
    _check_camping(balls, current_tick)
    _throw_buffs_if_needed(balls, current_tick)
    _throw_hazards_if_bored(balls, current_tick)
    _process_audience_favor(balls, current_tick)
    _process_votes(balls, current_tick)
    _process_spectator_signs(balls, current_tick)
    _process_global_modifier(balls, current_tick)
    _trigger_large_scale_event(balls, current_tick)

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



func _trigger_large_scale_event(balls: Array, current_tick: int):
    if excitement_level >= 10.0:
        return

    if randf() < 0.005:  # 0.5% chance per tick when excitement is critically low
        var event_types = ["closing_zone", "weather_transition"]
        var event_type = event_types[randi() % event_types.size()]

        if world != null and world.has_method("add_event"):
            if event_type == "closing_zone":
                world.add_event("spawn_zone", {
                    "x": 500.0,
                    "y": 500.0,
                    "radius": 1000.0,
                    "shrink_rate": 10.0,
                    "damage": 5.0
                })
                world.add_event("crowd_throw", {"message": "The crowd is bored! A shrinking zone has been deployed!"})
            else:
                var weathers = ["thunderstorm", "blizzard", "acid_rain"]
                var new_weather = weathers[randi() % weathers.size()]
                world.add_event("weather_transition", {"new_weather": new_weather})
                world.add_event("crowd_throw", {"message": "The crowd is falling asleep! They trigger a " + new_weather + "!"})

            excitement_level += 40.0

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

func _update_corruptibility(current_tick: int):
    corruptibility_level = (sin(current_tick * 0.005) + 1.0) / 2.0

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

                if not _has_meta_safe("last_chant_team"):
                    set_meta("last_chant_team", leading_team)
                    set_meta("consecutive_chants", 1)
                elif get_meta("last_chant_team") == leading_team:
                    set_meta("consecutive_chants", get_meta("consecutive_chants") + 1)
                else:
                    if get_meta("consecutive_chants", 0) > 0 and world != null and world.has_method("add_event"):
                        world.add_event("audio_event", {"sound": "bgm_tempo_reset", "volume": 1.0})
                    set_meta("last_chant_team", leading_team)
                    set_meta("consecutive_chants", 1)

                world.add_event("audio_event", {"sound": "bgm_tempo_up", "volume": 1.0, "speed_multiplier": 1.0 + (get_meta("consecutive_chants") * 0.1)})

                if get_meta("consecutive_chants") >= 3:
                    world.add_event("crowd_cheer", {"message": "Team %s is fueled by the crowd's energy! Adrenaline buff applied!" % leading_team, "volume": 1.2})
                    world.add_event("audio_event", {"sound": "adrenaline_rush", "volume": 1.0})
                    world.add_event("visual_effect", {"type": "chant_streak", "team": leading_team})
                    for b in balls:
                        var is_alive = false
                        var team = ""
                        var b_x = 0.0
                        var b_y = 0.0
                        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                            is_alive = b.get("alive") if b.get("alive") != null else false
                            team = b.get("team")
                            if team == null or team == "":
                                team = b.get("ball_type")
                            b_x = float(b.get("x")) if b.get("x") != null else 0.0
                            b_y = float(b.get("y")) if b.get("y") != null else 0.0
                        elif typeof(b) == TYPE_DICTIONARY:
                            is_alive = b.get("alive", false)
                            team = b.get("team", b.get("ball_type", ""))
                            b_x = float(b.get("x", 0.0))
                            b_y = float(b.get("y", 0.0))

                        if is_alive and team == leading_team:
                            var b_id = -1
                            if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                                b_id = b.get("id") if b.get("id") != null else -1
                            elif typeof(b) == TYPE_DICTIONARY:
                                b_id = b.get("id", -1)
                            world.add_event("visual_effect", {"type": "adrenaline_buff", "target_id": b_id})
                            world.add_event("spawn_booster", {
                                "x": b_x,
                                "y": b_y,
                                "kind": "speed",
                                "value": 50.0
                            })
            else:
                if get_meta("consecutive_chants", 0) > 0 and world != null and world.has_method("add_event"):
                    world.add_event("audio_event", {"sound": "bgm_tempo_reset", "volume": 1.0})
                set_meta("last_chant_team", null)
                set_meta("consecutive_chants", 0)
    elif current_tick % 200 == 0:
        if get_meta("consecutive_chants", 0) > 0 and world != null and world.has_method("add_event"):
            world.add_event("audio_event", {"sound": "bgm_tempo_reset", "volume": 1.0})
        set_meta("last_chant_team", null)
        set_meta("consecutive_chants", 0)

func _handle_kill(kill_info: Dictionary, current_tick: int, balls: Array):
    if not kill_info.has("killer_id"):
        return

    var killer_id = kill_info["killer_id"]


    var victim_obj = null
    var killer_obj = null
    for b in balls:
        var b_id = -1
        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
            if b.get("id") != null: b_id = b.get("id")
        elif typeof(b) == TYPE_DICTIONARY and b.has("id"):
            b_id = b["id"]

        if str(b_id) == str(kill_info.get("victim_id", "")):
            victim_obj = b
        if str(b_id) == str(killer_id):
            killer_obj = b

    if victim_obj != null and killer_obj != null:
        var v_timer = 0
        if typeof(victim_obj) == TYPE_OBJECT and victim_obj.has_method("get"):
            if victim_obj.has_method("get_meta") and victim_obj.has_meta("crowd_bounty_timer"):
                v_timer = victim_obj.get_meta("crowd_bounty_timer")
        elif typeof(victim_obj) == TYPE_DICTIONARY and victim_obj.has("crowd_bounty_timer"):
            v_timer = victim_obj["crowd_bounty_timer"]

        if v_timer > 0:
            if typeof(killer_obj) == TYPE_OBJECT and killer_obj.has_method("get") and killer_obj.has_method("set"):
                var k_score = killer_obj.get("score") if killer_obj.get("score") != null else 0
                var k_xp = killer_obj.get("xp") if killer_obj.get("xp") != null else 0
                killer_obj.set("score", k_score + 1000)
                killer_obj.set("xp", k_xp + 500)
            elif typeof(killer_obj) == TYPE_DICTIONARY:
                var k_score = killer_obj.get("score", 0)
                var k_xp = killer_obj.get("xp", 0)
                killer_obj["score"] = k_score + 1000
                killer_obj["xp"] = k_xp + 500

            if world != null and world.has_method("add_event"):
                world.add_event("visual_effect", {"type": "bounty_claimed", "target_id": killer_id})
                world.add_event("crowd_cheer", {"message": "The crowd goes wild as a bounty is claimed!"})

    if not kill_streak.has(killer_id):
        kill_streak[killer_id] = 1
    else:
        kill_streak[killer_id] += 1

    var streak = kill_streak[killer_id]

    if streak >= 3:
        excitement_level += 20.0
        if killer_obj != null:
            var current_favor = 0.0
            if typeof(killer_obj) == TYPE_OBJECT and killer_obj.has_method("get"):
                current_favor = killer_obj.get("audience_favor") if killer_obj.get("audience_favor") != null else 0.0
            elif typeof(killer_obj) == TYPE_DICTIONARY:
                current_favor = killer_obj.get("audience_favor", 0.0)

            var new_favor = min(100.0, current_favor + 20.0)
            if typeof(killer_obj) == TYPE_OBJECT and killer_obj.has_method("set"):
                killer_obj.set("audience_favor", new_favor)
            elif typeof(killer_obj) == TYPE_DICTIONARY:
                killer_obj["audience_favor"] = new_favor
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

            var current_favor = 0.0
            if typeof(killer) == TYPE_OBJECT and killer.has_method("get"):
                current_favor = killer.get("audience_favor") if killer.get("audience_favor") != null else 0.0
            elif typeof(killer) == TYPE_DICTIONARY:
                current_favor = killer.get("audience_favor", 0.0)

            var new_favor = min(100.0, current_favor + 30.0)
            if typeof(killer) == TYPE_OBJECT and killer.has_method("set"):
                killer.set("audience_favor", new_favor)
            elif typeof(killer) == TYPE_DICTIONARY:
                killer["audience_favor"] = new_favor
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

    if not vote_bids.is_empty():
        vote_auction_timer -= 1
        if vote_auction_timer <= 0:
            _resolve_vote_auction(balls)
    else:
        vote_timer -= 1

        if not has_real_spectators:
            if randf() < 0.05:
                _simulate_spectator_vote()

        if vote_timer <= 0:
            _resolve_vote(balls)

func _resolve_vote_auction(balls: Array):
    if vote_bids.is_empty():
        return

    var winner_id = ""
    var highest_bid = -1

    for pid in vote_bids.keys():
        if vote_bids[pid]["amount"] > highest_bid:
            highest_bid = vote_bids[pid]["amount"]
            winner_id = pid

    var bid_info = vote_bids[winner_id]

    if world != null and world.has_method("add_event"):
        world.add_event("auction_ended", {"message": "Player " + winner_id + " won the bribe auction and secured the decision!"})

    var action = bid_info["action"]
    var option = bid_info["option"]

    if action == "cancel":
        if world != null and world.has_method("add_event"):
            world.add_event("vote_cancelled", {"message": "Player " + winner_id + " bribed the crowd to cancel the vote!"})
        active_vote = null
        votes.clear()
        vote_cooldown = 1000
    elif action == "skew":
        if votes.has(option):
            votes[option] += 9999
            if world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "Player " + winner_id + " bribed the crowd to favor " + option + "!"})
            vote_timer = 0

    vote_bids.clear()
    vote_auction_active = false

func _process_spectator_signs(balls: Array, current_tick: int):
    if excitement_level < 10.0 or randf() > 0.01:
        return

    var alive_balls = []
    for b in balls:
        if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") and b.get("ball_type") != "spectator":
            alive_balls.append(b)
        elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"] and b.get("ball_type") != "spectator":
            alive_balls.append(b)

    if alive_balls.is_empty():
        return

    var target = alive_balls[randi() % alive_balls.size()]
    var kills = 0
    var b_type = "Player"
    var b_id = "?"
    var b_x = 0.0
    var b_y = 0.0

    if typeof(target) == TYPE_OBJECT and target.has_method("get"):
        kills = int(target.get("kills")) if target.get("kills") != null else 0
        b_type = str(target.get("ball_type")).capitalize() if target.get("ball_type") != null else "Player"
        b_id = str(target.get("id")) if target.get("id") != null else "?"
        b_x = float(target.get("x")) if target.get("x") != null else 0.0
        b_y = float(target.get("y")) if target.get("y") != null else 0.0
    elif typeof(target) == TYPE_DICTIONARY:
        kills = int(target.get("kills", 0))
        b_type = str(target.get("ball_type", "Player")).capitalize()
        b_id = str(target.get("id", "?"))
        b_x = float(target.get("x", 0.0))
        b_y = float(target.get("y", 0.0))

    var text = ""
    var size = 1.0

    if kills >= 3:
        text = "UNSTOPPABLE " + b_type + "-" + b_id + "!"
        size = 1.5 + (kills * 0.1)
    elif kills > 0:
        text = "GO " + b_type + "-" + b_id + "!"
        size = 1.2 + (kills * 0.1)
    else:
        text = "We believe in " + b_type + "-" + b_id + "!"
        size = 1.0

    if world != null and world.has_method("add_event"):
        var angle = randf() * 2.0 * PI
        var radius = 1000.0

        if typeof(world) == TYPE_OBJECT and world.has_method("get"):
            var arena = world.get("arena")
            if arena != null and typeof(arena) == TYPE_OBJECT and arena.has_method("get"):
                var sz_radius = arena.get("safe_zone_radius")
                if sz_radius != null:
                    radius = float(sz_radius) + 100.0
            elif arena != null and typeof(arena) == TYPE_DICTIONARY and arena.has("safe_zone_radius"):
                radius = float(arena.get("safe_zone_radius", 900.0)) + 100.0
        elif typeof(world) == TYPE_DICTIONARY and world.has("arena"):
            var arena = world["arena"]
            if typeof(arena) == TYPE_DICTIONARY:
                radius = float(arena.get("safe_zone_radius", 900.0)) + 100.0
            elif typeof(arena) == TYPE_OBJECT and arena.has_method("get"):
                var sz_radius = arena.get("safe_zone_radius")
                if sz_radius != null:
                    radius = float(sz_radius) + 100.0

        var sx = b_x + cos(angle) * radius
        var sy = b_y + sin(angle) * radius

        world.add_event("spectator_sign", {
            "x": sx,
            "y": sy,
            "text": text,
            "size": size,
            "duration": 100
        })

func _start_vote(balls: Array):
    var vote_types = [
        {"type": "spawn_hazard", "options": ["lava_pit", "spike_trap", "poison_cloud"]},
        {"type": "player_buff", "options": ["speed", "damage", "shield"]},
        {"type": "global_stat_modifier", "options": ["global_speed_up", "global_damage_up", "global_shield_up"]}
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
        elif vote_type == "global_stat_modifier":
            active_global_modifier = winning_option
            global_modifier_timer = 1800
            if world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "The crowd activated a " + winning_option + " for 30 seconds!", "volume": 1.2})


    for u in user_votes.keys():
        if user_votes[u] == winning_option:
            _add_viewer_loyalty(u, 10)
    user_votes.clear()

    var users_to_remove = []
    for u in viewer_vote_streaks.keys():
        if not current_vote_participants.has(u):
            users_to_remove.append(u)

    for u in users_to_remove:
        viewer_vote_streaks.erase(u)

    for u in current_vote_participants:
        if viewer_vote_streaks.has(u):
            viewer_vote_streaks[u] += 1
        else:
            viewer_vote_streaks[u] = 1

    current_vote_participants.clear()

    active_vote = null
    votes.clear()
    vote_cooldown = 1000

func _has_meta_safe(key: String) -> bool:
    return has_meta(key)


func _process_audience_favor(balls: Array, current_tick: int):
    for b in balls:
        var is_alive = false
        var is_spectator = false

        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
            is_alive = b.get("alive") if b.get("alive") != null else false
            is_spectator = b.get("ball_type") == "spectator"
        elif typeof(b) == TYPE_DICTIONARY:
            is_alive = b.get("alive", false)
            is_spectator = b.get("ball_type") == "spectator"

        if not is_alive or is_spectator:
            continue

        var favor = 0.0
        if typeof(b) == TYPE_OBJECT and b.has_method("get"):
            favor = b.get("audience_favor") if b.get("audience_favor") != null else 0.0
        elif typeof(b) == TYPE_DICTIONARY:
            favor = b.get("audience_favor", 0.0)

        if favor > 0:
            favor = max(0.0, favor - 0.05)
        elif favor < 0:
            favor = min(0.0, favor + 0.05)

        if typeof(b) == TYPE_OBJECT and b.has_method("set"):
            b.set("audience_favor", favor)
        elif typeof(b) == TYPE_DICTIONARY:
            b["audience_favor"] = favor

        if favor >= 50.0:
            if randf() < 0.05:
                var hp = 100.0
                var max_hp = 100.0
                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    hp = b.get("hp") if b.get("hp") != null else 100.0
                    max_hp = b.get("max_hp") if b.get("max_hp") != null else 100.0
                elif typeof(b) == TYPE_DICTIONARY:
                    hp = b.get("hp", 100.0)
                    max_hp = b.get("max_hp", 100.0)

                if hp < max_hp:
                    if typeof(b) == TYPE_OBJECT and b.has_method("set"):
                        b.set("hp", min(hp + 1.0, max_hp))
                    elif typeof(b) == TYPE_DICTIONARY:
                        b["hp"] = min(hp + 1.0, max_hp)

                var a_timer = 0.0
                var s_timer = 0.0
                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    a_timer = b.get("attack_timer") if b.get("attack_timer") != null else 0.0
                    s_timer = b.get("skill_timer") if b.get("skill_timer") != null else 0.0
                elif typeof(b) == TYPE_DICTIONARY:
                    a_timer = b.get("attack_timer", 0.0)
                    s_timer = b.get("skill_timer", 0.0)

                if a_timer > 0:
                    if typeof(b) == TYPE_OBJECT and b.has_method("set"):
                        b.set("attack_timer", max(0.0, a_timer - 0.1))
                    elif typeof(b) == TYPE_DICTIONARY:
                        b["attack_timer"] = max(0.0, a_timer - 0.1)
                if s_timer > 0:
                    if typeof(b) == TYPE_OBJECT and b.has_method("set"):
                        b.set("skill_timer", max(0.0, s_timer - 0.1))
                    elif typeof(b) == TYPE_DICTIONARY:
                        b["skill_timer"] = max(0.0, s_timer - 0.1)

        elif favor <= -50.0:
            if randf() < 0.005:
                var hazard_kinds = ["temporary_wall", "slow_field", "mini_bomb"]
                var hazard_kind = hazard_kinds[randi() % hazard_kinds.size()]
                if world != null and world.has_method("add_event"):
                    var b_x = 0.0
                    var b_y = 0.0
                    var b_id = "?"
                    if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                        b_x = float(b.get("x")) if b.get("x") != null else 0.0
                        b_y = float(b.get("y")) if b.get("y") != null else 0.0
                        b_id = str(b.get("id")) if b.get("id") != null else "?"
                    elif typeof(b) == TYPE_DICTIONARY:
                        b_x = float(b.get("x", 0.0))
                        b_y = float(b.get("y", 0.0))
                        b_id = str(b.get("id", "?"))

                    world.add_event("spawn_hazard", {
                        "x": b_x + (randf() * 60.0 - 30.0),
                        "y": b_y + (randf() * 60.0 - 30.0),
                        "kind": hazard_kind
                    })
                    world.add_event("crowd_throw", {"message": "The crowd hates Ball " + b_id + " and throws a hazard!"})

func _process_global_modifier(balls: Array, current_tick: int):
    if global_modifier_timer > 0:
        global_modifier_timer -= 1
        if global_modifier_timer <= 0:
            active_global_modifier = null
            if world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "The global stat modifier has worn off!", "volume": 1.0})

            for b in balls:
                if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
                    if b.has_meta("crowd_global_speed"):
                        b.remove_meta("crowd_global_speed")
                        if "base_speed" in b:
                            b.speed = b.base_speed
                    if b.has_meta("crowd_global_damage"):
                        b.remove_meta("crowd_global_damage")
                        if "base_damage" in b:
                            b.damage = b.base_damage
                    if b.has_meta("crowd_global_shield"):
                        b.remove_meta("crowd_global_shield")
                elif typeof(b) == TYPE_DICTIONARY:
                    if b.has("crowd_global_speed") and b["crowd_global_speed"]:
                        b.erase("crowd_global_speed")
                        b["speed"] = b.get("base_speed", b.get("speed", 100.0))
                    if b.has("crowd_global_damage") and b["crowd_global_damage"]:
                        b.erase("crowd_global_damage")
                        b["damage"] = b.get("base_damage", b.get("damage", 10.0))
                    if b.has("crowd_global_shield") and b["crowd_global_shield"]:
                        b.erase("crowd_global_shield")
        else:
            for b in balls:
                var is_alive = false
                var is_spectator = false

                if typeof(b) == TYPE_OBJECT and b.has_method("get"):
                    is_alive = b.get("alive") if b.get("alive") != null else false
                    is_spectator = b.get("ball_type") == "spectator"
                elif typeof(b) == TYPE_DICTIONARY:
                    is_alive = b.get("alive", false)
                    is_spectator = b.get("ball_type") == "spectator"

                if not is_alive or is_spectator:
                    continue

                if active_global_modifier == "global_speed_up":
                    if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                        var base_s = b.get("base_speed") if b.get("base_speed") != null else (b.get("speed") if b.get("speed") != null else 100.0)
                        b.set("speed", base_s * 1.2)
                        b.set_meta("crowd_global_speed", true)
                    elif typeof(b) == TYPE_DICTIONARY:
                        var base_s = b.get("base_speed", b.get("speed", 100.0))
                        b["speed"] = base_s * 1.2
                        b["crowd_global_speed"] = true
                elif active_global_modifier == "global_damage_up":
                    if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                        var base_d = b.get("base_damage") if b.get("base_damage") != null else (b.get("damage") if b.get("damage") != null else 10.0)
                        b.set("damage", base_d * 1.2)
                        b.set_meta("crowd_global_damage", true)
                    elif typeof(b) == TYPE_DICTIONARY:
                        var base_d = b.get("base_damage", b.get("damage", 10.0))
                        b["damage"] = base_d * 1.2
                        b["crowd_global_damage"] = true
                elif active_global_modifier == "global_shield_up":
                    if typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                        var cur_s = b.get("shield") if b.get("shield") != null else 0.0
                        b.set("shield", min(50.0, cur_s + 0.1))
                        b.set_meta("crowd_global_shield", true)
                    elif typeof(b) == TYPE_DICTIONARY:
                        var cur_s = b.get("shield", 0.0)
                        b["shield"] = min(50.0, cur_s + 0.1)
                        b["crowd_global_shield"] = true
