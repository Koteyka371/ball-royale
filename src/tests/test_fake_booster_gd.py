import pytest
import os

def test_gdscript_patched():
    with open("src/ai/action.gd", "r") as f:
        content = f.read()

    assert 'b.silence_timer = max(current_silence, 5.0)' in content
    assert 'b.set_meta("silence_timer", max(current_silence, 5.0))' in content
