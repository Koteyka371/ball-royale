class_name GuildEmblemEditor
extends Control

var profile_manager: ProfileManager
var guild_manager: GuildManager
var current_shape: String = "circle"
var current_color: String = "white"
var current_symbol: String = "none"

var available_shapes: Array = ["circle", "shield", "square", "diamond", "hexagon"]
var available_colors: Array = ["white", "red", "blue", "green", "gold", "black"]
var available_symbols: Array = ["none", "sword", "crown", "skull", "star", "fire"]

var shape_label: Label
var color_label: Label
var symbol_label: Label
var status_label: Label

func _init(pm: ProfileManager):
    profile_manager = pm
    guild_manager = GuildManager.new("user://guilds.json")

    var vbox = VBoxContainer.new()
    vbox.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
    add_child(vbox)

    var title = Label.new()
    title.text = "Guild Emblem Editor"
    vbox.add_child(title)

    shape_label = Label.new()
    vbox.add_child(shape_label)
    var shape_btn = Button.new()
    shape_btn.text = "Next Shape"
    shape_btn.pressed.connect(self._on_next_shape)
    vbox.add_child(shape_btn)

    color_label = Label.new()
    vbox.add_child(color_label)
    var color_btn = Button.new()
    color_btn.text = "Next Color"
    color_btn.pressed.connect(self._on_next_color)
    vbox.add_child(color_btn)

    symbol_label = Label.new()
    vbox.add_child(symbol_label)
    var symbol_btn = Button.new()
    symbol_btn.text = "Next Symbol"
    symbol_btn.pressed.connect(self._on_next_symbol)
    vbox.add_child(symbol_btn)

    var save_btn = Button.new()
    save_btn.text = "Save Emblem"
    save_btn.pressed.connect(self._on_save_pressed)
    vbox.add_child(save_btn)

    status_label = Label.new()
    vbox.add_child(status_label)

func _get_player_guild() -> String:
    var player_id = profile_manager.data.get("username", "player1")
    var guilds = guild_manager.data.get("guilds", {})
    for g_name in guilds.keys():
        var members = guilds[g_name].get("members", [])
        if player_id in members:
            return g_name
    return ""

func _refresh_ui():
    var guild_name = _get_player_guild()
    if guild_name != "":
        var guild = guild_manager.get_guild(guild_name)
        var emblem = guild.get("emblem", {"shape": "circle", "color": "white", "symbol": "none"})
        current_shape = emblem["shape"]
        current_color = emblem["color"]
        current_symbol = emblem["symbol"]
        _update_labels()
        status_label.text = ""
    else:
        status_label.text = "Not in a guild."

func _update_labels():
    shape_label.text = "Shape: " + current_shape
    color_label.text = "Color: " + current_color
    symbol_label.text = "Symbol: " + current_symbol

func _on_next_shape():
    var idx = available_shapes.find(current_shape)
    idx = (idx + 1) % available_shapes.size()
    current_shape = available_shapes[idx]
    _update_labels()

func _on_next_color():
    var idx = available_colors.find(current_color)
    idx = (idx + 1) % available_colors.size()
    current_color = available_colors[idx]
    _update_labels()

func _on_next_symbol():
    var idx = available_symbols.find(current_symbol)
    idx = (idx + 1) % available_symbols.size()
    current_symbol = available_symbols[idx]
    _update_labels()

func _on_save_pressed():
    var guild_name = _get_player_guild()
    if guild_name != "":
        var success = guild_manager.update_emblem(guild_name, current_shape, current_color, current_symbol)
        if success:
            status_label.text = "Saved successfully!"
        else:
            status_label.text = "Parts not unlocked."
    else:
        status_label.text = "Not in a guild."
