class_name MainMenu
extends Control

var profile_manager: ProfileManager
var prestige_shop_ui: PrestigeShop
var active_screen: String = "main"

func _ready():
    profile_manager = ProfileManager.new()
    prestige_shop_ui = PrestigeShop.new(profile_manager)
    add_child(prestige_shop_ui)
    prestige_shop_ui.visible = false

    var open_shop_btn = Button.new()
    open_shop_btn.text = "Open Prestige Shop"
    open_shop_btn.pressed.connect(self._on_open_shop_pressed)
    add_child(open_shop_btn)

func _on_open_shop_pressed():
    active_screen = "prestige_shop"
    prestige_shop_ui.visible = true
    prestige_shop_ui._refresh_ui()

func close_shop():
    active_screen = "main"
    prestige_shop_ui.visible = false
