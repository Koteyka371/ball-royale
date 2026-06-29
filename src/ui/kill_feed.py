class KillFeed:
    def __init__(self, max_lines=5):
        self.max_lines = max_lines
        self.messages = []
        self._processed_ticks = set()

    def update(self, kill_log):
        for log in kill_log:
            if log.get("type") == "weather_warning":
                weather = log.get("weather", "clear")
                event_hash = f"{log.get('tick', 0)}_weather_warning_{weather}"
                if event_hash not in self._processed_ticks:
                    message = f"Tick {log.get('tick', 0)}: WARNING! {weather.upper()} approaching!"
                    self.messages.append(message)
                    self._processed_ticks.add(event_hash)
            elif log.get("type") == "weather_change":
                weather = log.get("weather", "clear")
                event_hash = f"{log.get('tick', 0)}_weather_{weather}"
                if event_hash not in self._processed_ticks:
                    message = f"Tick {log.get('tick', 0)}: Weather changed to {weather.upper()}!"
                    self.messages.append(message)
                    self._processed_ticks.add(event_hash)
            else:
                event_hash = f"{log.get('tick', 0)}_{log.get('killer_id', '?')}_{log.get('victim_id', '?')}"
                if event_hash not in self._processed_ticks:
                    killer = f"{str(log.get('killer_type', 'unknown')).upper()}-{log.get('killer_id', '?')}"
                    victim = f"{str(log.get('victim_type', 'unknown')).upper()}-{log.get('victim_id', '?')}"
                    message = f"Tick {log.get('tick', 0)}: {killer} killed {victim}"
                    self.messages.append(message)
                    self._processed_ticks.add(event_hash)

        if len(self.messages) > self.max_lines:
            self.messages = self.messages[-self.max_lines:]

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []
        self._processed_ticks = set()
