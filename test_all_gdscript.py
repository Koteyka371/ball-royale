import subprocess
import os

files = [
    "src/arena/procedural_arena.gd",
    "src/arena/arena_types.gd",
    "src/arena/basic_arena.gd",
]

for f in files:
    with open(f, 'r') as file:
        content = file.read()
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "\t" in line and " " in line[:line.find("\t")+1] and line.strip() != "":
                # mixed
                print(f"{f}:{i+1} MIXED INDENTATION: {line!r}")
