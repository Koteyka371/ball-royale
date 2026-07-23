import pytest
import os
import tempfile
from system.world_map import WorldMapManager

@pytest.fixture
def temp_map_file():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.remove(path)

def test_world_map_register_and_capture(temp_map_file):
    wm = WorldMapManager(temp_map_file)

    # Register a zone
    assert wm.register_zone("Volcano Core", "resource_generation", 50)
    assert not wm.register_zone("Volcano Core", "other", 10) # already exists

    # Capture zone
    assert wm.capture_zone("clan", "FireLords", "Volcano Core")

    owner_type, owner_name = wm.get_zone_owner("Volcano Core")
    assert owner_type == "clan"
    assert owner_name == "FireLords"

    # Check controlled zones
    zones = wm.get_controlled_zones("clan", "FireLords")
    assert "Volcano Core" in zones

    # Check passive buffs
    buffs = wm.get_passive_buffs("clan", "FireLords")
    assert buffs.get("resource_generation") == 50

def test_world_map_battle(temp_map_file):
    wm = WorldMapManager(temp_map_file)
    wm.register_zone("Ice Cavern", "defense_bonus", 20)

    # Unowned battle
    assert wm.battle_for_zone("guild", "IceKings", None, None, "Ice Cavern", 10, 0)
    owner_type, owner_name = wm.get_zone_owner("Ice Cavern")
    assert owner_name == "IceKings"

    # Owned battle - defender wins
    assert not wm.battle_for_zone("clan", "FireLords", "guild", "IceKings", "Ice Cavern", 50, 60)
    owner_type, owner_name = wm.get_zone_owner("Ice Cavern")
    assert owner_name == "IceKings"

    # Owned battle - attacker wins
    assert wm.battle_for_zone("clan", "FireLords", "guild", "IceKings", "Ice Cavern", 100, 60)
    owner_type, owner_name = wm.get_zone_owner("Ice Cavern")
    assert owner_name == "FireLords"

    # Invalid defender
    assert not wm.battle_for_zone("guild", "EarthShakers", "guild", "RandomGuild", "Ice Cavern", 100, 0)
