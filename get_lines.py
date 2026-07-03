with open("src/ai/action.gd") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "if world.arena.get(\"is_raining\") == true and not ignores_mud and not is_wind_riding_f:" in l:
        print(repr(lines[i]))
        print(repr(lines[i+1]))
        print(repr(lines[i+2]))
        print(repr(lines[i+3]))
        print(repr(lines[i+4]))
