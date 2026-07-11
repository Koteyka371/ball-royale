1. **Add `thorn` trap to trap_variants:**
   - In `src/system/lobby.py`, add `"thorn"` to the `trap_variants` list.
   - In `src/system/lobby.gd`, add `"thorn"` to the `trap_variants` array.

2. **Handle `thorn` trap in `action.py` (Python AI):**
   - In `action.py`, inside the `execute` method where traps are checked (`elif trap_variant == "warp":` etc., around line 5000), add a condition:
     ```python
     elif trap_variant == "thorn":
         self.ball.thorn_aura_timer = 5.0
         if hasattr(hazard, "duration"):
             hazard.duration = 0.0
     ```
   - In `action.py`, inside `_attempt_damage`, add logic for friendly fire reflection:
     ```python
     # At the beginning of `_attempt_damage`
     a_team = getattr(attacker, "team", getattr(attacker, "ball_type", ""))
     t_team = getattr(target, "team", getattr(target, "ball_type", ""))
     if a_team == t_team and getattr(target, "thorn_aura_timer", 0.0) > 0:
         # Friendly fire reflection
         original_damage = getattr(attacker, "damage", 10.0)
         if hasattr(self.world, "_deal_damage"):
             old_dmg = getattr(target, "damage", original_damage)
             target.damage = original_damage
             self.world._deal_damage(target, attacker)
             target.damage = old_dmg
         return
     ```
   - Also, need to decay `thorn_aura_timer` in `action.py`. Inside the `execute` loop where timers decay:
     ```python
     if getattr(self.ball, "thorn_aura_timer", 0.0) > 0:
         self.ball.thorn_aura_timer -= delta
     ```

3. **Handle `thorn` trap in `action.gd` (GDScript AI):**
   - Similar to Python, where trap variants are checked (`elif trap_variant == "warp":` etc.), add:
     ```gdscript
     elif trap_variant == "thorn":
         self.ball.set_meta("thorn_aura_timer", 5.0)
         if "duration" in hazard: hazard.duration = 0.0
         elif hazard.has_method("set_meta"): hazard.set_meta("duration", 0.0)
         elif typeof(hazard) == TYPE_OBJECT and hazard.has_method("set"): hazard.set("duration", 0.0)
     ```
   - In `action.gd`, inside `_attempt_damage`:
     ```gdscript
     var a_team = ""
     if typeof(attacker) == TYPE_OBJECT and "team" in attacker: a_team = attacker.team
     elif typeof(attacker) == TYPE_OBJECT and attacker.has_method("has_meta") and attacker.has_meta("team"): a_team = attacker.get_meta("team")

     var t_team = ""
     if typeof(target) == TYPE_OBJECT and "team" in target: t_team = target.team
     elif typeof(target) == TYPE_OBJECT and target.has_method("has_meta") and target.has_meta("team"): t_team = target.get_meta("team")

     var t_thorn = 0.0
     if typeof(target) == TYPE_OBJECT and "thorn_aura_timer" in target: t_thorn = target.thorn_aura_timer
     elif typeof(target) == TYPE_OBJECT and target.has_method("has_meta") and target.has_meta("thorn_aura_timer"): t_thorn = target.get_meta("thorn_aura_timer")

     if a_team == t_team and t_thorn > 0.0:
         var orig_damage = 10.0
         if typeof(attacker) == TYPE_OBJECT and "damage" in attacker: orig_damage = attacker.damage
         elif typeof(attacker) == TYPE_OBJECT and attacker.has_method("has_meta") and attacker.has_meta("damage"): orig_damage = attacker.get_meta("damage")

         if self.world != null and self.world.has_method("_deal_damage"):
             var old_dmg = 10.0
             if typeof(target) == TYPE_OBJECT and "damage" in target: old_dmg = target.damage
             elif typeof(target) == TYPE_OBJECT and target.has_method("has_meta") and target.has_meta("damage"): old_dmg = target.get_meta("damage")

             if typeof(target) == TYPE_OBJECT and "damage" in target: target.damage = orig_damage
             elif typeof(target) == TYPE_OBJECT and target.has_method("set_meta"): target.set_meta("damage", orig_damage)

             self.world._deal_damage(target, attacker)

             if typeof(target) == TYPE_OBJECT and "damage" in target: target.damage = old_dmg
             elif typeof(target) == TYPE_OBJECT and target.has_method("set_meta"): target.set_meta("damage", old_dmg)
         return
     ```
   - Decay `thorn_aura_timer` in `action.gd`:
     ```gdscript
     var t_thorn = 0.0
     if "thorn_aura_timer" in self.ball: t_thorn = self.ball.thorn_aura_timer
     elif self.ball.has_method("has_meta") and self.ball.has_meta("thorn_aura_timer"): t_thorn = self.ball.get_meta("thorn_aura_timer")
     if t_thorn > 0.0:
         t_thorn -= delta
         if "thorn_aura_timer" in self.ball: self.ball.thorn_aura_timer = t_thorn
         elif self.ball.has_method("set_meta"): self.ball.set_meta("thorn_aura_timer", t_thorn)
     ```

4. **Testing & PR Preparation**
   - Create tests to verify the thorn logic.
   - Run tests.
   - Create IDEAS INBOX.
   - Run quality metrics and verify.
   - Create PR using git and gh.
