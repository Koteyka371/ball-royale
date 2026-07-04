1. **Understand the Goal**:
   - Add a new equippable item or booster that temporarily grants immunity to EMP bursts and other scrambling effects.
   - The item should be named something like `emp_immunity_booster` or `faraday_cage_booster`. Let's use `emp_immunity_booster` for simplicity.
   - It will set a flag/timer on the ball that collects it, making it immune to effects that set `is_emped` or `is_scrambled` to true.

2. **Files to Modify**:
   - `src/ai/game_modes.py`: Add `emp_immunity_booster` to `booster_kinds`.
   - `src/ai/game_modes.gd`: Add `emp_immunity_booster` to `booster_kinds`.
   - `src/ai/action.py`:
     - In `_collect_booster`: Add logic for `emp_immunity_booster` to set `emp_immunity_timer`.
     - In `execute` or `_apply_hazards` / loop: Add countdown for `emp_immunity_timer` and reset `is_emp_immune` flag.
     - Modify places where `is_emped` or `is_scrambled` are set to `True` (like EMP burst, EMP trap, emp_item) to check `if not getattr(self.ball, "is_emp_immune", False):`. Wait, these effects might be applied to *other* balls (e.g. EMP trap hits a ball, or emp_item hits nearby balls). If `next_entity` hits a ball `b`, we check `if not getattr(b, "is_emp_immune", False):`.
   - `src/ai/action.gd`:
     - Same logic translated to GDScript for `emp_immunity_booster`.

3. **Detailed Logic Details**:
   - The booster adds `emp_immunity_timer = 15.0` (or some duration) and `is_emp_immune = True`.
   - Or maybe just check `getattr(b, "emp_immunity_timer", 0.0) > 0` everywhere, to avoid a boolean flag. Let's just use `emp_immunity_timer`.
   - When an EMP effect tries to hit a ball `b`, check `if getattr(b, "emp_immunity_timer", 0.0) <= 0:`.
   - The scrambling effects are applied in `action.py`:
     - EMP trap charge (`b.is_emped = True`, `b.is_scrambled = True`, etc.)
     - Trap variant "emp" (`self.ball.is_emped = True`)
     - Hazard `emp_burst` (`self.ball.is_scrambled = True`)
     - `emp_item` collecting (`other_ball.has_drone = False`, etc. - could block this too).
   - And the same in `action.gd`.

4. **Testing**:
   - Create `src/ai/test_emp_immunity_booster.py` to verify the ball becomes immune and timers work correctly.

5. **Generate Ideas**:
   - Create 2 valid JSON files in `ideas/`.

6. **Pre-commit and PR**:
   - Run tests, check for issues, format code.

