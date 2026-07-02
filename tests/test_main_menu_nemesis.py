import pytest
from ui.main_menu import MainMenu

def test_main_menu_nemesis_screen():
    menu = MainMenu()

    assert menu.active_screen == "main"

    output = menu.open_nemesis_screen()
    assert menu.active_screen == "nemesis"
    assert "--- Nemeses ---" in output

    assert menu.process_input("back") == True
    assert menu.active_screen == "main"

    menu.open_nemesis_screen()
    assert menu.process_input("unknown_action") == False
    assert menu.active_screen == "nemesis"
