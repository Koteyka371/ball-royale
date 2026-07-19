def patch_python():
    with open('src/ai/game_modes.py', 'r') as f:
        content = f.read()

    # Search for MockBall attribute missing
    old_code = """world.add_event("visual_effect", {"type": "solar_flare_supercharge", "ball_id": b.id})"""
    new_code = """world.add_event("visual_effect", {"type": "solar_flare_supercharge", "ball_id": getattr(b, "id", 0)})"""
    content = content.replace(old_code, new_code)

    with open('src/ai/game_modes.py', 'w') as f:
        f.write(content)

patch_python()
print("Done patching game_modes.py")
