with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

# Register Conjurer in game_modes.gd
# Actually we don't need to import it in GDScript typically, it's loaded dynamically or preloaded,
# but let's check game_modes.gd for any hardcoded lists.
