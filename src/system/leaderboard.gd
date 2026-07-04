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
        "players": {}
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
