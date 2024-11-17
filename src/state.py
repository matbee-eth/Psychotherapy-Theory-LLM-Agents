from dataclasses import dataclass
from typing import List
from enum import Enum
from datetime import datetime, timedelta

class RelationshipStage(Enum):
    INITIAL = "initial"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    CONFIDANT = "confidant"

@dataclass
class PsychologicalVariable:
    """Represents a psychological variable with meta-information"""
    name: str
    value: float  # 0-100 scale
    min_value: float
    max_value: float
    decay_rate: float  # Per hour
    recovery_rate: float  # Per positive interaction
    dependencies: List[str]  # Names of variables this one depends on
    last_update: datetime
    
    def update(self, delta: float, time_elapsed: timedelta) -> None:
        """Update variable value considering time decay"""
        # Apply time decay
        decay = self.decay_rate * time_elapsed.total_seconds() / 3600
        self.value = max(self.min_value, 
                        min(self.max_value, 
                            self.value * (1 - decay) + delta))
        self.last_update = datetime.now()