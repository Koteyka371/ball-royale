import pytest
import time
import os
import json
from unittest.mock import patch, MagicMock
from system.auction.guild_auction import GuildAuctionManager

@pytest.fixture
def temp_auction_file(tmp_path):
    f = tmp_path / "test_auction.json"
    yield str(f)
    if f.exists():
        os.remove(str(f))

@pytest.fixture
def mock_guild_manager():
    mock = MagicMock()
    mock.data = {
        "guilds": {
            "seller_guild": {"resources": 1000, "hq": {}},
            "buyer1": {"resources": 500, "hq": {}},
            "buyer2": {"resources": 600, "hq": {}}
        }
    }
    return mock

def test_auction_open_times(temp_auction_file):
    manager = GuildAuctionManager(temp_auction_file)

    # Mocking time for exactly 18:00
    t = time.struct_time((2023, 1, 1, 18, 0, 0, 6, 1, 0))
    t_sec = time.mktime(t)
    assert manager.is_auction_open(t_sec) == True

    # Mocking time for 21:59
    t = time.struct_time((2023, 1, 1, 21, 59, 59, 6, 1, 0))
    t_sec = time.mktime(t)
    assert manager.is_auction_open(t_sec) == True

    # Mocking time for exactly 22:00
    t = time.struct_time((2023, 1, 1, 22, 0, 0, 6, 1, 0))
    t_sec = time.mktime(t)
    assert manager.is_auction_open(t_sec) == False

def test_generate_rare_booster(temp_auction_file):
    manager = GuildAuctionManager(temp_auction_file)
    booster = manager.generate_rare_booster()

    assert "booster_type" in booster
    assert "stats" in booster
    assert "multiplier" in booster
    assert "description" in booster
    assert len(booster["stats"]) == 2

def test_listing_and_bidding(temp_auction_file, mock_guild_manager):
    auction_manager = GuildAuctionManager(temp_auction_file)

    # Set to open time
    t = time.struct_time((2023, 1, 1, 19, 0, 0, 6, 1, 0))
    t_sec = time.mktime(t)

    with patch('time.time', return_value=t_sec), patch('time.localtime', return_value=time.struct_time((2023, 1, 1, 19, 0, 0, 6, 1, 0))):
        listing_id = auction_manager.list_procedural_item("seller_guild", starting_bid=100)
        assert listing_id is not None

        # Bid from buyer1
        assert auction_manager.place_bid(listing_id, "buyer1", 200, mock_guild_manager) == True
        assert mock_guild_manager.data["guilds"]["buyer1"]["resources"] == 300

        # Outbid by buyer2
        assert auction_manager.place_bid(listing_id, "buyer2", 300, mock_guild_manager) == True
        assert mock_guild_manager.data["guilds"]["buyer2"]["resources"] == 300
        assert mock_guild_manager.data["guilds"]["buyer1"]["resources"] == 500 # Refunded

        # Bid lower amount - should fail
        assert auction_manager.place_bid(listing_id, "buyer1", 250, mock_guild_manager) == False

        # Not enough funds - should fail
        assert auction_manager.place_bid(listing_id, "buyer1", 1000, mock_guild_manager) == False

    # Resolve after time passed
    t_sec_later = t_sec + 7200
    with patch('time.time', return_value=t_sec_later), patch('time.localtime', return_value=time.struct_time((2023, 1, 1, 21, 0, 0, 6, 1, 0))):
        auction_manager.resolve_auctions(mock_guild_manager)

        assert len(auction_manager.get_active_listings()) == 0
        assert "auction_items" in mock_guild_manager.data["guilds"]["buyer2"]["hq"]
        assert len(mock_guild_manager.data["guilds"]["buyer2"]["hq"]["auction_items"]) == 1
