# Ah, `is_stunned` is False because in `execute`:
# ```
#         if getattr(self.ball, "stutter_timer", 0.0) > 0:
#             # ...
#             # Wait, where is is_stunned set to False?
#             # Let's check `src/ai/action.py` again.
# ```
