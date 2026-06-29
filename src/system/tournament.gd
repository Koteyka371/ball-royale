class_name TournamentManager
extends RefCounted

const TOURNAMENT_DURATION = 30 * 24 * 60 * 60 # 30 days in seconds

var filename = "user://tournament.json"
var profile_manager = null
var data = {}

func _init(pm = null, file_path: String = "user://tournament.json"):
    profile_manager = pm
    filename = file_path
    load_tournament()

func load_tournament():
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
        "tournament_start_time": Time.get_unix_time_from_system(),
        "current_tournament": 1,
        "player_scores": {}
    }

func save_tournament():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func record_score(player_id: String, score: int):
    if not data.has("player_scores"):
        data["player_scores"] = {}

    var current_score = 0
    if data["player_scores"].has(player_id):
        current_score = data["player_scores"][player_id]

    data["player_scores"][player_id] = current_score + score
    save_tournament()

func check_tournament_end():
    var current_time = Time.get_unix_time_from_system()
    var start_time = data.get("tournament_start_time", current_time)

    if current_time - start_time >= TOURNAMENT_DURATION:
        end_tournament()

func end_tournament():
    var tournament_num = data.get("current_tournament", 1)
    var player_scores = data.get("player_scores", {})

    if player_scores.size() > 0:
        var max_score = -1
        var top_players = []

        for pid in player_scores.keys():
            var p_score = player_scores[pid]
            if p_score > max_score:
                max_score = p_score
                top_players = [pid]
            elif p_score == max_score:
                top_players.append(pid)

        if top_players.has("local_player") and profile_manager != null:
            if profile_manager.has_method("add_cosmetic"):
                profile_manager.call("add_cosmetic", "Tournament " + str(tournament_num) + " Champion Skin")
            if profile_manager.has_method("add_status_effect"):
                profile_manager.call("add_status_effect", "Aura of Tournament " + str(tournament_num))

    data["tournament_start_time"] = Time.get_unix_time_from_system()
    data["current_tournament"] = tournament_num + 1
    data["player_scores"] = {}
    save_tournament()
