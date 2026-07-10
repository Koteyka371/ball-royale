class_name NemesisScreen
extends Control

var profile_manager: ProfileManager
var label: Label
var theme: String = "Genesis"

func _init(pm: ProfileManager = null, t: String = "Genesis"):
    profile_manager = pm
    theme = t

func _ready():
    label = Label.new()
    add_child(label)

    var close_btn = Button.new()
    close_btn.text = "Close"
    close_btn.pressed.connect(self._on_close_pressed)
    add_child(close_btn)

func _on_close_pressed():
    visible = false

func _get_flourish(t: String) -> String:
    match t:
        "Genesis": return "A calm, neutral genesis light illuminates the screen."
        "Inferno": return "Ember particles float across the screen, radiating heat."
        "Frost": return "A gentle snowfall and frost frames the edges of the UI."
        "Void": return "Dark purple energy swirls in the background."
        "Celestial": return "Golden stars twinkle in a bright, heavenly backdrop."
        "Abyssal": return "Deep-sea ambient particle effects bubble upward."
        "Ethereal": return "Ghostly green and blue wisps drift aimlessly."
        "Phantom": return "Shadowy silhouettes fade in and out of the periphery."
        "Eclipse": return "A ring of light is blocked by absolute darkness."
        "Radiance": return "Blinding rays of golden light shine from the center."
        _: return ""

func _refresh_ui() -> String:
    var result_text = ""

    var output = ["--- Nemeses ---"]
    var flourish = _get_flourish(theme)
    if flourish != "":
        output.append("[" + theme + " Theme] " + flourish)

    if profile_manager == null:
        output.append("No nemeses yet.")
        result_text = "\n".join(output)
    else:
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
