extends Control

var stats = {
    "alive": 0,
    "total_kills": 0,
    "top_killstreak": 0,
    "fps": 60,
    "tick": 0
}

var labels = {}
var vbox = null

func _ready():
    mouse_filter = Control.MOUSE_FILTER_IGNORE

    vbox = VBoxContainer.new()
    add_child(vbox)

    _add_stat_label("title", "=== STATS ===")
    _add_stat_label("tick", "Tick: 0")
    _add_stat_label("fps", "FPS: 60")
    _add_stat_label("alive", "Alive: 0")
    _add_stat_label("total_kills", "Total Kills: 0")
    _add_stat_label("top_killstreak", "Top Killstreak: 0")
    _add_stat_label("footer", "=============")

func _add_stat_label(key: String, initial_text: String):
    var label = Label.new()
    label.text = initial_text
    label.add_theme_font_size_override("font_size", 14)
    vbox.add_child(label)
    labels[key] = label

func update_stats(battle_stats: Dictionary, current_tick: int, fps: int = Engine.get_frames_per_second()):
    stats["tick"] = current_tick
    stats["fps"] = fps
    stats["total_kills"] = battle_stats.get("total_kills", 0)
    stats["top_killstreak"] = battle_stats.get("longest_killstreak", 0)

    if battle_stats.has("survivors"):
        stats["alive"] = battle_stats["survivors"]
    elif battle_stats.has("ball_types_alive"):
        var alive_counts = battle_stats["ball_types_alive"]
        if typeof(alive_counts) == TYPE_DICTIONARY:
            var total = 0
            for type in alive_counts.keys():
                total += alive_counts[type]
            stats["alive"] = total
        else:
            stats["alive"] = 0
    else:
        stats["alive"] = 0

    _refresh_ui()

func _refresh_ui():
    if labels.has("tick"): labels["tick"].text = "Tick: " + str(stats["tick"])
    if labels.has("fps"): labels["fps"].text = "FPS: " + str(stats["fps"])
    if labels.has("alive"): labels["alive"].text = "Alive: " + str(stats["alive"])
    if labels.has("total_kills"): labels["total_kills"].text = "Total Kills: " + str(stats["total_kills"])
    if labels.has("top_killstreak"): labels["top_killstreak"].text = "Top Killstreak: " + str(stats["top_killstreak"])

func toggle_visibility():
    visible = not visible
