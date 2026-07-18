1. **Add `decoy_swap_survival` skill to Python (`src/ai/action.py`)**
   - In `Action._use_skill`, handle `elif skill_name == "decoy_swap_survival":`
   - It should spawn a single decoy at the ball's position.
   - Set `decoy.survival_swap_timer = 3.0`. Or better, set it on the ball itself: `self.ball.survival_swap_target_id = decoy.id` and `self.ball.survival_swap_timer = 3.0`.
2. **Handle the timer and swap in `Action.execute()` for Python**
   - Early in `Action.execute()`, check `if getattr(self.ball, "survival_swap_timer", 0.0) > 0.0:`
   - Decrement the timer by delta.
   - If it hits `<= 0.0` after decrement, find the decoy in `self.world.balls` with `id == self.ball.survival_swap_target_id`. If it's alive and a decoy, swap their positions.
3. **Add identical logic to GDScript (`src/ai/action.gd`)**
   - In `_use_skill`, handle `elif skill_name == "decoy_swap_survival":`.
   - In `execute`, handle the timer and swap logic.
4. **Write tests (`src/ai/test_decoy_swap_survival.py`)**
   - Ensure the skill spawns a decoy and sets timer.
   - Ensure it swaps after 3 seconds.
5. **Create ideas in `ideas/` directory**
   - Create two idea JSON files.
6. **Pre commit step**
