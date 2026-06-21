1. *Modify `src/arena/arena_types.py`*
   - Add `NeuralBallArena` class extending `ProceduralArena`.
   - Implement the `generate` method:
     - `w, h = self.width, self.height`, `cx, cy = w/2, h/2`.
     - Center room: `Room(cx - 500, cy - 500, 1000, 1000)`
     - Top room: `Room(cx - 100, 50, 200, cy - 500 - 50)`
     - Bottom room: `Room(cx - 100, cy + 500, 200, h - 50 - (cy + 500))`
     - Left room: `Room(50, cy - 100, cx - 500 - 50, 200)`
     - Right room: `Room(cx + 500, cy - 100, w - 50 - (cx + 500), 200)`
     - Top corridor: `Corridor(cx - 50, cy - 550, 100, 100)`
     - Bottom corridor: `Corridor(cx - 50, cy + 450, 100, 100)`
     - Left corridor: `Corridor(cx - 550, cy - 50, 100, 100)`
     - Right corridor: `Corridor(cx + 450, cy - 50, 100, 100)`
     - Hazard 1: `Hazard(id=1, x=cx - 250, y=cy - 250, radius=50, kind="lava", damage=10.0)`
     - Hazard 2: `Hazard(id=2, x=cx + 250, y=cy - 250, radius=50, kind="lava", damage=10.0)`
     - Hazard 3: `Hazard(id=3, x=cx - 250, y=cy + 250, radius=50, kind="lava", damage=10.0)`
     - Hazard 4: `Hazard(id=4, x=cx + 250, y=cy + 250, radius=50, kind="lava", damage=10.0)`
   - Register `"neural_ball": NeuralBallArena` in the `ARENAS` dictionary.

2. *Verify Python modifications*
   - Use the `read_file` tool to verify the modifications to `src/arena/arena_types.py`.

3. *Modify `src/arena/procedural_arena.gd`*
   - Add `NeuralBallArena` GDScript class extending `ProceduralArena`.
   - Implement the `generate` method:
     - `var w = width`, `var h = height`, `var cx = w / 2.0`, `var cy = h / 2.0`
     - Center room: `ProceduralArena.Room.new(cx - 500, cy - 500, 1000, 1000)`
     - Top room: `ProceduralArena.Room.new(cx - 100, 50, 200, cy - 500 - 50)`
     - Bottom room: `ProceduralArena.Room.new(cx - 100, cy + 500, 200, h - 50 - (cy + 500))`
     - Left room: `ProceduralArena.Room.new(50, cy - 100, cx - 500 - 50, 200)`
     - Right room: `ProceduralArena.Room.new(cx + 500, cy - 100, w - 50 - (cx + 500), 200)`
     - Top corridor: `ProceduralArena.Corridor.new(cx - 50, cy - 550, 100, 100)`
     - Bottom corridor: `ProceduralArena.Corridor.new(cx - 50, cy + 450, 100, 100)`
     - Left corridor: `ProceduralArena.Corridor.new(cx - 550, cy - 50, 100, 100)`
     - Right corridor: `ProceduralArena.Corridor.new(cx + 450, cy - 50, 100, 100)`
     - Hazard 1: `ProceduralArena.Hazard.new(1, cx - 250, cy - 250, 50, "lava", 10.0)`
     - Hazard 2: `ProceduralArena.Hazard.new(2, cx + 250, cy - 250, 50, "lava", 10.0)`
     - Hazard 3: `ProceduralArena.Hazard.new(3, cx - 250, cy + 250, 50, "lava", 10.0)`
     - Hazard 4: `ProceduralArena.Hazard.new(4, cx + 250, cy + 250, 50, "lava", 10.0)`

4. *Verify GDScript modifications*
   - Use the `read_file` tool to verify the changes to `src/arena/procedural_arena.gd`.

5. *Modify `src/arena/arena_types.gd`*
   - Add `"neural_ball"` to the `ARENAS` constant string array.

6. *Verify arena types GDScript modifications*
   - Use the `read_file` tool to verify the changes to `src/arena/arena_types.gd`.

7. *Create `tests/test_arena_neural_ball.py`*
   - Write a test using `pytest` for the `NeuralBallArena`.
   - Ensure the module imports properly by prepending `src` path to `sys.path`.
   - Use the assertion: `assert len(arena.rooms) == 5`.
   - Use the assertion: `assert len(arena.corridors) == 4`.
   - Use the assertion: `assert len(arena.hazards) == 4`.

8. *Verify tests modifications*
   - Use the `read_file` tool to verify the creation and contents of the test file.

9. *Create Idea JSON*
    - Run the command `mkdir -p ideas` using bash.
    - Write the content `{"title": "Neural Evolution Dashboard", "description": "Add a visual dashboard that shows the neural network's weights and learning progress over generations."}` into the file `ideas/neural_evolution_dashboard.json`.

10. *Verify Idea JSON*
    - Use the `read_file` tool to verify the contents of the generated JSON file `ideas/neural_evolution_dashboard.json`.

11. *Run Tests*
   - Run `PYTHONPATH=src /home/jules/.local/share/pipx/venvs/pytest/bin/python -m pytest tests/test_arena_neural_ball.py`.
   - Run `PYTHONPATH=src /home/jules/.local/share/pipx/venvs/pytest/bin/python scripts/auto_test.py`.

12. *Complete pre-commit steps*
Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

13. *Submit Pull Request*
    - Call submit tool with branch `idea-arena-119`, title `[idea-arena-119] Implement Neural Ball arena`, body `Task: idea-arena-119`.
