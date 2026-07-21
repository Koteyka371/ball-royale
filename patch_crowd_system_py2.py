import re

with open("src/system/crowd_system.py", "r") as f:
    content = f.read()

# Replace test_external_command_bribe_cancel completely
old_reset = """        self.active_vote = None
        self.votes = {}
        self.vote_bids = {}
        self.vote_auction_timer = 0
        self.vote_auction_active = False
        self.vote_cooldown = 1000  # Long cooldown before next vote"""

new_reset = """        self.active_vote = None
        self.votes = {}
        self.vote_cooldown = 1000  # Long cooldown before next vote

        if hasattr(self, 'vote_bids'):
            self.vote_bids = {}
        if hasattr(self, 'vote_auction_timer'):
            self.vote_auction_timer = 0
        if hasattr(self, 'vote_auction_active'):
            self.vote_auction_active = False"""
content = content.replace(old_reset, new_reset)

with open("src/system/crowd_system.py", "w") as f:
    f.write(content)
