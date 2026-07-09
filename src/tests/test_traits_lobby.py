import pytest
from system.lobby import PreGameLobby

def test_select_traits():
    lobby = PreGameLobby()
    lobby.select_traits(1, ["swift", "slow", "invalid_trait", "fragile"])
    traits = lobby.get_traits(1)
    assert "swift" in traits
    assert "slow" in traits
    assert "fragile" in traits
    assert "invalid_trait" not in traits

class MockProfile:
    def get_loadout(self, name):
        if name == "trait_loadout":
            return {"trap_variant": "normal", "traits": ["sturdy", "lethal"]}
        return None

def test_apply_loadout_traits():
    pm = MockProfile()
    lobby = PreGameLobby()
    lobby.apply_loadout_to_ball(2, pm, "trait_loadout")

    traits = lobby.get_traits(2)
    assert "sturdy" in traits
    assert "lethal" in traits
