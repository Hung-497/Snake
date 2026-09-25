"""Small, display-free rules for presentation effects."""

import math


FOOD_PULSE_SECONDS = 1.2
END_FLASH_SECONDS = 0.18
VIEW_FADE_SECONDS = 0.18


class ViewFade:
    """Fade out the current App View, switch, then reveal the next one."""

    def __init__(self):
        self.clear()

    def start(self, next_view):
        self.pending_view = next_view
        self.elapsed_seconds = 0.0
        self.switched = False

    def clear(self):
        self.pending_view = None
        self.elapsed_seconds = 0.0
        self.switched = False

    @property
    def active(self):
        return self.pending_view is not None

    @property
    def alpha(self):
        if not self.active:
            return 0

        half = VIEW_FADE_SECONDS / 2
        visible_fraction = min(self.elapsed_seconds, VIEW_FADE_SECONDS - self.elapsed_seconds) / half
        return round(255 * max(0.0, visible_fraction))

    def advance_by(self, elapsed_seconds):
        """Return the view to show once the overlay fully covers the old one."""
        if not self.active:
            return None

        self.elapsed_seconds = min(VIEW_FADE_SECONDS,
                                   self.elapsed_seconds + max(0.0, elapsed_seconds))
        next_view = None
        if not self.switched and self.elapsed_seconds >= VIEW_FADE_SECONDS / 2:
            self.switched = True
            next_view = self.pending_view

        if self.elapsed_seconds >= VIEW_FADE_SECONDS:
            self.clear()

        return next_view


def board_effects_enabled(speed_delay):
    """Fast games finish too often for repeated board effects to be comfortable."""
    return speed_delay > 1


def food_pulse_scale(elapsed_seconds):
    """Keep the food between 90% and 100% of its usual size."""
    return 0.95 + 0.05 * math.cos(math.tau * elapsed_seconds / FOOD_PULSE_SECONDS)


def end_flash_alpha(elapsed_seconds):
    """Fade a brief board flash from visible to transparent."""
    remaining = min(1.0, max(0.0, 1.0 - elapsed_seconds / END_FLASH_SECONDS))
    return round(80 * remaining * remaining)
