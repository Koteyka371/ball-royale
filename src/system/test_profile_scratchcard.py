import pytest
import os
import sys
sys.path.insert(0, os.path.abspath('src'))
from system.profile import ProfileManager

@pytest.fixture
def temp_profile_file(tmp_path):
    return str(tmp_path / "test_profile_scratchcard.json")

def test_scratchcard(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    assert pm.data.get("scratchcards", 0) == 0

    import datetime
    today_str = datetime.date.today().isoformat()
    rewards = pm.process_daily_login(today_str)
    assert rewards.get("scratchcards") == 1
    assert pm.data["scratchcards"] == 1

    res = pm.use_scratchcard()
    assert ("skill_points" in res or "prestige_tokens" in res)
    assert pm.data["scratchcards"] == 0

    res2 = pm.use_scratchcard()
    assert res2 == {}
