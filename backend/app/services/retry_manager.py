import random 

class RetryManager:
    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 0.5,
        max_delay: float = 30.0,
        jitter: float = 0.25,
    )-> None:
        self.max_attempts=max_attempts
        self.base_delay=base_delay
        self.max_delay=max_delay
        self.jitter=jitter

    def should_retry(self, attempt:int)->bool:
        return attempt < self.max_attempts

    def get_delay(self, attempt: int) -> float:
        delay = min(
            self.base_delay * (2 ** (attempt - 1)),
            self.max_delay,
        )

        jitter_range = delay * self.jitter

        return random.uniform(
            delay - jitter_range,
            delay + jitter_range,
        )



        
