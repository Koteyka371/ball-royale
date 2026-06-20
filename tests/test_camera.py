from video.camera import CameraSystem

def test_camera_initialization():
    cam = CameraSystem(width=1000, height=800)
    assert cam.x == 500
    assert cam.y == 400
    assert cam.zoom == 1.0
    assert cam.target_id is None

def test_camera_follows_most_active():
    cam = CameraSystem(width=1000, height=800)
    balls = [
        {"id": 1, "x": 100, "y": 100, "hp": 100, "max_hp": 100},
        {"id": 2, "x": 200, "y": 200, "hp": 100, "max_hp": 100}
    ]

    events = []

    cam.update(balls, events)
    assert cam.target_id in [1, 2] # Usually picks first one when scores tie, but let's test dynamic change

    # Give ball 2 a kill
    events.append({"type": "kill", "killer_id": 2})

    cam.update(balls, events)
    assert cam.target_id == 2

    # Ensure smooth tracking started
    assert cam.x != 500 or cam.y != 400

def test_camera_zooms_on_action():
    cam = CameraSystem()
    balls = [{"id": 1, "x": 100, "y": 100, "hp": 100, "max_hp": 100}]
    events = [{"type": "kill", "killer_id": 1}]

    cam.update(balls, events)
    assert cam.zoom > 1.0 # Should zoom in due to kill score
