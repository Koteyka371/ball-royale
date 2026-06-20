1. **Update Action mappings in `decision.py` and `decision.gd`**:
   - Use `run_in_bash_session` to run a Python script that injects `"hide_behind"` into `scores` dict and `action_order` array in `src/ai/decision.py`, and into `actions` array in `src/ai/neural_decision.py`.
   - Use `run_in_bash_session` with `sed` or python to inject `"hide_behind"` into `scores`, `action_order` in `src/ai/decision.gd`, and `actions` in `src/ai/neural_decision.gd`.
   - Verify the changes using `grep`.

2. **Add weights in `ai_weights.json`**:
   - Use `run_in_bash_session` to write and execute a Python script to load `src/ai/ai_weights.json`, add `"hide_behind"`: `{"hp_percent": -50.0, "danger_level": 80.0, "allies_count": 50.0, "bias": 0.0}`, and save.
   - Verify with `cat src/ai/ai_weights.json`.

3. **Add weights in `nn_weights.json`**:
   - Use `run_in_bash_session` to write and execute a Python script to load `src/ai/nn_weights.json`, update `output_size` to 10, append `[0.1, 0.2, 0.3, 0.4]` to `weights`, append `0.5` to `biases`, and save.
   - Verify with `cat src/ai/nn_weights.json`.

4. **Implement `_hide_behind` in `action.py` and `action.gd`**:
   - Use `run_in_bash_session` with a Python script to rewrite the `execute` method to include `elif strategy == "hide_behind": self._hide_behind(delta)`, and append the `_hide_behind` logic into `src/ai/action.py`.
   - Use `run_in_bash_session` with a Python script to rewrite the `execute` method in `src/ai/action.gd` and append the `_hide_behind` GDScript logic.

5. **Verify implementation**:
   - Use `run_in_bash_session` with `grep` and `cat` to verify that `_hide_behind` logic exists in `src/ai/action.py` and `src/ai/action.gd`.

6. **Write a test for the new behavior**:
   - Use `run_in_bash_session` with `cat << 'EOF'` to write `tests/test_hide_behind.py`.
   - Use `run_in_bash_session` to verify with `cat tests/test_hide_behind.py`.

7. **Run all tests**:
   - Run `pytest tests/` via `run_in_bash_session` to ensure nothing is broken and the new test passes.

8. **Complete pre-commit steps**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

9. **Submit changes**:
   - Use `run_in_bash_session` to create the branch `idea-arena-103`, stage with `git add`, commit with `git commit -m`, push with `git push`, create PR with `gh pr create` with `automated` label, and finally invoke `submit`.
