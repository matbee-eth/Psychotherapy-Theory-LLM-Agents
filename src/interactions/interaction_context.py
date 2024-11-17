from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class InteractionType(Enum):
    MESSAGE = "message"
    QUESTION = "question"
    DISCLOSURE = "disclosure"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    REQUEST = "request"
    FEEDBACK = "feedback"

@dataclass
class MessageAnalysis:
    """Analysis results for a user message"""
    sentiment_score: float  # -1 to 1
    emotional_intensity: float  # 0 to 1
    topics: List[str]
    intent: InteractionType
    disclosure_level: float  # 0 to 1
    uncertainty_level: float  # 0 to 1
    key_entities: List[str]
    emotional_indicators: Dict[str, float]

@dataclass
class InteractionContext:
    """Maintains context for a single interaction"""
    
    # Message information
    message_id: str
    timestamp: datetime
    raw_message: str
    message_analysis: Optional[MessageAnalysis] = None
    
    # State snapshots
    previous_state: Dict[str, Any] = field(default_factory=dict)
    current_state: Dict[str, Any] = field(default_factory=dict)
    
    # Emotional agent states
    emotional_states: Dict[str, float] = field(default_factory=dict)
    controlling_emotion: str = "joy"
    
    # Memory context
    relevant_memories: List[Dict] = field(default_factory=list)
    interaction_history: List[Dict] = field(default_factory=list)
    
    # Theory guidance
    active_theories: List[str] = field(default_factory=list)
    theory_suggestions: Dict[str, List[str]] = field(default_factory=dict)
    
    # Response tracking
    generated_responses: List[Dict] = field(default_factory=list)
    selected_response: Optional[str] = None
    response_confidence: float = 0.0
    
    # Metadata
    processing_start: datetime = field(default_factory=datetime.now)
    processing_end: Optional[datetime] = None
    processing_steps: List[str] = field(default_factory=list)
    
    def add_processing_step(self, step: str) -> None:
        """Add a processing step with timestamp"""
        self.processing_steps.append({
            'step': step,
            'timestamp': datetime.now()
        })
    
    def update_emotional_state(self, emotion: str, value: float) -> None:
        """Update the intensity of an emotional state"""
        self.emotional_states[emotion] = value
    
    def add_theory_suggestion(self, theory: str, suggestion: str) -> None:
        """Add a suggestion from a psychological theory"""
        if theory not in self.theory_suggestions:
            self.theory_suggestions[theory] = []
        self.theory_suggestions[theory].append(suggestion)
    
    def add_generated_response(self, response: str, source: str, confidence: float) -> None:
        """Add a generated response with metadata"""
        self.generated_responses.append({
            'response': response,
            'source': source,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
    
    def select_response(self, response: str, confidence: float) -> None:
        """Set the selected response"""
        self.selected_response = response
        self.response_confidence = confidence
    
    def add_relevant_memory(self, memory: Dict) -> None:
        """Add a relevant memory to the context"""
        self.relevant_memories.append({
            **memory,
            'added_at': datetime.now()
        })
    
    def get_processing_duration(self) -> float:
        """Get the total processing duration in seconds"""
        end = self.processing_end or datetime.now()
        return (end - self.processing_start).total_seconds()
    
    def get_emotional_summary(self) -> Dict[str, Any]:
        """Get a summary of emotional states"""
        return {
            'dominant_emotion': max(self.emotional_states.items(), 
                                  key=lambda x: x[1])[0],
            'emotional_diversity': len([v for v in self.emotional_states.values() if v > 0.2]),
            'average_intensity': sum(self.emotional_states.values()) / len(self.emotional_states),
            'controlling_emotion': self.controlling_emotion
        }
    
    def get_theory_summary(self) -> Dict[str, Any]:
        """Get a summary of theory applications"""
        return {
            'active_theories': self.active_theories,
            'suggestion_count': sum(len(sugs) for sugs in self.theory_suggestions.values()),
            'theories_by_suggestions': sorted(
                [(theory, len(sugs)) for theory, sugs in self.theory_suggestions.items()],
                key=lambda x: x[1],
                reverse=True
            )
        }
    
    def finalize(self) -> None:
        """Finalize the interaction context"""
        self.processing_end = datetime.now()
        self.add_processing_step("Interaction completed")

class InteractionContextManager:
    """Manages creation and tracking of interaction contexts"""
    
    def __init__(self, max_history: int = 100):
        self.context_history: List[InteractionContext] = []
        self.max_history = max_history
        self.current_context: Optional[InteractionContext] = None
    
    def create_context(self, message: str) -> InteractionContext:
        """Create a new interaction context"""
        context = InteractionContext(
            message_id=self._generate_message_id(),
            timestamp=datetime.now(),
            raw_message=message
        )
        
        # Store previous context data if available
        if self.current_context:
            context.previous_state = self.current_context.current_state
            context.interaction_history = (
                self.current_context.interaction_history[-5:] +
                [{
                    'message': self.current_context.raw_message,
                    'response': self.current_context.selected_response,
                    'timestamp': self.current_context.timestamp
                }]
            )
        
        self.current_context = context
        return context
    
    def save_context(self, context: InteractionContext) -> None:
        """Save a completed interaction context"""
        self.context_history.append(context)
        if len(self.context_history) > self.max_history:
            self.context_history.pop(0)
    
    def get_recent_contexts(self, count: int = 5) -> List[InteractionContext]:
        """Get the most recent interaction contexts"""
        return self.context_history[-count:]
    
    def _generate_message_id(self) -> str:
        """Generate a unique message ID"""
        return f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.context_history)}"

# Example usage
def test_interaction_context():
    context_manager = InteractionContextManager()
    
    # Create a new context for a message
    context = context_manager.create_context("Hello, how are you today?")
    
    # Add some processing steps
    context.add_processing_step("Message received")
    context.update_emotional_state("joy", 0.7)
    context.update_emotional_state("sadness", 0.1)
    
    # Add theory suggestions
    context.add_theory_suggestion("social_penetration", 
                                "Maintain surface-level disclosure")
    context.add_theory_suggestion("attachment", 
                                "Show consistent availability")
    
    # Generate and select response
    context.add_generated_response(
        "I'm doing well, thank you! How has your day been?",
        "joy_agent",
        0.85
    )
    context.select_response(
        "I'm doing well, thank you! How has your day been?",
        0.85
    )
    
    # Finalize context
    context.finalize()
    
    # Save context
    context_manager.save_context(context)
    
    # Print summary
    print("Emotional Summary:", context.get_emotional_summary())
    print("Theory Summary:", context.get_theory_summary())
    print("Processing Duration:", context.get_processing_duration())

if __name__ == "__main__":
    test_interaction_context()