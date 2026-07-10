class_name NemesisScreen
extends Control

var profile_manager: ProfileManager
var leaderboard_manager: LeaderboardManager
var label: Label
var bg_rect: ColorRect
var particles: CPUParticles2D

func _init(pm: ProfileManager = null, lm: LeaderboardManager = null):
    profile_manager = pm
    leaderboard_manager = lm

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

func _ready():
    var season_theme = "Genesis"
    if leaderboard_manager != null:
        var season = leaderboard_manager.data.get("current_season", 1)
        season_theme = leaderboard_manager.get_theme(season)

    bg_rect = ColorRect.new()
    bg_rect.color = _get_theme_color(season_theme)
    bg_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg_rect)

    particles = CPUParticles2D.new()
    add_child(particles)
    particles.position = Vector2(500, 300)
    particles.amount = 50
    particles.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
    particles.emission_rect_extents = Vector2(500, 300)

    match season_theme:
        "Inferno":
            particles.direction = Vector2(0, -1)
            particles.gravity = Vector2(0, -98)
            particles.color = Color(1, 0.5, 0)
        "Frost":
            particles.direction = Vector2(0, 1)
            particles.gravity = Vector2(0, 98)
            particles.color = Color(0.8, 0.9, 1.0)
        "Abyssal":
            particles.direction = Vector2(0, -1)
            particles.gravity = Vector2(0, -50)
            particles.color = Color(0, 0.5, 1.0)
            particles.spread = 180.0
        _:
            particles.direction = Vector2(0, 0)
            particles.gravity = Vector2(0, 0)
            particles.color = Color(1, 1, 1, 0.5)

    label = Label.new()
    add_child(label)

    var close_btn = Button.new()
    close_btn.text = "Close"
    close_btn.pressed.connect(self._on_close_pressed)
    add_child(close_btn)

func _on_close_pressed():
    visible = false

func _refresh_ui() -> String:
    var season_theme = "Genesis"
    if leaderboard_manager != null:
        var season = leaderboard_manager.data.get("current_season", 1)
        season_theme = leaderboard_manager.get_theme(season)

    var flourishes = {
        "Genesis": "* A soft, pale light gently pulses *",
        "Inferno": "* Embers drift lazily across the screen *",
        "Frost": "* Light snowflakes fall quietly *",
        "Void": "* Dark energy crackles silently *",
        "Celestial": "* Stars twinkle in the background *",
        "Abyssal": "* Deep-sea ambient particles swirling *",
        "Ethereal": "* Spectral wisps float around *",
        "Phantom": "* Ghostly shadows shift in the corners *",
        "Eclipse": "* The edge of the screen darkens mysteriously *",
        "Radiance": "* A warm, golden aura surrounds the UI *"
    }

    var result_text = ""

    if profile_manager == null:
        result_text = "--- Nemeses --- [" + season_theme + " Season]\n"
        var f = flourishes.get(season_theme, "")
        if f != "":
            result_text += f + "\n"
        result_text += "No nemeses yet."
    else:
        var output = ["--- Nemeses --- [" + season_theme + " Season]"]
        var flourish = flourishes.get(season_theme, "")
        if flourish != "":
            output.append(flourish)
        var nemeses = profile_manager.data.get("nemeses", {})

        var has_nemesis = false
        if typeof(nemeses) == TYPE_DICTIONARY:
            for killer_type in nemeses.keys():
                var victims = nemeses[killer_type]
                if typeof(victims) == TYPE_DICTIONARY:
                    for victim_type in victims.keys():
                        var count = victims[victim_type]
                        if count >= 2:
                            output.append(str(killer_type) + " vs " + str(victim_type) + ": " + str(count) + " kills")
                            has_nemesis = true

        if not has_nemesis:
            output.append("No nemeses yet.")

        result_text = "\n".join(output)

    if label != null:
        label.text = result_text

    return result_text
