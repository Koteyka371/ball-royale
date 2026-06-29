def replace_weather_in_action_py():
    with open("src/ai/action.py", "r") as f:
        content = f.read()

    # Look for the perception radius part and reduce it if raining.
    # Look for weather friction part and increase slippery in rain.

replace_weather_in_action_py()
