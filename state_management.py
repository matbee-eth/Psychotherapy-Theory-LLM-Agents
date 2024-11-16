import math
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from enhanced_memory_system import Memory
from interaction_context import MessageAnalysis
from personality_framework import SocialPenetrationLayer
from state import PsychologicalVariable, RelationshipStage

@dataclass
class ResponseContext:
    """Context for response generation including memories"""
    message: str
    analysis: MessageAnalysis
    episodic_memories: List[Memory]
    emotional_memories: List[Memory]
    behavioral_memories: List[Memory]
    current_state: Dict[str, Any]

@dataclass
class GeneratedResponse:
    """A generated response with its context"""
    content: str
    confidence: float
    emotion: str
    memory_references: List[str]  # IDs of memories referenced
    reasoning: str


class StateManager:
    """Manages psychological state variables and their interactions"""
    
    def __init__(self):
        self.variables = self._initialize_variables()
        self.relationship_stage = RelationshipStage.INITIAL
        self.social_penetration_layer = SocialPenetrationLayer.PERIPHERAL
        self.interaction_count = 0
        self.last_interaction = datetime.now()
        
    def _initialize_variables(self) -> Dict[str, PsychologicalVariable]:
        """Initialize all psychological variables with default values"""
        return {
            "trust": PsychologicalVariable(
                name="trust",
                value=0.0,
                min_value=0.0,
                max_value=100.0,
                decay_rate=0.01,  # 1% decay per hour
                recovery_rate=2.0,
                dependencies=[],
                last_update=datetime.now()
            ),
            "emotional_connection": PsychologicalVariable(
                name="emotional_connection",
                value=0.0,
                min_value=0.0,
                max_value=100.0,
                decay_rate=0.005,
                recovery_rate=1.5,
                dependencies=["trust"],
                last_update=datetime.now()
            ),
            "self_disclosure": PsychologicalVariable(
                name="self_disclosure",
                value=0.0,
                min_value=0.0,
                max_value=100.0,
                decay_rate=0.008,
                recovery_rate=2.0,
                dependencies=["trust", "emotional_connection"],
                last_update=datetime.now()
            ),
            "interest_alignment": PsychologicalVariable(
                name="interest_alignment",
                value=0.0,
                min_value=0.0,
                max_value=100.0,
                decay_rate=0.002,
                recovery_rate=1.0,
                dependencies=[],
                last_update=datetime.now()
            ),
            "uncertainty": PsychologicalVariable(
                name="uncertainty",
                value=100.0,
                min_value=0.0,
                max_value=100.0,
                decay_rate=0.0,  # Doesn't decay with time
                recovery_rate=-5.0,  # Negative because we want it to decrease
                dependencies=["trust"],
                last_update=datetime.now()
            )
        }
    
    def process_interaction(
        self,
        interaction_quality: float,
        shared_interests: List[str],
        emotional_depth: float,
        self_disclosure_level: float
    ) -> Dict:
        """Process an interaction and update all relevant variables"""
        
        # Calculate time elapsed since last interaction
        time_elapsed = datetime.now() - self.last_interaction
        
        # Calculate variable updates
        updates = self._calculate_variable_updates(
            interaction_quality,
            shared_interests,
            emotional_depth,
            self_disclosure_level,
            time_elapsed
        )
        
        # Apply updates
        self._apply_updates(updates, time_elapsed)
        
        # Check for stage transitions
        self._check_stage_transitions()
        
        # Update interaction metadata
        self.interaction_count += 1
        self.last_interaction = datetime.now()
        
        return self.get_state()
    
    def _calculate_variable_updates(
        self,
        interaction_quality: float,
        shared_interests: List[str],
        emotional_depth: float,
        self_disclosure_level: float,
        time_elapsed: timedelta
    ) -> Dict[str, float]:
        """Calculate updates for all variables based on interaction"""
        
        # Base updates
        updates = {
            "trust": self._calculate_trust_change(
                interaction_quality,
                emotional_depth,
                time_elapsed
            ),
            "emotional_connection": self._calculate_emotional_connection_change(
                emotional_depth,
                self_disclosure_level
            ),
            "self_disclosure": self._calculate_self_disclosure_change(
                self_disclosure_level,
                interaction_quality
            ),
            "interest_alignment": self._calculate_interest_alignment_change(
                shared_interests,
                interaction_quality
            ),
            "uncertainty": self._calculate_uncertainty_change(
                interaction_quality,
                self_disclosure_level
            )
        }
        
        # Apply dependency effects
        self._apply_dependency_effects(updates)
        
        return updates
    
    def _calculate_trust_change(
        self,
        interaction_quality: float,
        emotional_depth: float,
        time_elapsed: timedelta
    ) -> float:
        """Calculate trust change based on interaction"""
        base_change = interaction_quality * 5  # -5 to +5
        depth_multiplier = 1 + (emotional_depth * 0.5)  # 1 to 1.5
        current_trust = self.variables["trust"].value
        
        # Trust harder to gain at higher levels
        trust_resistance = math.sqrt(current_trust / 100)
        
        return base_change * depth_multiplier * (1 - trust_resistance)
    
    def _calculate_emotional_connection_change(
        self,
        emotional_depth: float,
        self_disclosure_level: float
    ) -> float:
        """Calculate emotional connection change"""
        base_change = emotional_depth * 3  # 0 to 3
        disclosure_multiplier = 1 + (self_disclosure_level * 0.5)  # 1 to 1.5
        return base_change * disclosure_multiplier
    
    def _calculate_self_disclosure_change(
        self,
        self_disclosure_level: float,
        interaction_quality: float
    ) -> float:
        """Calculate self-disclosure change"""
        base_change = self_disclosure_level * 4  # 0 to 4
        quality_multiplier = max(0, interaction_quality)  # 0 to 1
        return base_change * quality_multiplier
    
    def _calculate_interest_alignment_change(
        self,
        shared_interests: List[str],
        interaction_quality: float
    ) -> float:
        """Calculate interest alignment change"""
        interest_factor = len(shared_interests) * 2  # 2 points per shared interest
        quality_multiplier = max(0, interaction_quality)  # 0 to 1
        return interest_factor * quality_multiplier
    
    def _calculate_uncertainty_change(
        self,
        interaction_quality: float,
        self_disclosure_level: float
    ) -> float:
        """Calculate uncertainty change"""
        base_reduction = -5  # Base reduction of 5 points
        quality_factor = 1 + max(0, interaction_quality)  # 1 to 2
        disclosure_factor = 1 + self_disclosure_level  # 1 to 2
        return base_reduction * quality_factor * disclosure_factor
    
    def _apply_dependency_effects(self, updates: Dict[str, float]) -> None:
        """Apply effects of variable dependencies"""
        for var_name, variable in self.variables.items():
            for dependency in variable.dependencies:
                if dependency in updates:
                    # Positive dependencies increase effect, negative decrease
                    dependency_effect = updates[dependency] * 0.2  # 20% effect
                    updates[var_name] += dependency_effect
    
    def _apply_updates(self, updates: Dict[str, float], time_elapsed: timedelta) -> None:
        """Apply calculated updates to variables"""
        for var_name, delta in updates.items():
            self.variables[var_name].update(delta, time_elapsed)
    
    def _check_stage_transitions(self) -> None:
        """Check and perform relationship stage transitions"""
        trust_level = self.variables["trust"].value
        emotional_connection = self.variables["emotional_connection"].value
        
        # Define stage thresholds
        thresholds = {
            RelationshipStage.ACQUAINTANCE: (20, 10),  # (trust, emotional_connection)
            RelationshipStage.FRIEND: (40, 30),
            RelationshipStage.CLOSE_FRIEND: (60, 50),
            RelationshipStage.CONFIDANT: (80, 70)
        }
        
        # Check each stage in reverse order
        for stage, (trust_threshold, emotional_threshold) in reversed(thresholds.items()):
            if (trust_level >= trust_threshold and 
                emotional_connection >= emotional_threshold):
                if self.relationship_stage.value < stage.value:
                    self.relationship_stage = stage
                break
        
        # Update social penetration layer based on self-disclosure
        self_disclosure = self.variables["self_disclosure"].value
        if self_disclosure >= 80:
            self.social_penetration_layer = SocialPenetrationLayer.CORE
        elif self_disclosure >= 60:
            self.social_penetration_layer = SocialPenetrationLayer.PERSONAL
        elif self_disclosure >= 30:
            self.social_penetration_layer = SocialPenetrationLayer.INTERMEDIATE
    
    def get_state(self) -> Dict:
        """Get current state of all variables and relationship"""
        return {
            "variables": {
                name: {
                    "value": var.value,
                    "last_update": var.last_update
                } for name, var in self.variables.items()
            },
            "relationship_stage": self.relationship_stage,
            "social_penetration_layer": self.social_penetration_layer,
            "interaction_count": self.interaction_count,
            "last_interaction": self.last_interaction
        }

# Example usage
def test_state_manager():
    manager = StateManager()
    
    # Simulate a positive interaction
    state = manager.process_interaction(
        interaction_quality=0.8,
        shared_interests=["music", "travel"],
        emotional_depth=0.6,
        self_disclosure_level=0.4
    )
    
    print("After positive interaction:")
    print(f"Trust level: {manager.variables['trust'].value:.2f}")
    print(f"Emotional connection: {manager.variables['emotional_connection'].value:.2f}")
    print(f"Relationship stage: {manager.relationship_stage}")
    print(f"Social penetration layer: {manager.social_penetration_layer}")

if __name__ == "__main__":
    test_state_manager()