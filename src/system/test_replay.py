import sys

sys.path.insert(0, 'src')
from system.replay import ReplaySystem

def test_recording():
    replay = ReplaySystem()
    assert not replay.is_recording

    replay.start_recording()
    assert replay.is_recording

    replay.record_frame(1, [{"id": 1, "x": 10}], [{"type": "spawn"}])
    replay.record_frame(2, [{"id": 1, "x": 12}], [{"type": "move"}])

    assert len(replay.frames) == 2
    assert replay.frames[0]["tick"] == 1
    assert replay.frames[0]["entities"][0]["x"] == 10

    replay.stop_recording()
    assert not replay.is_recording

def test_playback():
    replay = ReplaySystem()
    replay.start_recording()
    replay.record_frame(1, [{"id": 1}], [])
    replay.record_frame(2, [{"id": 1}], [])
    replay.record_frame(3, [{"id": 1}], [])
    replay.stop_recording()

    replay.start_playback(speed=1.5)
    assert replay.is_playing
    assert replay.playback_speed == 1.5

    frame1 = replay.get_next_frame()
    assert frame1 is not None and frame1["tick"] == 1

    frame2 = replay.get_next_frame()
    assert frame2 is not None and frame2["tick"] == 2

    replay.set_frame(0)
    frame1_again = replay.get_next_frame()
    assert frame1_again is not None and frame1_again["tick"] == 1

    replay.stop_playback()
    assert not replay.is_playing
    assert replay.get_next_frame() is None

def test_extract_highlight():
    replay = ReplaySystem()
    replay.start_recording()
    for i in range(10):
        replay.record_frame(i, [{"id": i}], [])
    replay.stop_recording()

    highlight = replay.extract_highlight(3, 6)
    assert len(highlight.frames) == 4
    assert highlight.frames[0]["tick"] == 3
    assert highlight.frames[-1]["tick"] == 6

def test_serialization():
    replay = ReplaySystem()
    replay.start_recording()
    replay.record_frame(1, [{"id": 1, "hp": 100}], [{"event": "hit"}])
    replay.stop_recording()

    data = replay.to_dict()
    assert "frames" in data
    assert data["version"] == "1.0"

    new_replay = ReplaySystem()
    new_replay.from_dict(data)

    assert len(new_replay.frames) == 1
    assert new_replay.frames[0]["tick"] == 1
    assert new_replay.frames[0]["entities"][0]["hp"] == 100
