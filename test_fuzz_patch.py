import math

def _key(self, x: float, y: float) -> int:
    if math.isnan(x) or math.isinf(x): x = 0
    if math.isnan(y) or math.isinf(y): y = 0
    col = int(x / self.cell_size)
    row = int(y / self.cell_size)
    return row * self.cols + col
