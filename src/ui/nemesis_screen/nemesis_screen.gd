class_name NemesisScreen
extends Control

var profile_manager: ProfileManager
var label: Label

func _init(pm: ProfileManager = null):
    profile_manager = pm

func _ready():
    label = Label.new()
    add_child(label)

    var close_btn = Button.new()
    close_btn.text = "Close"
    close_btn.pressed.connect(self._on_close_pressed)
    add_child(close_btn)

func _on_close_pressed():
    visible = false

func _refresh_ui() -> String:
    var result_text = ""

    if profile_manager == null:
        result_text = "--- Nemeses ---\nNo nemeses yet."
    else:
        var output = ["--- Nemeses ---"]
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
