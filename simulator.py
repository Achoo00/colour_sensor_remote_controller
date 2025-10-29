import time
from actions import perform_action

class ColorSimulator:
    def __init__(self, mode_config, sequence_window=2.5):
        self.mode_config = mode_config
        self.sequence_history = []
        self.sequence_window = sequence_window

    def record_color(self, color):
        now = time.time()
        self.sequence_history.append((color, now))
        self.sequence_history = [
            (c, t) for c, t in self.sequence_history if now - t < self.sequence_window
        ]

    def get_recent_sequence(self, length=2):
        """Get the most recent sequence of colors and their timestamps."""
        if len(self.sequence_history) < length:
            return None, None
        
        colors = [c for c, _ in self.sequence_history[-length:]]
        times = [t for _, t in self.sequence_history[-length:]]
        return colors, times
    
    def check_sequences(self):
        """Check if any configured sequences match the recent input."""
        if "sequences" not in self.mode_config:
            return False

        for seq in self.mode_config["sequences"]:
            if isinstance(seq, dict) and "pattern" in seq:
                pattern = seq["pattern"]
                seq_time = seq.get("time_window", self.sequence_window)
                
                colors, times = self.get_recent_sequence(len(pattern))
                if not colors:
                    continue
                    
                if colors == pattern and (times[-1] - times[0]) <= seq_time:
                    print(f"🎯 Sequence matched: {'→'.join(pattern)}")
                    if "action" in seq:
                        perform_action(seq["action"])
                    self.sequence_history.clear()
                    return True
        return False
