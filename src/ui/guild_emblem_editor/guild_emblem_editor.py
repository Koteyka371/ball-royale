from system.guild import GuildManager

class GuildEmblemEditor:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.guild_manager = GuildManager("guilds.json")
        self.current_shape = "circle"
        self.current_color = "white"
        self.current_symbol = "none"

        self.available_shapes = ["circle", "shield", "square", "diamond", "hexagon"]
        self.available_colors = ["white", "red", "blue", "green", "gold", "black"]
        self.available_symbols = ["none", "sword", "crown", "skull", "star", "fire"]

    def _get_player_guild(self):
        player_id = self.profile_manager.data.get("username", "player1")
        for guild_name, guild_data in self.guild_manager.data.get("guilds", {}).items():
            if player_id in guild_data.get("members", []):
                return guild_name
        return None

    def refresh_ui(self):
        guild_name = self._get_player_guild()
        if guild_name:
            guild = self.guild_manager.get_guild(guild_name)
            emblem = guild.get("emblem", {"shape": "circle", "color": "white", "symbol": "none"})
            self.current_shape = emblem["shape"]
            self.current_color = emblem["color"]
            self.current_symbol = emblem["symbol"]
            return {
                "guild_name": guild_name,
                "current_emblem": emblem,
                "unlocked_parts": guild.get("unlocked_emblem_parts", {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]})
            }
        return {"error": "Not in a guild"}

    def save_emblem(self):
        guild_name = self._get_player_guild()
        if guild_name:
            return self.guild_manager.update_emblem(guild_name, self.current_shape, self.current_color, self.current_symbol)
        return False
