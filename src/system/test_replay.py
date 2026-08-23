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

def test_replay_rewind():
    replay = ReplaySystem()
    replay.start_recording()
    for i in range(5):
        replay.record_frame(i, [{"id": i}], [])
    replay.stop_recording()

    replay.start_playback(speed=-1.0)
    replay.set_frame(4)

    f1 = replay.get_next_frame()
    assert f1 is not None and f1["tick"] == 4

    f2 = replay.get_next_frame()
    assert f2 is not None and f2["tick"] == 3

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
    assert highlight.commentary
    assert highlight.commentary[0] == "A very tense moment where survival was the only option."

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

def test_generate_highlight_reel():
    replay = ReplaySystem()
    replay.start_recording()

    # Normal frames
    for i in range(1, 40):
        replay.record_frame(i, [{"id": 1, "hp": 100}], [])

    # Close call frame (hp <= 20)
    replay.record_frame(40, [{"id": 1, "hp": 15}], [])

    # Normal frames
    for i in range(41, 100):
        replay.record_frame(i, [{"id": 1, "hp": 50}], [])

    # Kill frame
    replay.record_frame(100, [{"id": 1, "hp": 50}], [{"type": "kill", "killer_id": 1}])

    # Normal frames
    for i in range(101, 150):
        replay.record_frame(i, [{"id": 1, "hp": 100}], [])

    replay.stop_recording()

    reel = replay.generate_highlight_reel(margin_before=5, margin_after=5)

    # 40 - 5 to 40 + 5 -> 35 to 45
    # 100 - 5 to 100 + 5 -> 95 to 105
    # Number of frames: 11 + 11 = 22
    assert len(reel.frames) == 22
    assert reel.frames[0]["tick"] == 35
    assert reel.frames[-1]["tick"] == 105
    assert "Welcome to the highlight reel!" in reel.commentary
