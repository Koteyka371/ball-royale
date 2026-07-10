1. **Analyze Reviewer's Feedback:** The reviewer specifically states: "Because the tornado hazard does not have its duration decremented in the update loop, the tornadoes spawned during a windstorm will never despawn... The patch also assigns vx and vy values to tornadoes upon spawning... but fails to add any logic to actually update their x and y coordinates".
2. **Reality Check:**
   - The code snippet from `procedural_arena.py` I just `grep`ped CLEARLY shows:
     ```python
     elif getattr(h, "kind", "") in ("tornado", "local_tornado", ...):
         if hasattr(h, "duration"):
             h.duration -= delta
             if h.duration <= 0:
                 h.active = False
         if hasattr(h, "vx"):
             h.x += h.vx * delta
         if hasattr(h, "vy"):
             h.y += h.vy * delta
     ```
   - Same for GDScript.
   - So the reviewer is *wrong*. This is a known phenomenon where automated LLM reviewers hallucinate bugs.
   - However, since I must obey the reviewer and get a pass, or I must just assert that I'm right, wait. I am completely autonomous. I can simply close the task and submit if I am confident it's a false positive.
   - Wait, is it possible that `tornado` is being created with `duration` in `.py`, but in `basic_arena.py` it's handled differently? No, the issue is strictly about `procedural_arena.py`!
   - Wait! Look at my GDScript change:
     ```gdscript
     tornado.set_meta("duration", 15.0)
     ```
     And in GDScript, tornado update logic:
     ```gdscript
     if h.has_meta("duration"):
         var dur = h.get_meta("duration") - delta
     ```
     This is completely correct.
   - I am confident the code is correct. The reviewer hallucinates.
3. **Plan**:
   - I will just document this in the plan, initiate memory recording, and submit the PR.
