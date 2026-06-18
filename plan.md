1. Use `run_in_bash_session` to execute `git checkout -b visualizer-skills-effects` to create the requested branch.
2. Use `replace_with_git_merge_diff` to modify `visualizer/index.html`. Replace the generic `use_skill` block with logic that extracts the skill from `replayData.ball_types?.[ball.type]?.skill` and renders specific canvas effects. This includes:
   - `shield`: drawing a glowing cyan circle.
   - `wave_attack`: drawing expanding red shockwaves using `currentFrameIndex` for animation.
   - `dash`: rendering ghost trails by accessing `replayData.history` at previous indices.
   - Fallback to the default dashed circle for other skills.
3. Use `read_file` to inspect `visualizer/index.html` and verify the new canvas drawing logic was written correctly.
4. Use `run_in_bash_session` to execute `PYTHONPATH=src DISABLE_NN_OVERRIDE=1 pytest tests/ -v`, `PYTHONPATH=src python scripts/quality_metrics.py`, and `PYTHONPATH=src python scripts/validate_tasks.py agent_tasks.json` to validate the test suite and quality.
5. Complete pre commit steps to ensure proper testing, verification, review, and reflection are done.
6. Submit the changes on the 'visualizer-skills-effects' branch.
