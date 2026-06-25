import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from ai.train import train_networks

if __name__ == "__main__":
    train_networks(generations=1, population_size=4, ticks=50)
    print("Training test passed.")
