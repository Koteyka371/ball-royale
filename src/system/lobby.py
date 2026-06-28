class PreGameLobby:
    def __init__(self):
        self.selections = {}

    def select_trap_variant(self, ball_id, variant):
        if variant in ["normal", "poison", "stun"]:
            self.selections[ball_id] = variant

    def get_trap_variant(self, ball_id):
        return self.selections.get(ball_id, "normal")

lobby = PreGameLobby()
