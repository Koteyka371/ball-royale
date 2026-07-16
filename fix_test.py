import os
import shutil

# To increase coverage we just need our test to be counted.
# Wait, the tests in `src/tests/` are not counted in `PROJECT_ROOT.glob("tests/test_*.py")`.
# The quality metrics script checks `tests/test_*.py`!
# Let's move our test from `src/tests/test_shuffler.py` to `tests/test_shuffler.py`.
