import json
import random
import time
from typing import Dict, List, Any, Optional

class GuildAuctionManager:
    def __init__(self, filename="guild_auction.json"):
        self.filename = filename
        self.data = self.load()
        self.active_listings = self.data.get("listings", [])

        # Determine auction hours (e.g., opens 18:00 to 22:00 server time)
        self.auction_open_hour = 18
        self.auction_close_hour = 22

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "listings" not in data:
                    data["listings"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"listings": []}

    def save(self):
        self.data["listings"] = self.active_listings
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def is_auction_open(self, current_time: Optional[float] = None) -> bool:
        if current_time is None:
            current_time = time.time()

        t = time.localtime(current_time)
        return self.auction_open_hour <= t.tm_hour < self.auction_close_hour

    def generate_rare_booster(self) -> Dict[str, Any]:
        booster_types = ["stat_modifier", "unique_aura", "skill_enhancer"]
        booster_type = random.choice(booster_types)

        stats = ["speed", "power", "health", "armor"]
        chosen_stats = random.sample(stats, 2)

        multiplier = random.uniform(1.2, 1.5)

        return {
            "booster_type": booster_type,
            "stats": chosen_stats,
            "multiplier": round(multiplier, 2),
            "description": f"Extremely rare {booster_type} granting {chosen_stats[0]} and {chosen_stats[1]} bonus."
        }

    def list_procedural_item(self, guild_name: str, starting_bid: int, duration_hours: int = 1):
        if not self.is_auction_open():
            return None

        item = self.generate_rare_booster()

        listing_id = f"list_{int(time.time())}_{random.randint(1000, 9999)}"
        listing = {
            "id": listing_id,
            "item": item,
            "seller": guild_name,
            "starting_bid": starting_bid,
            "current_bid": starting_bid,
            "highest_bidder": None,
            "end_time": time.time() + (duration_hours * 3600)
        }
        self.active_listings.append(listing)
        self.save()
        return listing_id

    def get_active_listings(self) -> List[Dict[str, Any]]:
        current_time = time.time()
        return [l for l in self.active_listings if l["end_time"] > current_time]

    def place_bid(self, listing_id: str, guild_name: str, bid_amount: int, guild_manager: Any) -> bool:
        if not self.is_auction_open():
            return False

        listing = next((l for l in self.active_listings if l["id"] == listing_id), None)
        if not listing:
            return False

        if time.time() >= listing["end_time"]:
            return False

        if bid_amount <= listing["current_bid"]:
            return False

        if guild_name not in guild_manager.data.get("guilds", {}):
            return False

        guild = guild_manager.data["guilds"][guild_name]
        resources = guild.get("resources", 0)

        if resources < bid_amount:
            return False

        # Refund previous bidder if any
        if listing["highest_bidder"]:
            prev_bidder = listing["highest_bidder"]
            if prev_bidder in guild_manager.data["guilds"]:
                prev_guild = guild_manager.data["guilds"][prev_bidder]
                prev_guild["resources"] = prev_guild.get("resources", 0) + listing["current_bid"]

        # Deduct from new bidder
        guild["resources"] -= bid_amount

        listing["highest_bidder"] = guild_name
        listing["current_bid"] = bid_amount

        guild_manager.save()
        self.save()
        return True

    def resolve_auctions(self, guild_manager: Any):
        current_time = time.time()
        ongoing = []

        for listing in self.active_listings:
            if current_time >= listing["end_time"]:
                # Auction ended
                if listing["highest_bidder"]:
                    winner = listing["highest_bidder"]
                    if winner in guild_manager.data.get("guilds", {}):
                        winner_guild = guild_manager.data["guilds"][winner]
                        hq = winner_guild.setdefault("hq", {})
                        inventory = hq.setdefault("auction_items", [])
                        inventory.append(listing["item"])
                        guild_manager.save()
            else:
                ongoing.append(listing)

        self.active_listings = ongoing
        self.save()
