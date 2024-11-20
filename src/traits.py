from dataclasses import dataclass


@dataclass
class PersonalityTraits:
    openness: float  # 0-1
    conscientiousness: float  # 0-1
    extraversion: float  # 0-1
    agreeableness: float  # 0-1
    neuroticism: float  # 0-1