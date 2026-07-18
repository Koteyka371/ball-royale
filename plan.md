# Plan

1. Implement `CaptureableWeatherStation` game mode class in `src/ai/game_modes.py` and `src/ai/game_modes.gd`. This game mode will spawn 4 weather stations in different sectors of the arena. Each team can capture a weather station. When a team captures a station, they control the weather in that sector, and that weather grants positive buffs to their team while penalizing the enemy team in the sector.

2. A station is captured by staying near it. It will have properties `owner_team`, `capture_progress` (from -100 to 100), and `sector_rect`.

3. Register the mode in both files `GAME_MODES["weather_station"] = CaptureableWeatherStation`.

4. Update `src/ai/action.py` and `src/ai/action.gd` to treat weather stations as strategic locations that agents should try to capture. We'll add logic so agents move toward neutral or enemy stations and stay near them to capture.

5. Add tests in `src/ai/test_weather_station.py` to verify the capture logic, weather effects, and agent targeting.

6. Add pre-commit step

7. Create 2 ideas in `ideas/`.
