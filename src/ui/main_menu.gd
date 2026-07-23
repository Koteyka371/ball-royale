class_name MainMenu
extends Control

var profile_manager: ProfileManager
var leaderboard_manager: LeaderboardManager
var prestige_shop_ui: PrestigeShop
var nemesis_screen_ui: NemesisScreen

var active_screen: String = "main"
var weekend_options: Array = ["10x_speed", "invisible_enemies", "lava_floor"]
var weekend_votes: Dictionary = {"10x_speed": 0, "invisible_enemies": 0, "lava_floor": 0}
var active_weekend_event: String = ""


var background_theme: String = ""
var background_color: Color = Color(0, 0, 0)
var bg_rect: ColorRect

func _ready():
    profile_manager = ProfileManager.new()
    leaderboard_manager = LeaderboardManager.new(profile_manager, "user://leaderboard.json")

    var season = leaderboard_manager.data.get("current_season", 1)
    background_theme = leaderboard_manager.get_theme(season)
    background_color = _get_theme_color(background_theme)

    bg_rect = ColorRect.new()
    bg_rect.color = background_color
    bg_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg_rect)
    move_child(bg_rect, 0)

    prestige_shop_ui = PrestigeShop.new(profile_manager)
    add_child(prestige_shop_ui)
    prestige_shop_ui.visible = false

    nemesis_screen_ui = NemesisScreen.new(profile_manager, background_theme)
    add_child(nemesis_screen_ui)
    nemesis_screen_ui.visible = false

    var open_shop_btn = Button.new()
    open_shop_btn.text = "Open Prestige Shop"
    open_shop_btn.pressed.connect(self._on_open_shop_pressed)
    add_child(open_shop_btn)


    var open_nemesis_btn = Button.new()
    open_nemesis_btn.text = "Open Nemesis Screen"
    open_nemesis_btn.pressed.connect(self._on_open_nemesis_pressed)
    add_child(open_nemesis_btn)

    var open_vote_btn = Button.new()
    open_vote_btn.text = "Weekend Event Vote"
    open_vote_btn.pressed.connect(self._on_open_vote_pressed)
    add_child(open_vote_btn)


func _get_theme_color(theme: String) -> Color:
    match theme:
        "Genesis":
            return Color(200.0/255.0, 200.0/255.0, 200.0/255.0)
        "Inferno":
            return Color(200.0/255.0, 50.0/255.0, 50.0/255.0)
        "Frost":
            return Color(50.0/255.0, 150.0/255.0, 200.0/255.0)
        "Void":
            return Color(50.0/255.0, 0.0, 100.0/255.0)
        "Celestial":
            return Color(255.0/255.0, 255.0/255.0, 200.0/255.0)
        "Abyssal":
            return Color(0.0, 0.0, 50.0/255.0)
        "Ethereal":
            return Color(150.0/255.0, 255.0/255.0, 200.0/255.0)
        "Phantom":
            return Color(100.0/255.0, 100.0/255.0, 150.0/255.0)
        "Eclipse":
            return Color(50.0/255.0, 50.0/255.0, 50.0/255.0)
        "Radiance":
            return Color(255.0/255.0, 200.0/255.0, 50.0/255.0)
        _:
            return Color(0, 0, 0)



func open_replay_screen() -> Array:
    active_screen = "replay_screen"
    if leaderboard_manager != null and leaderboard_manager.has_method("get_available_replays"):
        return leaderboard_manager.call("get_available_replays")
    return []

func process_replay_input(action: String, args: Array = []):
    if action == "watch" and args.size() > 0:
        var player_id = args[0]
        if leaderboard_manager != null and leaderboard_manager.has_method("get_top_player_replay"):
            var replay = leaderboard_manager.call("get_top_player_replay", player_id)
            if replay != null:
                return "watching " + player_id
        return "not found"
    elif action == "download" and args.size() > 0:
        var player_id = args[0]
        if leaderboard_manager != null and leaderboard_manager.has_method("get_top_player_replay"):
            var replay = leaderboard_manager.call("get_top_player_replay", player_id)
            if replay != null:
                return "downloaded " + player_id
        return "not found"
    elif action == "back":
        active_screen = "main"
        return true
    return false

func _on_open_nemesis_pressed():
    active_screen = "nemesis"
    prestige_shop_ui.visible = false
    nemesis_screen_ui.visible = true
    nemesis_screen_ui._refresh_ui()

func _on_open_vote_pressed():
    active_screen = "weekend_vote"
    prestige_shop_ui.visible = false
    if nemesis_screen_ui != null:
        nemesis_screen_ui.visible = false

func cast_weekend_vote(mode: String) -> bool:
    if weekend_options.has(mode):
        var tokens = profile_manager.data.get("prestige_tokens", 0)
        if tokens > 0:
            profile_manager.data["prestige_tokens"] = tokens - 1
            profile_manager.save()
            var current_votes = 0
            if weekend_votes.has(mode):
                current_votes = weekend_votes[mode]
            weekend_votes[mode] = current_votes + 1

            var max_v = -1
            var best = ""
            for m in weekend_votes.keys():
                if weekend_votes[m] > max_v:
                    max_v = weekend_votes[m]
                    best = m
            active_weekend_event = best
            return true
    return false


func _on_open_shop_pressed():
    active_screen = "prestige_shop"
    nemesis_screen_ui.visible = false
    prestige_shop_ui.visible = true
    prestige_shop_ui._refresh_ui()

func close_shop():
    active_screen = "main"
    prestige_shop_ui.visible = false
    if nemesis_screen_ui != null:
        nemesis_screen_ui.visible = false
