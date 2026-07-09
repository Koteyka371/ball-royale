1. **Understand the Goal**: The task is to create a hazard that when stepped on causes all friendly fire damage to be reflected back onto the attacker for 5 seconds.
2. **Implementation Details**:
   - We need to create a new booster or hazard type. The prompt says "A hazard that when stepped on...", so it's a hazard or booster. Let's call it `friendly_fire_reflect_trap` or similar. Wait, the prompt says "A hazard that when stepped on...". Let's create a new hazard type `friendly_fire_reflect_trap`. Or maybe a booster? Often hazards that buff/debuff are just boosters, or traps.
   - Let's look at how hazards apply effects. When a ball overlaps with a hazard, it triggers.
   - We need to add logic in `Action.execute()` or `GameMode.tick()` where a ball interacts with this hazard.
   - The effect: "causes all friendly fire damage to be reflected back onto the attacker for 5 seconds."
   - Friendly fire damage happens when an ally attacks another ally. Wait, in this game, can allies attack each other? Normally `_attempt_damage` handles enemy checking before attacking, but there might be splash damage or specific game modes.
   - We will add an effect `friendly_fire_reflect_timer` = 5.0.
   - We need to intercept damage calculation in `_deal_damage` or `_attempt_damage`. Let's look at where damage is dealt between allies.
   - Actually, in `Action._attempt_damage`, we can check if `attacker.team == target.team` (and they are not the same entity). If so, and `target.friendly_fire_reflect_timer > 0`, the damage is reflected to the attacker instead of hurting the target.
   - Let's modify `src/ai/action.py` `_attempt_damage` to add this reflection logic.
3. **Execution Steps**:
   - Add `friendly_fire_reflect_hazard` (or just check for `friendly_fire_reflect` hazard kind) processing in `action.py`.
   - Update `_attempt_damage` to check `attacker.team == target.team` and `target.friendly_fire_reflect_timer > 0`.
   - Add a test.
   - Generate two new ideas in the `ideas` directory.
   - Run pre-commit checks.
