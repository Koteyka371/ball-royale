import pytest
from unittest.mock import MagicMock
from game_modes import ItemMorphMode

def test_item_morph_mode():
    mode = ItemMorphMode()
    world = MagicMock()

    class FakeBooster:
        def __init__(self, kind):
            self.kind = kind
            self.active = True

    b1 = FakeBooster("speed_booster")
    b2 = FakeBooster("hp_booster")
    world.boosters = [b1, b2]

    mode.tick(world, [], 10.0)

    # Check that they have a kind attribute, and we don't crash
    assert hasattr(b1, "kind")
    assert hasattr(b2, "kind")

    # We can also check if add_event was called because they were morphed
    world.add_event.assert_called_with("items_morphed", {"message": "All items have morphed!"})

def test_item_morph_mode_no_boosters():
    mode = ItemMorphMode()
    world = MagicMock()
    world.boosters = []

    mode.tick(world, [], 10.0)
    world.add_event.assert_not_called()
