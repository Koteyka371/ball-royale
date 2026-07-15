1. **Update `src/ai/action.py`**:
   - Inside `_use_skill`, add logic for `elif skill_name == "swap_decoy_types":`.
   - Retrieve all active decoys owned by the player:
     `active_decoys = [b for b in getattr(self.world, "balls", []) if getattr(b, "is_decoy", False) and getattr(b, "owner_id", None) == self.ball.id and getattr(b, "alive", True)]`
   - Iterate over these active decoys, and change their `decoy_type` using deterministic shifting:
     `types = ["explosive", "stun_trap", "healing", "siren"]`
     `for d in active_decoys:`
         `if hasattr(d, "decoy_type") and d.decoy_type in types:`
             `d.decoy_type = types[(types.index(d.decoy_type) + 1) % len(types)]`
         `else:`
             `import random`
             `d.decoy_type = random.choice(types)`
   - Set the cooldown: `self.ball.skill_timer = getattr(self.ball, "SKILL_COOLDOWN", 10.0)`.

2. **Verify `src/ai/action.py` edits**:
   - Read `src/ai/action.py` using `cat` and `grep` to confirm the `swap_decoy_types` logic was inserted correctly.

3. **Update `src/ai/action.gd`**:
   - Inside `_use_skill`, add logic for `elif skill_name == "swap_decoy_types":`.
   - Similar to Python, iterate through decoys, check ownership, shift `decoy_type` to the next in the list, and update cooldown.

4. **Verify `src/ai/action.gd` edits**:
   - Read `src/ai/action.gd` using `cat` and `grep` to confirm the edits were written successfully.

5. **Test changes**:
   - Run the full test suite using `PYTHONPATH=.:src:src/ai pytest tests/ src/ai/` to ensure no regressions were introduced.

6. **Generate ideas**:
   - Create `ideas/idea_idea-1030_1.json` with content: `{"title": "Decoy Mimicry", "description": "Decoys slowly move towards the nearest enemy while maintaining their original form, acting as a distraction."}`
   - Create `ideas/idea_idea-1030_2.json` with content: `{"title": "Quantum Decoys", "description": "When a decoy is destroyed, it has a 50% chance to respawn at a random nearby location."}`

7. **Verify new files**:
   - Run `cat ideas/idea_idea-1030_1.json ideas/idea_idea-1030_2.json` to confirm the files were created properly.

8. **Complete pre-commit steps**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

9. **Submit changes**:
   - Add changes with `git add src/ai/action.py src/ai/action.gd src/ai/test_swap_decoy_types.py ideas/idea_idea-1030_1.json ideas/idea_idea-1030_2.json`
   - Commit with `git commit -m "[idea-1030] Add dynamic decoy swap skill"`
   - Push branch to origin with `git push origin idea-1030`
   - Create Pull Request with title `[idea-1030] Add dynamic decoy swap skill` and body `Task: idea-1030`
