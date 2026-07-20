# Execution Plan

## 1. Add `invisibility_booster` to game modes booster generation
Update `booster_kinds` arrays in both `src/ai/game_modes.py` and `src/ai/game_modes.gd` to include `"invisibility_booster"` so it can spawn in matches.
- Also, update `excluded_hazards` in `src/ai/game_modes.py` to exclude `"invisibility_booster"` where stealth/ghost boosters are excluded (e.g. `TricksterMode`).
- Add `"invisibility_booster"` to `booster_types` in `MegaBoosterMode` in `src/ai/game_modes.py`.
- Add `"invisibility_booster"` to ignored items in `Action._use_skill` for items like magnet where stealth/ghost boosters are included.

## 2. Handle collection and ticking of `invisibility_booster`
- In `src/ai/action.py` and `src/ai/action.gd` generic hazard processing loop, add `invisibility_booster` to the list of safe hazards (bypassing damage).
- In `Action.execute` / `_kite` or `Action._collect_booster`, handle collection of `invisibility_booster`. Set `ball.invisibility_booster_timer = 10.0`.
- In the per-agent tick update in `src/ai/action.py` and `src/ai/action.gd` (`tick` or start of `execute`), decrement `invisibility_booster_timer` by `delta`.

## 3. Apply the invisibility effect in Perception
- In `src/ai/perception.py` and `src/ai/perception.gd`, check for `invisibility_booster_timer > 0` (using dictionary and object checks).
- If active, the enemy should be invisible to AI targeting.
- Modify the logic where `e_has_stealth_booster` or `e_has_ghost_mode_booster` is handled, creating an `e_has_invisibility_booster` variable and treating it similarly, so AI ignores players with this booster.
- Add checks for `invisibility_booster_timer` in `GameMode` logic like `TricksterMode` where stealth is forced to 0 or 9999, doing the same for invisibility.

## 4. Add Unit Tests for `invisibility_booster`
- Create `src/tests/test_invisibility_booster.py`.
- Mock necessary classes.
- Test that collecting the booster sets `invisibility_booster_timer`.
- Test that Perception correctly ignores enemies with `invisibility_booster_timer > 0`.
- Run tests and verify functionality.

## 5. Add 2 New Feature Ideas
- Create `src/ideas/idea_idea-1206_1.json` and `src/ideas/idea_idea-1206_2.json` with valid JSON containing "title" and "description".

## 6. Pre-commit instructions
- Call `pre_commit_instructions` tool to run checks.

## 7. Submit Pull Request
- Create branch, commit, push, and submit using PR.
