1. **Add `orbital_mine` game mode to `src/ai/game_modes.py`**
    - Create an `OrbitalMinesMode` class inheriting from `GameMode`.
    - `name = "Orbital Mines"`, `id = "orbital_mines"`.
    - In the `tick(self, world, balls, delta=0.016)` method, safely check `hasattr(world, 'arena') and hasattr(world.arena, 'hazards')`.
    - Count if `orbital_mine` hazards exist. If fewer than 5, instantiate using `from arena.procedural_arena import Hazard` and set `active = True`, `angle` attribute, and append to `world.arena.hazards`.
    - Update the positions of all `orbital_mine` hazards so they revolve around the center of the arena (cx = world.width / 2, cy = world.height / 2). `angle += orbit_speed * delta`, calculating new `x = cx + math.cos(angle) * dist` and `y = cy + math.sin(angle) * dist`.
    - Register it in `GAME_MODES["orbital_mines"] = OrbitalMinesMode()`.
2. **Verify `src/ai/game_modes.py` edits**
    - Use `read_file` to confirm the edits.
3. **Add `orbital_mine` game mode to `src/ai/game_modes.gd`**
    - Create an `OrbitalMinesMode` class extending `GameMode`.
    - `func _init(): super(); name = "Orbital Mines"; id = "orbital_mines"`
    - In `func tick(world, balls: Array, delta: float = 0.016) -> void:`, safely validate `typeof(world) == TYPE_OBJECT and "arena" in world and "hazards" in world.arena`.
    - Set cx = world.width / 2.0 and cy = world.height / 2.0 (fallback to arena dimensions if missing).
    - Count existing `orbital_mine`s. If fewer than 5, use `var HazardObj = load("res://src/arena/procedural_arena.gd").Hazard` to instantiate new ones. Set `.active = true` and `.set_meta("angle", value)`. Append them to `world.arena.hazards`.
    - Loop over hazards. If `hazard.kind == "orbital_mine"`, update its angle (`var ang = hazard.get_meta("angle") + speed * delta; hazard.set_meta("angle", ang)`) and position (`x = cx + cos(ang) * dist`, `y = cy + sin(ang) * dist`).
    - Register it in the `GAME_MODES` dictionary: `"orbital_mines": OrbitalMinesMode.new()`.
4. **Verify `src/ai/game_modes.gd` edits**
    - Use `read_file` to confirm the edits.
5. **Handle `orbital_mine` behavior in `src/ai/action.py`**
    - In the hazard handling block (around line 6436), add `elif hazard.kind == "orbital_mine":`.
    - Distance check: `dist_sq < (hazard.radius + self.ball.radius) ** 2`.
    - If hit: Set `hazard.active = False`, deal `hazard.damage` to ball (e.g., 30.0 damage: `self.ball.hp -= hazard.damage`), and apply a slow debuff: `self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.5` and `self.ball.slow_timer = max(getattr(self.ball, 'slow_timer', 0.0), 2.0)`.
6. **Verify `src/ai/action.py` edits**
    - Use `read_file` to confirm the edits.
7. **Handle `orbital_mine` behavior in `src/ai/action.gd`**
    - Find the hazard handling loop block (around line 9274). Add `elif hazard.kind == "orbital_mine":`.
    - Distance check: `dist_sq < (hazard.radius + self.ball.radius) * (hazard.radius + self.ball.radius)`.
    - If hit: set `hazard.active = false`, deal `hazard.damage` to ball (e.g., `self.ball.hp -= hazard.damage`).
    - Apply slow: set `speed` to half, and timer: `self.ball.set("slow_timer", max(self.ball.get("slow_timer") if self.ball.get("slow_timer") != null else 0.0, 2.0))` (using `set_meta` if dict).
8. **Verify `src/ai/action.gd` edits**
    - Use `read_file` to confirm the edits.
9. **Edit `src/ai/test_game_modes.py` to append tests**
    - Append test `test_orbital_mines_mode()` at the end of the file verifying mode registers, spawns mines via `tick`, updates hazard positions in an orbit, and hazard properties (kind="orbital_mine"). Setup `MockWorld` and `MockArena` (with `self.name = 'mock_arena'`, `self.weather = 'clear'`) for the test.
10. **Verify `src/ai/test_game_modes.py` edits**
    - Use `read_file` to confirm the edits.
11. **Run tests**
    - Execute `PYTHONPATH=.:src:src/ai pytest tests/ src/ai/test_game_modes.py` to ensure it passes.
12. **Create Idea JSONs**
    - Create `ideas/idea_idea-1016_1.json` and `ideas/idea_idea-1016_2.json` with valid JSON format {"title": "...", "description": "..."}.
13. **Verify Idea JSONs**
    - Use `cat` to verify the JSON contents.
14. **Git staging**
    - `git add src/ai/game_modes.py src/ai/game_modes.gd src/ai/action.py src/ai/action.gd src/ai/test_game_modes.py ideas/idea_idea-1016_1.json ideas/idea_idea-1016_2.json`
15. **Git commit**
    - `git commit` with descriptive message.
16. **Push branch**
    - `git push origin idea-1016`
17. **Pre-commit steps**
    - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
18. **Create Pull Request**
    - Submit PR with title `[idea-1016] descriptive title` and body `Task: idea-1016`.
