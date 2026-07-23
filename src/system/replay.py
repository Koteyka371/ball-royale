import json
from typing import Any, Dict, List, Optional

class ReplaySystem:
    """
    Manages recording, playback, and highlight extraction for the game.
    """
    def __init__(self):
        self.frames: List[Dict[str, Any]] = []
        self.current_frame_index = 0
        self.is_recording = False
        self.is_playing = False
        self.playback_speed = 1.0
        self.commentary: List[str] = []

    def start_recording(self):
        self.frames = []
        self.is_recording = True
        self.is_playing = False

    def stop_recording(self):
        self.is_recording = False

    def record_frame(self, tick: int, entities: List[Dict[str, Any]], events: List[Dict[str, Any]]):
        if not self.is_recording:
            return

        # Deep copy to ensure state is captured
        # Simplified for mock objects typically used in tests
        import copy
        try:
            entities_copy = copy.deepcopy(entities)
            events_copy = copy.deepcopy(events)
        except Exception:
            # Fallback if uncopyable
            entities_copy = [dict(e) if isinstance(e, dict) else e for e in entities]
            events_copy = [dict(e) if isinstance(e, dict) else e for e in events]

        frame = {
            "tick": tick,
            "entities": entities_copy,
            "events": events_copy
        }
        self.frames.append(frame)

    def start_playback(self, speed: float = 1.0):
        self.is_playing = True
        self.is_recording = False
        self.current_frame_index = 0
        self.playback_speed = speed

        # In python we simulate TTS or just print it if present
        if self.commentary:
            print(f"[TTS COMMENTARY]: {self.commentary[0]}")

    def stop_playback(self):
        self.is_playing = False

    def get_next_frame(self) -> Optional[Dict[str, Any]]:
        if not self.is_playing or self.current_frame_index >= len(self.frames):
            return None

        frame = self.frames[self.current_frame_index]
        # In a real game, logic to advance based on delta time and playback speed would be here.
        # For simplicity, we just advance by 1 frame.
        self.current_frame_index += 1
        return frame

    def set_frame(self, index: int):
        if 0 <= index < len(self.frames):
            self.current_frame_index = index

    def extract_highlight(self, start_tick: int, end_tick: int) -> 'ReplaySystem':
        """
        Extracts a subset of frames based on tick range.
        Returns a new ReplaySystem instance with the highlight frames.
        """
        highlight = ReplaySystem()
        highlight.frames = [f for f in self.frames if start_tick <= f["tick"] <= end_tick]

        kill_count = 0
        player_ids = []
        for f in highlight.frames:
            for e in f.get("events", []):
                if e.get("type") == "kill":
                    kill_count += 1
                    killer_id = e.get("killer_id")
                    if killer_id not in player_ids:
                        player_ids.append(killer_id)

        if kill_count > 0:
            pid = player_ids[0] if player_ids else "unknown"
            highlight.commentary.append(f"Incredible performance! {kill_count} eliminations by player {pid}!")
        else:
            highlight.commentary.append("A very tense moment where survival was the only option.")

        return highlight

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frames": self.frames,
            "version": "1.0"
        }

    def from_dict(self, data: Dict[str, Any]):
        self.frames = data.get("frames", [])
        self.current_frame_index = 0
        self.is_recording = False
        self.is_playing = False

    def save_to_file(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f)

    def load_from_file(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.from_dict(data)
