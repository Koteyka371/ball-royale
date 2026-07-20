import re

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

new_mode = '''class CursedBoosterMode extends GameMode:
	func _init():
		super._init()
		self.name = "Cursed Boosters"
		self.description = "All boosters collected have the opposite of their intended effect, forcing players to avoid items they usually collect."

'''

if "CursedBoosterMode" not in content:
    idx = content.find('var GAME_MODES = {')

    content = content[:idx] + new_mode + content[idx:]

    target_reg = 'var GAME_MODES = {'
    replace_reg = 'var GAME_MODES = {\n	"cursed_boosters": CursedBoosterMode.new(),'
    content = content.replace(target_reg, replace_reg)

    with open("src/ai/game_modes.gd", "w") as f:
        f.write(content)
