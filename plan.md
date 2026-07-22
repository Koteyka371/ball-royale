1. **Create Skeletal Archer Subtype:**
   - Create `src/ai/ball_types_skeletal_archer.py` with `BALL_TYPE = "skeletal_archer"`, `HP = 15.0`, `SPEED = 3.0`, `DAMAGE = 0.0`. Set `is_minion = True`.
   - Create `src/ai/ball_types_skeletal_archer.gd` similarly.
   - Wait, GDScript classes need to be loadable.
2. **Update Necromancer's Summoning Logic:**
   - In `src/ai/action.py` and `src/ai/action.gd`, under `summon_minions` skill logic, check if the summoner's `ball_type` is `"necromancer"`. If so, randomly choose between `minion` and `skeletal_archer` (e.g. 50/50 chance), or maybe 100% `skeletal_archer`. I'll do a 50/50 mix or choose randomly. "Add a new subtype of minion for the Necromancer: Skeletal Archers." It implies Necromancers can have them.
3. **AI Logic for Skeletal Archer:**
   - Modify `src/ai/action.py` inside `execute()` where AI runs, add logic for `if getattr(self.ball, "ball_type", "") == "skeletal_archer":`.
     - Find enemies. Use `_update_skill_timer(delta)`.
     - Move towards the enemy if `distance > 200`. Move away if `distance < 150`.
     - If `attack_timer <= 0`, fire a `homing_missile` (instantiate `HomingMissileHazard` in python, `HazardType` in GDScript with kind `"homing_missile"`) directed at the nearest enemy.
   - Do the same in `src/ai/action.gd`.
4. **Pre-commit Instructions:**
   - Always run tests and frontend verification.
