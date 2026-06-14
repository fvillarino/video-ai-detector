import time


class CooldownRateLimiter:
    """Permite una acción por key cada N segundos."""

    def __init__(self, cooldown_seconds: float):
        self.cooldown = cooldown_seconds
        self._last_trigger: dict[str, float] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        last = self._last_trigger.get(key, 0.0)
        if now - last >= self.cooldown:
            self._last_trigger[key] = now
            return True
        return False
