extends PanelContainer

var max_top_killers: int = 3
var stats_label: Label

func _ready():
    var vbox = VBoxContainer.new()
    add_child(vbox)

    var title = Label.new()
    title.text = "BATTLE STATS"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    vbox.add_child(title)

    stats_label = Label.new()
    stats_label.autowrap_mode = TextServer.AUTOWRAP_WORD
    vbox.add_child(stats_label)

func update_stats(balls_data: Array):
    var alive_count = 0
    var total_kills = 0
    var valid_balls = []

    for b in balls_data:
        var hp = b.get("hp", 0)
        var kills = b.get("kills", 0)

        if hp > 0:
            alive_count += 1

        total_kills += kills

        if kills > 0:
            valid_balls.append(b)

    # Sort balls by kills descending, then by id ascending to match Python
    valid_balls.sort_custom(Callable(self, "_sort_by_kills"))

    var text = "Alive: %d\nTotal Kills: %d" % [alive_count, total_kills]

    var top_killers = []
    for i in range(min(max_top_killers, valid_balls.size())):
        var b = valid_balls[i]
        var b_type = str(b.get("type", "unknown")).to_upper()
        var b_id = str(b.get("id", "?"))
        var b_kills = b.get("kills", 0)
        top_killers.append(" - %s-%s: %d kills" % [b_type, b_id, b_kills])

    if top_killers.size() > 0:
        text += "\nTop Killers:\n" + "\n".join(top_killers)

    stats_label.text = text

func _sort_by_kills(a, b):
    var kills_a = a.get("kills", 0)
    var kills_b = b.get("kills", 0)
    if kills_a != kills_b:
        return kills_a > kills_b
    return a.get("id", 0) < b.get("id", 0)
