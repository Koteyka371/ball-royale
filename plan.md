## Plan
1. **Add `disruption_bomb` to skills list**:
   - In `src/ai/action.py` and `src/ai/action.gd`, add `disruption_bomb` to the `skills` arrays where random skills are generated.
2. **Implement `disruption_bomb` skill in `_use_skill`**:
   - In `src/ai/action.py` (`elif skill_name == "disruption_bomb":`) and `src/ai/action.gd`, duplicate the core hazard-spawning logic from `throw_bomb` to spawn a new hazard named `disruption_bomb`. It will have a 2.0s duration and travel towards the nearest enemy.
3. **Implement `disruption_bomb` detonation in `_resolve_hazards`**:
   - In `src/ai/action.py` and `src/ai/action.gd`, add a check for `disruption_bomb`. If its duration reaches 0, detonate it.
   - When detonated, apply `aura_disruption_timer = 10.0` to all enemies within a blast radius (e.g. 200.0). Also, spawn an explosion effect for visual feedback.
4. **Complete pre commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5. **Submit changes**
   - Create 2 IDEAS INBOX files `ideas/idea_idea-818_1.json` and `ideas/idea_idea-818_2.json`.
   - Submit the PR.
