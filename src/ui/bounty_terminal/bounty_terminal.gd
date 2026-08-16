class_name BountyTerminalUI
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

    _refresh_ui()

func _on_close_pressed():
    visible = false

func _refresh_ui() -> String:
    var output = ["--- Active High-Value Bounties ---"]
    var result_text = ""

    if profile_manager == null:
        output.append("No active bounties at this time.")
        result_text = "\n".join(output)
    else:
        var bounties = {}
        if profile_manager.has_method("get_player_bounties"):
            bounties = profile_manager.get_player_bounties()
        elif typeof(profile_manager.data) == TYPE_DICTIONARY and profile_manager.data.has("active_bounties"):
            bounties = profile_manager.data["active_bounties"]

        var has_bounty = false

        if typeof(bounties) == TYPE_DICTIONARY:
            var sorted_targets = bounties.keys()

            # Simple bubble sort by reward
            for i in range(sorted_targets.size()):
                for j in range(0, sorted_targets.size() - i - 1):
                    var r1 = 0
                    var r2 = 0
                    if typeof(bounties[sorted_targets[j]]) == TYPE_DICTIONARY:
                        r1 = bounties[sorted_targets[j]].get("reward", 0)
                    if typeof(bounties[sorted_targets[j+1]]) == TYPE_DICTIONARY:
                        r2 = bounties[sorted_targets[j+1]].get("reward", 0)

                    if r2 > r1:
                        var temp = sorted_targets[j]
                        sorted_targets[j] = sorted_targets[j+1]
                        sorted_targets[j+1] = temp

            for target in sorted_targets:
                var details = bounties[target]
                if typeof(details) == TYPE_DICTIONARY:
                    var reward = details.get("reward", 0)
                    if reward > 0:
                        var currency = details.get("currency", "tokens")
                        var placer = details.get("placer", "Unknown")
                        output.append("TARGET: " + str(target) + " | REWARD: " + str(reward) + " " + str(currency) + " | PLACED BY: " + str(placer))
                        has_bounty = true

        if not has_bounty:
            output.append("No active bounties at this time.")

        result_text = "\n".join(output)

    if label != null:
        label.text = result_text

    return result_text
