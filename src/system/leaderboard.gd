class_name LeaderboardManager
extends RefCounted

const SEASON_DURATION = 30 * 24 * 60 * 60 # 30 days in seconds
const SEASON_THEMES = ["Genesis", "Inferno", "Frost", "Void", "Celestial", "Abyssal", "Ethereal", "Phantom", "Eclipse", "Radiance"]

var filename = "user://leaderboard.json"
var profile_manager = null
var data = {}

func _init(pm = null, file_path: String = "user://leaderboard.json"):
    profile_manager = pm
    filename = file_path
    load_leaderboard()

func load_leaderboard():
    var file = FileAccess.open(filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            data = json.get_data()
            return

    # Default data
    data = {
        "season_start_time": Time.get_unix_time_from_system(),
        "current_season": 1,
        "players": {},
        "viewer_loyalty": {}
    }

func save_leaderboard():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func record_loadout_win(loadout_code: String, is_win: bool = true):
    if not data.has("loadouts"):
        data["loadouts"] = {}

    if not data["loadouts"].has(loadout_code):
        data["loadouts"][loadout_code] = {"uses": 0, "wins": 0}

    data["loadouts"][loadout_code]["uses"] += 1
    if is_win:
        data["loadouts"][loadout_code]["wins"] += 1

    save_leaderboard()

func get_top_loadouts(limit: int = 10) -> Array:
    if not data.has("loadouts"):
        return []

    var loadouts = data["loadouts"]
    var sorted_loadouts = []

    for code in loadouts.keys():
        var stats = loadouts[code]
        sorted_loadouts.append({
            "code": code,
            "uses": stats.get("uses", 0),
            "wins": stats.get("wins", 0)
        })

    sorted_loadouts.sort_custom(func(a, b):
        var uses_a = a["uses"]
        var wins_a = a["wins"]
        var win_rate_a = 0.0
        if uses_a > 0:
            win_rate_a = float(wins_a) / uses_a

        var uses_b = b["uses"]
        var wins_b = b["wins"]
        var win_rate_b = 0.0
        if uses_b > 0:
            win_rate_b = float(wins_b) / uses_b

        if uses_a != uses_b:
            return uses_a > uses_b
        return win_rate_a > win_rate_b
    )

    if sorted_loadouts.size() > limit:
        return sorted_loadouts.slice(0, limit)
    return sorted_loadouts

func update_prestige(player_id: String, prestige_level: int):
    if not data.has("players"):
        data["players"] = {}

    var current_prestige = 0
    if data["players"].has(player_id):
        current_prestige = data["players"][player_id]

    if current_prestige < prestige_level:
        data["players"][player_id] = prestige_level
        save_leaderboard()

func check_season():
    var current_time = Time.get_unix_time_from_system()
    var start_time = data.get("season_start_time", current_time)

    if current_time - start_time >= SEASON_DURATION:
        end_season()

func get_theme(season_num: int) -> String:
    var index = (season_num - 1) % SEASON_THEMES.size()
    return SEASON_THEMES[index]




func get_top_n_players(n: int = 10) -> Array:
    if not data.has("players"):
        return []

    var players = data["players"]
    var sorted_players = []
    for pid in players.keys():
        sorted_players.append({"id": pid, "prestige": players[pid]})

    sorted_players.sort_custom(func(a, b): return a["prestige"] > b["prestige"])

    var top_n = []
    for i in range(min(n, sorted_players.size())):
        top_n.append(sorted_players[i]["id"])

    return top_n

func record_match_replay(player_id: String, replay_system: Object):
    var top_10 = get_top_n_players(10)
    if top_10.has(player_id):
        store_top_player_replay(player_id, replay_system.to_dict())

func get_available_replays() -> Array:
    if not data.has("top_replays"):
        return []

    return data["top_replays"].keys()

func store_top_player_replay(player_id: String, replay_data: Dictionary):
    if not data.has("top_replays"):
        data["top_replays"] = {}

    var replay_filename = "user://replay_" + player_id + ".json"
    var file = FileAccess.open(replay_filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(replay_data, "  "))

    data["top_replays"][player_id] = replay_filename
    save_leaderboard()

func get_top_player_replay(player_id: String):
    if not data.has("top_replays") or not data["top_replays"].has(player_id):
        return null

    var replay_filename = data["top_replays"][player_id]
    var file = FileAccess.open(replay_filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            return json.get_data()
    return null

func generate_season_summary_video(top_players: Array, season_num: int):
    var video_data = {
        "title": "Season " + str(season_num) + " Highlight Reel",
        "season": season_num,
        "theme": get_theme(season_num),
        "top_players": top_players,
        "type": "video_mp4_mock",
        "duration": 120,
        "resolution": "1080p",
        "events": []
    }
    if top_players.size() > 0:
        video_data["events"].append({"timestamp": 10, "description": str(top_players[0]) + " gets a multi-kill!"})
    video_data["events"].append({"timestamp": 50, "description": "Epic final circle showdown."})

    var filename = "user://season_" + str(season_num) + "_summary.json"
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(video_data, "  "))

func end_season():
    var season_num = data.get("current_season", 1)
    var players = data.get("players", {})

    if players.size() > 0:
        var sorted_players = []
        for pid in players.keys():
            sorted_players.append({"id": pid, "prestige": players[pid]})

        sorted_players.sort_custom(func(a, b): return a["prestige"] > b["prestige"])

        var top_100 = []
        for i in range(min(100, sorted_players.size())):
            top_100.append(sorted_players[i]["id"])

        generate_season_summary_video(top_100, season_num)

        if top_100.has("local_player") and profile_manager != null:
            var theme = get_theme(season_num)
            if profile_manager.has_method("add_cosmetic"):
                profile_manager.call("add_cosmetic", "Crown of " + theme)
            if profile_manager.has_method("add_title"):
                profile_manager.call("add_title", theme + " Champion")
            if profile_manager.has_method("add_status_effect"):
                profile_manager.call("add_status_effect", "Aura of " + theme)

        var all_ranked = []
        for p in sorted_players:
            all_ranked.append(p["id"])

        if all_ranked.has("local_player") and profile_manager != null:
            var rank = all_ranked.find("local_player") + 1
            var theme = get_theme(season_num)
            var badge_name = "Season " + str(season_num) + " Rank " + str(rank) + " " + theme + " Badge"
            if profile_manager.has_method("add_badge"):
                profile_manager.call("add_badge", badge_name)

    data["season_start_time"] = Time.get_unix_time_from_system()
    data["current_season"] = season_num + 1
    data["players"] = {}
    save_leaderboard()

func record_viewer_loyalty(viewer_id: String, points: int):
    if not data.has("viewer_loyalty"):
        data["viewer_loyalty"] = {}

    var current_points = 0
    if data["viewer_loyalty"].has(viewer_id):
        current_points = data["viewer_loyalty"][viewer_id]

    data["viewer_loyalty"][viewer_id] = current_points + points
    save_leaderboard()

func get_top_viewers(limit: int = 5) -> Array:
    if not data.has("viewer_loyalty"):
        return []

    var viewers = data["viewer_loyalty"]
    var sorted_viewers = []

    for v_id in viewers.keys():
        sorted_viewers.append({
            "id": v_id,
            "points": viewers[v_id],
            "badge": get_viewer_badge(v_id)
        })

    sorted_viewers.sort_custom(func(a, b): return a["points"] > b["points"])

    if sorted_viewers.size() > limit:
        return sorted_viewers.slice(0, limit)
    return sorted_viewers

func get_viewer_badge(viewer_id: String) -> String:
    if not data.has("viewer_loyalty") or not data["viewer_loyalty"].has(viewer_id):
        return ""

    var points = data["viewer_loyalty"][viewer_id]
    if points >= 50:
        return "👑"
    elif points >= 20:
        return "⭐"
    return ""


func process_guild_boss_leaderboard(guild_manager: Object, week_id: String, tier_requirements: Dictionary):
    if not data.has("guild_boss_leaderboard"):
        data["guild_boss_leaderboard"] = {}

    var guild_scores = []

    if not guild_manager.data.has("guilds"):
        return

    for guild_name in guild_manager.data["guilds"].keys():
        var max_tier = 0
        var tiebreaker_damage = 0.0

        for tier_key in tier_requirements.keys():
            var tier_str = str(tier_key)
            var tier_int = int(tier_key)
            var required_damage = tier_requirements[tier_key]

            var damage = 0.0
            if guild_manager.has_method("_get_alliance_boss_damage"):
                damage = guild_manager.call("_get_alliance_boss_damage", guild_name, week_id, tier_str)

            if damage >= required_damage:
                if tier_int > max_tier:
                    max_tier = tier_int
                    tiebreaker_damage = damage

        if max_tier > 0:
            guild_scores.append({
                "guild_name": guild_name,
                "max_tier": max_tier,
                "damage": tiebreaker_damage
            })

    guild_scores.sort_custom(func(a, b):
        if a["max_tier"] != b["max_tier"]:
            return a["max_tier"] > b["max_tier"]
        return a["damage"] > b["damage"]
    )

    data["guild_boss_leaderboard"][week_id] = guild_scores

    var rewards = ["Boss Slayer Gold Aura", "Boss Slayer Silver Aura", "Boss Slayer Bronze Aura"]

    for i in range(min(3, guild_scores.size())):
        var g_name = guild_scores[i]["guild_name"]
        var guild = guild_manager.data["guilds"][g_name]
        if not guild.has("cosmetic_auras"):
            guild["cosmetic_auras"] = []

        var aura = rewards[i]
        if not guild["cosmetic_auras"].has(aura):
            guild["cosmetic_auras"].append(aura)

    save_leaderboard()
    if guild_manager.has_method("save_guilds"):
        guild_manager.call("save_guilds")
    elif guild_manager.has_method("save"):
        guild_manager.call("save")

func get_guild_boss_leaderboard(week_id: String) -> Array:
    if not data.has("guild_boss_leaderboard"):
        return []
    if not data["guild_boss_leaderboard"].has(week_id):
        return []
    return data["guild_boss_leaderboard"][week_id]
