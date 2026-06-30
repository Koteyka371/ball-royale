1.  **Add `deploy_fake_booster` skill to `src/ai/action.py`**
    *   Use `replace_with_git_merge_diff` to add an `elif skill_name == "deploy_fake_booster":` block in `_use_skill` (around line 2900). Create a mock hazard object with `kind="fake_booster"`, coordinates matching `self.ball`, `damage=50.0`, `duration=30.0`, and `owner_id=self.ball.id`. Append to `self.world.arena.hazards`. Apply skill cooldown.

2.  **Verify `src/ai/action.py` edit**
    *   Use `run_in_bash_session` with `git diff src/ai/action.py` to verify the logic was added correctly.

3.  **Add `deploy_fake_booster` skill to `src/ai/action.gd`**
    *   Use `replace_with_git_merge_diff` to add an `elif skill_name == "deploy_fake_booster":` block in `_use_skill` (around line 4560). Create a dictionary hazard with `kind="fake_booster"`, append it to `world.arena.hazards`, and apply skill cooldown.

4.  **Verify `src/ai/action.gd` edit**
    *   Use `run_in_bash_session` with `git diff src/ai/action.gd` to verify the logic was added correctly.

5.  **Update `Fake Booster` stun effect in `src/ai/action.py`**
    *   Use `replace_with_git_merge_diff` to modify lines around 2710 in `src/ai/action.py` to add `self.ball.stun_timer = max(getattr(self.ball, "stun_timer", 0.0), 2.0)` inside the `fake_booster` collection logic.

6.  **Verify `src/ai/action.py` stun effect edit**
    *   Use `run_in_bash_session` with `git diff src/ai/action.py` to verify the stun logic was added.

7.  **Update `Fake Booster` stun effect in `src/ai/action.gd`**
    *   Use `replace_with_git_merge_diff` to modify lines around 4205 in `src/ai/action.gd` to add stun logic: `if "stun_timer" in self.ball: self.ball.stun_timer = max(self.ball.stun_timer, 2.0) else: self.ball.set_meta("stun_timer", 2.0)`.

8.  **Verify `src/ai/action.gd` stun effect edit**
    *   Use `run_in_bash_session` with `git diff src/ai/action.gd` to verify the stun logic was added.

9.  **Assign the skill to `Rogue`**
    *   Use `replace_with_git_merge_diff` on `src/ai/ball_types_rogue.py` to change `SKILL = "smokescreen"` to `SKILL = "deploy_fake_booster"`.

10. **Verify `Rogue` assignment**
    *   Use `run_in_bash_session` with `git diff src/ai/ball_types_rogue.py`.

11. **Create tests for `deploy_fake_booster`**
    *   Use `run_in_bash_session` with `cat << 'EOF' > src/ai/test_deploy_fake_booster.py` to provide the test logic.

12. **Generate Ideas**
    *   Use `run_in_bash_session` to create two idea JSON files using `echo '{"title": "Idea 1", "description": "..."}' > ideas/idea_idea-323_1.json`.

13. **Run Test Suite**
    *   Use `run_in_bash_session` with `PYTHONPATH=src pytest src/` to ensure all tests pass.

14. **Pre-commit steps**
    *   Complete pre commit steps to ensure proper testing, verification, review, and reflection are done using `pre_commit_instructions`.

15. **Commit and Push**
    *   Use `run_in_bash_session` to execute:
        `git add .`
        `git commit -m "Add deploy_fake_booster skill and stun to fake booster collection"`
        `git push -u origin HEAD`
        `gh pr create --title "[idea-323] Add deploy_fake_booster skill and psychological trapping" --body "Task: idea-323" --label "automated"`
