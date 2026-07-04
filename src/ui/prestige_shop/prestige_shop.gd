class_name PrestigeShop
extends Control

var profile_manager = null

func _init(pm = null):
    if pm != null:
        profile_manager = pm
    else:
        profile_manager = ProfileManager.new()

func get_available_upgrades() -> Dictionary:
    return {
        "permanent_hp": {"cost": 5, "description": "Increases max HP permanently"},
        "permanent_speed": {"cost": 5, "description": "Increases base speed permanently"},
        "permanent_damage": {"cost": 5, "description": "Increases base damage permanently"},
        "mutator_unlocked": {"cost": 15, "description": "Unlocks custom match mutators (run mutators)"},
        "starting_artifact_shield": {"cost": 10, "description": "Start matches with a shield artifact"},
        "starting_artifact_dash": {"cost": 10, "description": "Start matches with a dash artifact"},
        "unlock_time_mage": {"cost": 25, "description": "Unlocks the Time-Mage ball archetype"},
        "shield_capacity_up": {"cost": 10, "description": "Increases reflect shield capacity by 20"},
        "shield_duration_up": {"cost": 10, "description": "Increases reflect shield duration by 1s"}
    }

func buy_upgrade(upgrade_name: String) -> bool:
    var upgrades = get_available_upgrades()
    if not upgrades.has(upgrade_name):
        return false
    var cost = upgrades[upgrade_name]["cost"]
    return profile_manager.buy_prestige_upgrade(upgrade_name, cost)

var container: VBoxContainer
var token_label: Label

func _ready():
    container = VBoxContainer.new()
    add_child(container)

    token_label = Label.new()
    container.add_child(token_label)

    _refresh_ui()

func _refresh_ui():
    # Clear existing buttons
    for child in container.get_children():
        if child is Button:
            container.remove_child(child)
            child.queue_free()

    var tokens = 0
    if profile_manager != null and "data" in profile_manager:
        tokens = profile_manager.data.get("prestige_tokens", 0)

    token_label.text = "Prestige Tokens: " + str(tokens)

    var upgrades = get_available_upgrades()
    for upgrade_name in upgrades.keys():
        var upgrade_data = upgrades[upgrade_name]
        var btn = Button.new()
        btn.text = upgrade_data["description"] + " (" + str(upgrade_data["cost"]) + " Tokens)"
        btn.pressed.connect(self._on_buy_pressed.bind(upgrade_name))
        container.add_child(btn)

func _on_buy_pressed(upgrade_name: String):
    var success = buy_upgrade(upgrade_name)
    if success:
        print("Successfully bought " + upgrade_name)
        _refresh_ui()
    else:
        print("Not enough tokens to buy " + upgrade_name)
