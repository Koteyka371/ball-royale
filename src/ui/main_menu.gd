class_name MainMenu
extends Control

var profile_manager: ProfileManager
var prestige_shop_ui: PrestigeShop
var nemesis_screen_ui: NemesisScreen
var active_screen: String = "main"

func _ready():
    profile_manager = ProfileManager.new()
    prestige_shop_ui = PrestigeShop.new(profile_manager)
    add_child(prestige_shop_ui)
    prestige_shop_ui.visible = false

    nemesis_screen_ui = NemesisScreen.new(profile_manager)
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

func _on_open_nemesis_pressed():
    active_screen = "nemesis"
    prestige_shop_ui.visible = false
    nemesis_screen_ui.visible = true
    nemesis_screen_ui._refresh_ui()

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
