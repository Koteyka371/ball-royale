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

func update_prestige(player_id: String, prestige_level: int):
    if not data.has("players"):
        data["players"] = {}

    var current_prestige = 0
    if data["players"].has(player_id):
        current_prestige = data["players"][player_id]

    if current_prestige < prestige_level:
        data["players"][player_id] = prestige_level
        save_leaderboard()

func get_catchup_multiplier() -> float:
    var current_time = Time.get_unix_time_from_system()
    var start_time = data.get("season_start_time", current_time)
    var elapsed = current_time - start_time

    var catchup_start = SEASON_DURATION - (7 * 24 * 60 * 60)
    if elapsed >= catchup_start and elapsed < SEASON_DURATION:
        return 1.5
    return 1.0

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

    data["season_start_time"] = Time.get_unix_time_from_system()
    data["current_season"] = season_num + 1
    data["players"] = {}
    save_leaderboard()
