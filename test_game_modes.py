def check():
    with open('src/ai/game_modes.py', 'r') as f:
        content = f.read()

    idx = content.find('def apply_dynamic_traits')
    print(content[idx:idx+1500])

check()
