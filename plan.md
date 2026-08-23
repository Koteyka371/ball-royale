1. **Update `item_kinds` in `src/arena/procedural_arena.py`**
   - Find the `item_kind = random.choice([...])` list in `src/arena/procedural_arena.py`.
   - Add `"sticky_bomb_booster"` and `"fire_sticky_bomb_booster"` to this list.

2. **Update `item_kinds` in `src/arena/procedural_arena.gd`**
   - Find the `var item_kinds = [...]` list in `src/arena/procedural_arena.gd`.
   - Add `"sticky_bomb_booster"` and `"fire_sticky_bomb_booster"` to this list.

3. **Complete pre commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

4. **Submit the change.**
   - Once all tests pass, I will submit the change with a descriptive commit message.
