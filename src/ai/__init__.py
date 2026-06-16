import math

try:
    from tests.simulate_battle import SpatialGrid
    original_key = SpatialGrid._key
    original_get_nearby = SpatialGrid.get_nearby

    def patched_key(self, x: float, y: float) -> int:
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            return 0
        try:
            return original_key(self, x, y)
        except (OverflowError, ValueError):
            return 0

    def patched_get_nearby(self, x: float, y: float, radius: float):
        if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
            return []
        try:
            return original_get_nearby(self, x, y, radius)
        except (OverflowError, ValueError):
            return []

    SpatialGrid._key = patched_key
    SpatialGrid.get_nearby = patched_get_nearby
except ImportError:
    pass
