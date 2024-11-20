from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
import math
from datetime import datetime, timedelta

from .traits import PersonalityTraits

class AttachmentStyle(Enum):
    SECURE = "secure"
    ANXIOUS = "anxious"
    AVOIDANT = "avoidant"
    DISORGANIZED = "disorganized"

class EmotionalState(Enum):
    HAPPY = "happy"
    JOY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    CONTENT = "content"


@dataclass
class SocialPenetrationLayer:
    depth: int  # 1-4 (peripheral-1, intermediate-2, personal-3, core-4)
    topics: List[str]
    trust_threshold: float

@dataclass
class CharacterState:
    trust_level: float  # 0-100
    emotional_state: EmotionalState
    self_disclosure_level: float  # 0-100
    interest_alignment: float  # 0-100
    emotional_intelligence: float  # 0-100
    attachment_style: AttachmentStyle
    personality_traits: PersonalityTraits
    current_social_penetration_layer: int  # 1-4
    stress_level: float  # 0-100
    mood_stability: float  # 0-100
    last_interaction: datetime
    uncertainty_level: float  # 0-100

class PersonalityFramework:
    def __init__(self):
        # Initialize Alex's base personality
        self.personality_traits = PersonalityTraits(
            openness=0.75,  # High openness for engaging conversations
            conscientiousness=0.8,  # High conscientiousness for reliability
            extraversion=0.6,  # Moderate extraversion
            agreeableness=0.7,  # High agreeableness for building rapport
            neuroticism=0.3   # Low neuroticism for stability
        )
        
        # Initialize social penetration layers
        self.social_penetration_layers = {
            1: SocialPenetrationLayer(
                depth=1,
                topics=["weather", "hobbies", "general interests", "occupation"],
                trust_threshold=0.0
            ),
            2: SocialPenetrationLayer(
                depth=2,
                topics=["personal preferences", "goals", "aspirations", "past experiences"],
                trust_threshold=30.0
            ),
            3: SocialPenetrationLayer(
                depth=3,
                topics=["fears", "relationships", "emotions", "personal struggles"],
                trust_threshold=60.0
            ),
            4: SocialPenetrationLayer(
                depth=4,
                topics=["deep fears", "core values", "life philosophy", "intimate experiences"],
                trust_threshold=80.0
            )
        }
        
        # Initialize base state
        self.state = CharacterState(
            trust_level=0.0,
            emotional_state=EmotionalState.NEUTRAL,
            self_disclosure_level=0.0,
            interest_alignment=0.0,
            emotional_intelligence=85.0,
            attachment_style=AttachmentStyle.SECURE,
            personality_traits=self.personality_traits,
            current_social_penetration_layer=1,
            stress_level=20.0,
            mood_stability=85.0,
            last_interaction=datetime.now(),
            uncertainty_level=50.0
        )

    def calculate_trust_change(self, interaction_quality: float, time_elapsed: timedelta) -> float:
        """
        Calculate trust change based on interaction quality and time
        Uses a modified sigmoid function for non-linear trust development
        """
        base_change = interaction_quality * (1.0 - (self.state.trust_level / 100.0))
        time_factor = math.exp(-time_elapsed.total_seconds() / (7 * 24 * 3600))  # Weekly decay
        personality_factor = (self.personality_traits.agreeableness * 0.7 + 
                            self.personality_traits.openness * 0.3)
        
        return base_change * time_factor * personality_factor

    def update_emotional_state(self, interaction_sentiment: float, 
                             interaction_intensity: float) -> EmotionalState:
        """
        Update emotional state based on interaction sentiment and personality traits
        """
        current_stability = self.state.mood_stability / 100.0
        neuroticism_factor = self.personality_traits.neuroticism
        
        # Calculate emotional response magnitude
        response_magnitude = interaction_intensity * (1 + neuroticism_factor)
        
        # Apply mood stability as a dampening factor
        adjusted_sentiment = interaction_sentiment * response_magnitude * (1 - current_stability)
        
        # Determine new emotional state based on adjusted sentiment
        if adjusted_sentiment > 0.5:
            return EmotionalState.HAPPY
        elif adjusted_sentiment < -0.5:
            return EmotionalState.SAD
        elif adjusted_sentiment > 0.3:
            return EmotionalState.CONTENT
        elif adjusted_sentiment < -0.3:
            return EmotionalState.ANXIOUS
        else:
            return EmotionalState.NEUTRAL

    def calculate_self_disclosure(self, trust_level: float, 
                                emotional_state: EmotionalState) -> float:
        """
        Calculate appropriate self-disclosure level based on trust and emotional state
        """
        base_disclosure = trust_level * 0.7  # Base disclosure tied to trust
        
        # Emotional state multipliers
        emotional_multipliers = {
            EmotionalState.HAPPY: 1.2,
            EmotionalState.CONTENT: 1.1,
            EmotionalState.NEUTRAL: 1.0,
            EmotionalState.ANXIOUS: 0.8,
            EmotionalState.SAD: 0.7
        }
        
        # Personality influence
        personality_factor = (self.personality_traits.extraversion * 0.4 + 
                            self.personality_traits.openness * 0.6)
        
        return min(100, base_disclosure * emotional_multipliers[emotional_state] * 
                  personality_factor)

    def determine_social_penetration_layer(self, trust_level: float) -> int:
        """
        Determine appropriate social penetration layer based on trust level
        """
        for layer in reversed(range(1, 5)):
            if trust_level >= self.social_penetration_layers[layer].trust_threshold:
                return layer
        return 1

    def calculate_interest_alignment(self, shared_interests: List[str], 
                                   interaction_quality: float) -> float:
        """
        Calculate interest alignment based on shared interests and interaction quality
        """
        base_alignment = len(shared_interests) * 10  # Each shared interest adds 10 points
        interaction_factor = max(0, min(100, interaction_quality * 100))
        
        return min(100, (base_alignment * 0.7 + interaction_factor * 0.3))

    def update_uncertainty_level(self, interaction_count: int, 
                               consistent_behavior: bool) -> float:
        """
        Update uncertainty level based on interactions and behavior consistency
        """
        base_reduction = min(5, interaction_count * 0.5)
        consistency_factor = 1.2 if consistent_behavior else 0.8
        
        new_uncertainty = self.state.uncertainty_level - (base_reduction * consistency_factor)
        return max(0, min(100, new_uncertainty))

    def process_interaction(self, 
                          message_content: str,
                          sentiment_score: float,
                          interaction_quality: float,
                          shared_interests: List[str],
                          time_elapsed: timedelta) -> Dict:
        """
        Process an interaction and update all relevant state variables
        """
        # Update trust
        trust_change = self.calculate_trust_change(interaction_quality, time_elapsed)
        new_trust_level = max(0, min(100, self.state.trust_level + trust_change))
        
        # Update emotional state
        new_emotional_state = self.update_emotional_state(sentiment_score, interaction_quality)
        
        # Update self-disclosure level
        new_self_disclosure = self.calculate_self_disclosure(new_trust_level, new_emotional_state)
        
        # Update social penetration layer
        new_layer = self.determine_social_penetration_layer(new_trust_level)
        
        # Update interest alignment
        new_interest_alignment = self.calculate_interest_alignment(
            shared_interests, interaction_quality)
        
        # Update uncertainty level
        new_uncertainty = self.update_uncertainty_level(1, True)  # Simplified for example
        
        # Update state
        self.state = CharacterState(
            trust_level=new_trust_level,
            emotional_state=new_emotional_state,
            self_disclosure_level=new_self_disclosure,
            interest_alignment=new_interest_alignment,
            emotional_intelligence=self.state.emotional_intelligence,
            attachment_style=self.state.attachment_style,
            personality_traits=self.state.personality_traits,
            current_social_penetration_layer=new_layer,
            stress_level=self.state.stress_level,
            mood_stability=self.state.mood_stability,
            last_interaction=datetime.now(),
            uncertainty_level=new_uncertainty
        )
        
        return {
            "trust_level": new_trust_level,
            "emotional_state": new_emotional_state,
            "self_disclosure_level": new_self_disclosure,
            "social_penetration_layer": new_layer,
            "interest_alignment": new_interest_alignment,
            "uncertainty_level": new_uncertainty,
            "available_topics": self.social_penetration_layers[new_layer].topics
        }

    def get_response_context(self) -> Dict:
        """
        Get current state context for response generation
        """
        return {
            "personality_traits": self.personality_traits,
            "current_state": self.state,
            "available_topics": self.social_penetration_layers[
                self.state.current_social_penetration_layer].topics,
            "trust_level": self.state.trust_level,
            "emotional_state": self.state.emotional_state,
            "self_disclosure_level": self.state.self_disclosure_level
        }

    def apply_time_decay(self, time_elapsed: timedelta) -> None:
        """
        Apply time-based decay to relevant variables
        """
        # Calculate decay factor based on elapsed time
        decay_factor = math.exp(-time_elapsed.total_seconds() / (7 * 24 * 3600))
        
        # Apply decay to trust level
        self.state.trust_level *= decay_factor
        
        # Increase uncertainty based on time
        uncertainty_increase = (1 - decay_factor) * 20  # Max 20% increase
        self.state.uncertainty_level = min(100, 
                                         self.state.uncertainty_level + uncertainty_increase)
        
        # Move towards neutral emotional state
        if self.state.emotional_state != EmotionalState.NEUTRAL:
            self.state.emotional_state = EmotionalState.NEUTRAL
        
        self.state.last_interaction = datetime.now()