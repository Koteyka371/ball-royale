extends PanelContainer

var stats_label: Label
var vbox: VBoxContainer

func _ready():
    vbox = VBoxContainer.new()
    add_child(vbox)

    var title = Label.new()
    title.text = "=== BATTLE STATS ==="
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    vbox.add_child(title)

    stats_label = Label.new()
    stats_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    vbox.add_child(stats_label)

func update_stats(stats: Dictionary):
    var text = ""

    var duration = stats.get("battle_duration", 0.0)
    var ticks = stats.get("ticks", 0)
    text += "Time: %.2fs (Ticks: %d)\n" % [duration, ticks]

    var survivors = stats.get("survivors", 0)
    var kills = stats.get("total_kills", 0)
    text += "Survivors: %d  |  Kills: %d\n" % [survivors, kills]

    var winner = stats.get("winner")
    if winner != null:
        text += "Winner: %s\n" % str(winner).to_upper()
    else:
        text += "Winner: None\n"

    var killstreak = stats.get("longest_killstreak", 0)
    text += "Highest Killstreak: %d\n" % killstreak

    var avg_hp = stats.get("avg_hp_at_end", 0.0)
    if avg_hp > 0:
        text += "Avg End HP: %.1f\n" % avg_hp

    var alive_types = stats.get("ball_types_alive", {})
    if alive_types.size() > 0:
        var type_strings = []
        for key in alive_types.keys():
            type_strings.append("%s: %d" % [key, alive_types[key]])
        text += "Alive Types: %s\n" % ", ".join(type_strings)

    stats_label.text = text

func clear():
    stats_label.text = ""
