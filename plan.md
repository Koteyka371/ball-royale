1. Use `run_in_bash_session` to run patch script to add `hologram_trap` to hazard lists in `src/arena/procedural_arena.py` and `src/arena/procedural_arena.gd`. Update generation ratios.
2. Verify Step 1 modifications using `run_in_bash_session` with `cat`.
3. Use `run_in_bash_session` to run patch script to add `hologram_trap` to the expected list in `src/arena/test_procedural_arena.py`.
4. Verify Step 3 modifications using `run_in_bash_session` with `cat`.
5. Use `run_in_bash_session` to run patch script to add interaction logic for `hologram_trap` in `src/ai/action.py`. Inside `_collect_booster` where a hazard is triggered when collected, when `hologram_trap` is collided with, trigger an explosion, deal damage, and set `is_confused = True` and `confusion_timer` to a value.
6. Verify Step 5 modifications using `run_in_bash_session` with `cat`.
7. Use `run_in_bash_session` to run patch script to add interaction logic for `hologram_trap` in `src/ai/action.gd`. Inside `_collect_booster` processing.
8. Verify Step 7 modifications using `run_in_bash_session` with `cat`.
9. Execute tests using `run_in_bash_session` with `PYTHONPATH=src python3 -m pytest src/`.
10. Generate 2 new feature idea JSON files in `ideas/` using `run_in_bash_session` to execute a script creating unique filenames and exact formatting.
11. Verify Step 10 modifications using `run_in_bash_session` with `cat ideas/*.json`.
12. Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
13. Execute git commands using `run_in_bash_session` to `git add .`, `git commit -m 'Add hologram_trap'`, `git push origin idea-451`, and `gh pr create --title '[idea-451] Add hologram trap' --body 'Task: idea-451' --label 'automated'`, then call `request_code_review`.
