import pytest
from system.lobby import PreGameLobby

def test_spectator_queue():
    lobby = PreGameLobby()
    lobby.join_spectator_queue("player1", "match1")
    lobby.join_spectator_queue("player2")
    lobby.join_spectator_queue("player3", "match2")

    match1_spectators = lobby.get_spectators_for_match("match1")
    assert "player1" in match1_spectators
    assert "player2" in match1_spectators
    assert "player3" not in match1_spectators

    match2_spectators = lobby.get_spectators_for_match("match2")
    assert "player3" in match2_spectators
    assert "player2" in match2_spectators
    assert "player1" not in match2_spectators

if __name__ == "__main__":
    pytest.main(["-v", __file__])
