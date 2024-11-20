
import logging

from typing import Any, Dict, List, Optional
from datetime import datetime

import autogen

from ..base_agents import ProcessedResponse, ResponseSynthesizer
from ..councils.emotion_council import EmotionalCouncil
from ..councils.theory_council import TheoryCouncil
from ..emotions.base_emotion_agent import EmotionalAgent
from ..personality_framework import EmotionalState
from ..theories.base_theory_agent import TheoryAgent
from ..traits import PersonalityTraits

class ControlRoom:
    """Main orchestrator for the emotion-theory system"""
    
    def __init__(
        self,
        emotional_agents: List[EmotionalAgent],
        theory_agents: List[TheoryAgent],
        llm_config: dict,
        persona_name: str = "Alex"
    ):
        # Initialize components
        self.emotional_council = EmotionalCouncil(
            emotional_agents,
            llm_config,
            persona_name
        )
        self.emotional_agents = emotional_agents
        self.theory_council = TheoryCouncil(theory_agents, llm_config)
        self.response_synthesizer = ResponseSynthesizer(llm_config)
        
        # Set persona name
        self.persona_name = persona_name
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize state
        self.conversation_history = []
        self.current_context = {}
        self.processing_stats = {
            "total_interactions": 0,
            "average_processing_time": 0.0,
            "success_rate": 1.0
        }
    
    @property
    def current_controller(self) -> EmotionalAgent:
        """Get the current controlling emotional agent"""
        return self.emotional_council.current_controller
    
    async def process_input(self, sender: autogen.AssistantAgent, message: str, context: Optional[Dict] = None) -> ProcessedResponse:
        """Process a message through the complete emotion-theory pipeline"""
        start_time = datetime.now()
        context = context or {}
        
        try:
            # Update context with persona information
            self.current_context = self._update_context(context)
            
            # 1. Get emotional responses
            emotional_responses = await self.emotional_council.process(
                message,
                self.current_context
            )
            
            # 2. Get theory validations
            theory_validations = await self.theory_council.validate(
                message,
                emotional_responses,
                self.current_context
            )
            
            # 3. Synthesize final response
            response = await self.response_synthesizer.create_response(
                message,
                sender,
                emotional_responses,
                theory_validations,
                self.current_context
            )
            
            # 4. Add controller information
            response.controlling_emotion = self.current_controller.emotion
            
            # 5. Update history and stats
            self._update_history(message, response)
            self._update_stats(start_time)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in control room processing: {str(e)}", exc_info=True)
            self._update_stats(start_time, success=False)
            return self._create_fallback_response()
    
    def _update_context(self, new_context: Dict) -> Dict:
        """Update current context with new information"""
        return {
            **self.current_context,
            **new_context,
            "persona_name": self.persona_name,
            "current_controller": self.current_controller.emotion.value,
            "timestamp": datetime.now(),
            "interaction_count": len(self.conversation_history),
            "processing_stats": self.processing_stats
        }
    
    def _update_history(self, message: str, response: ProcessedResponse) -> None:
        """Update conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now(),
            "message": message,
            "response": response,
            "controlling_emotion": self.current_controller.emotion,
            "context": self.current_context.copy()
        })
    
    def _create_fallback_response(self) -> ProcessedResponse:
        """Create a safe fallback response"""
        return ProcessedResponse(
            content=f"I understand. Could you tell me more about that?",
            dominant_emotion=EmotionalState.NEUTRAL,
            controlling_emotion=self.current_controller.emotion,
            emotional_states={EmotionalState.NEUTRAL: 1.0},
            theory_scores={"fallback": 1.0},
            confidence=0.5,
            processing_time=0.0,
            context=self.current_context
        )

    def get_emotional_state(self) -> Dict[str, Any]:
        """Get current emotional state information"""
        return {
            "controlling_emotion": self.current_controller.emotion,
            "controller_influence": self.current_controller.state.influence,
            "controller_confidence": self.current_controller.state.confidence,
            "emotional_states": {
                emotion: agent.state.influence
                for emotion, agent in self.emotional_council.agents.items()
            }
        }

    def get_persona_info(self) -> Dict[str, Any]:
        """Get persona information"""
        return {
            "name": self.persona_name,
            "current_state": self.get_emotional_state(),
            "interaction_count": len(self.conversation_history),
            "processing_stats": self.processing_stats
        }
    
    def _update_stats(self, start_time: datetime, success: bool = True) -> None:
        """Update processing statistics"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.processing_stats["total_interactions"] += 1
        
        # Update average processing time
        current_avg = self.processing_stats["average_processing_time"]
        total = self.processing_stats["total_interactions"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # Update success rate
        if not success:
            current_success = self.processing_stats["success_rate"]
            self.processing_stats["success_rate"] = (
                (current_success * (total - 1) + 0) / total
            )

# Example usage
def create_base_personality() -> PersonalityTraits:
    return PersonalityTraits(
        openness=0.75,
        conscientiousness=0.8,
        extraversion=0.6,
        agreeableness=0.7,
        neuroticism=0.3
    )

def initialize_system(llm_config: dict) -> ControlRoom:
    # Create base personality
    personality = create_base_personality()
    
    # Initialize emotional agents
    emotional_agents = [
        EmotionalAgent("joy", EmotionalState.HAPPY, personality, llm_config),
        EmotionalAgent("sadness", EmotionalState.SAD, personality, llm_config),
        EmotionalAgent("anger", EmotionalState.ANGRY, personality, llm_config),
        EmotionalAgent("anxiety", EmotionalState.ANXIOUS, personality, llm_config),
        EmotionalAgent("neutral", EmotionalState.NEUTRAL, personality, llm_config)
    ]
    
    # Initialize theory agents
    theory_agents = [
        TheoryAgent(
            "social_penetration",
            "Social Penetration Theory",
            ["Relationships develop through self-disclosure",
             "Disclosure moves from shallow to deep"],
            ["Match disclosure level", "Progress gradually"],
            llm_config
        )
    ]
    
    # Create control room
    control_room = ControlRoom(emotional_agents, theory_agents)
    return control_room

