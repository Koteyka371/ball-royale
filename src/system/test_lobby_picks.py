import sys
import os
sys.path.insert(0, os.path.abspath('src'))

from system.lobby import PreGameLobby

def test_ban_and_pick():
    lobby = PreGameLobby()

    # Ban a type
    assert lobby.ban_ball_type("team1", "sniper")
    assert not lobby.ban_ball_type("team2", "sniper") # Already banned

    # Try picking a banned type
    assert not lobby.pick_ball_type("team1", "sniper")

    # Pick a valid type
    assert lobby.pick_ball_type("team1", "warrior")

    # Try picking an already picked type
    assert not lobby.pick_ball_type("team2", "warrior")

    # Pick another valid type
    assert lobby.pick_ball_type("team2", "healer")

    assert lobby.banned_ball_types == ["sniper"]
    assert lobby.team_picks == {"team1": ["warrior"], "team2": ["healer"]}

if __name__ == '__main__':
    test_ban_and_pick()
    print("All tests passed!")
