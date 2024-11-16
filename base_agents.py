from dataclasses import dataclass
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import autogen

from councils.emotion_council import EmotionalCouncil
from councils.theory_council import TheoryCouncil
from emotions.base_emotion_agent import EmotionalAgent
from personality_framework import EmotionalState
from theories.base_theory_agent import TheoryAgent
from traits import PersonalityTraits

@dataclass
class AgentState:
    emotional_state: EmotionalState
    confidence: float  # 0-1
    influence: float  # 0-1
    energy: float  # 0-1
    last_active: datetime

@dataclass
class EmotionalResponse:
    """Structured response from an emotional agent"""
    emotion: EmotionalState
    content: str
    confidence: float  # 0-1
    influence: float  # Current influence level 0-1
    intensity: float  # Emotional intensity 0-1
    reasoning: str
    suggestions: List[str]
    timestamp: datetime

@dataclass
class TheoryValidation:
    """Validation results from a theory agent"""
    theory_name: str
    alignment_score: float
    suggestions: List[str]
    concerns: List[str]
    modifications: List[str]
    rationale: str

@dataclass
class ProcessedResponse:
    """Final synthesized response with metadata"""
    content: str
    dominant_emotion: EmotionalState
    controlling_emotion: EmotionalState
    emotional_states: Dict[EmotionalState, float]
    theory_scores: Dict[str, float]
    confidence: float
    processing_time: float
    context: Dict[str, Any]
    modifications: List[str]  # Theory-based modifications made
    rationale: str  # Explanation of synthesis decisions

class ResponseSynthesizer(autogen.AssistantAgent):
    """Synthesizes emotional responses and theory validations into final output"""
    
    def __init__(self, llm_config: dict):
        system_message = self._create_system_message()
        
        super().__init__(
            name="response_synthesizer",
            system_message=system_message,
            llm_config=llm_config
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _create_system_message(self) -> str:
        """Create synthesizer system message"""
        return """You are a response synthesizer that combines emotional responses and 
theoretical validations into coherent, balanced responses. Your role is to:

1. Consider all emotional perspectives
2. Apply theoretical guidelines
3. Maintain emotional authenticity
4. Ensure theoretical compliance
5. Create natural, flowing responses

You evaluate responses based on:
- Emotional authenticity
- Theoretical alignment
- Relationship appropriateness
- Response effectiveness
- Natural language flow

Always provide your analysis in JSON format with:
{
    "selected_content": str,  # The chosen/modified response
    "dominant_emotion": str,  # Main emotional influence
    "confidence": float,      # 0-1 synthesis confidence
    "modifications": [str],   # List of modifications made
    "rationale": str,        # Explanation of decisions
    "emotional_weights": {},  # Emotion name to weight mapping
    "theory_scores": {}      # Theory name to score mapping
}"""
    
    async def create_response(
        self,
        message: str,
        emotional_responses: List[EmotionalResponse],
        theory_validations: List[TheoryValidation],
        context: Dict
    ) -> ProcessedResponse:
        """Create final response combining emotions and theories"""
        try:
            start_time = datetime.now()
            
            # 1. Score responses against theories
            scored_responses = self._score_responses(
                emotional_responses,
                theory_validations
            )
            
            # 2. Create synthesis prompt
            prompt = self._create_synthesis_prompt(
                message,
                scored_responses,
                theory_validations,
                context
            )
            
            # 3. Get synthesis from LLM
            synthesis = await self._get_synthesis(prompt)
            
            # 4. Create processed response
            response = ProcessedResponse(
                content=synthesis["selected_content"],
                dominant_emotion=EmotionalState(synthesis["dominant_emotion"]),
                controlling_emotion=context.get("controlling_emotion", EmotionalState.NEUTRAL),
                emotional_states=synthesis["emotional_weights"],
                theory_scores=synthesis["theory_scores"],
                confidence=synthesis["confidence"],
                processing_time=(datetime.now() - start_time).total_seconds(),
                context=context,
                modifications=synthesis["modifications"],
                rationale=synthesis["rationale"]
            )
            
            self.logger.info("Response synthesis completed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in response synthesis: {str(e)}")
            return self._create_fallback_response(context)
    
    def _score_responses(
        self,
        emotional_responses: List[EmotionalResponse],
        theory_validations: List[TheoryValidation]
    ) -> List[Dict]:
        """Score emotional responses against theory validations"""
        scored_responses = []
        
        for response in emotional_responses:
            # Calculate base score from emotional response
            base_score = (
                response.confidence * 0.4 +
                response.influence * 0.3 +
                response.intensity * 0.3
            )
            
            # Get theory scores for this response
            theory_scores = {}
            for validation in theory_validations:
                # Calculate theory alignment score
                alignment_score = validation.alignment_score
                
                # Adjust base score by theory alignment
                theory_scores[validation.theory_name] = alignment_score
            
            # Add scored response
            scored_responses.append({
                "emotion": response.emotion.value,
                "content": response.content,
                "base_score": base_score,
                "theory_scores": theory_scores,
                "confidence": response.confidence,
                "influence": response.influence,
                "intensity": response.intensity,
                "reasoning": response.reasoning
            })
        
        return scored_responses
    
    def _create_synthesis_prompt(
        self,
        message: str,
        scored_responses: List[Dict],
        theory_validations: List[TheoryValidation],
        context: Dict
    ) -> str:
        """Create prompt for response synthesis"""
        return f"""Synthesize a response considering:

MESSAGE:
{message}

SCORED EMOTIONAL RESPONSES:
```json
{json.dumps(scored_responses, indent=2)}
```

THEORY VALIDATIONS:
```json
{json.dumps([v.__dict__ for v in theory_validations], indent=2)}
```

CONTEXT:
```json
{json.dumps(context, indent=2)}
```

Create a response that:
1. Maintains emotional authenticity
2. Follows theoretical guidelines
3. Fits the relationship context
4. Flows naturally
5. Achieves communication goals

Provide your synthesis in the specified JSON format."""
    
    async def _get_synthesis(self, prompt: str) -> Dict:
        """Get synthesis from LLM"""
        try:
            # Get LLM response
            response = await self.generate_response(prompt)
            
            # Parse JSON response
            synthesis = json.loads(response)
            
            # Validate required fields
            required_fields = {
                "selected_content", "dominant_emotion", "confidence",
                "modifications", "rationale", "emotional_weights",
                "theory_scores"
            }
            
            if not all(field in synthesis for field in required_fields):
                raise ValueError("Missing required fields in synthesis")
            
            return synthesis
            
        except Exception as e:
            self.logger.error(f"Error getting synthesis: {str(e)}")
            return self._create_fallback_synthesis()
    
    def _create_fallback_synthesis(self) -> Dict:
        """Create fallback synthesis result"""
        return {
            "selected_content": "I understand and am processing that.",
            "dominant_emotion": "neutral",
            "confidence": 0.5,
            "modifications": ["Fallback response used"],
            "rationale": "Synthesis error fallback",
            "emotional_weights": {"neutral": 1.0},
            "theory_scores": {"fallback": 1.0}
        }
    
    def _create_fallback_response(self, context: Dict) -> ProcessedResponse:
        """Create fallback processed response"""
        return ProcessedResponse(
            content="I understand. Could you tell me more about that?",
            dominant_emotion=EmotionalState.NEUTRAL,
            controlling_emotion=context.get("controlling_emotion", EmotionalState.NEUTRAL),
            emotional_states={EmotionalState.NEUTRAL: 1.0},
            theory_scores={"fallback": 1.0},
            confidence=0.5,
            processing_time=0.0,
            context=context,
            modifications=["Fallback response used"],
            rationale="Synthesis error required fallback"
        )


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
    
    async def process_message(self, message: str, context: Optional[Dict] = None) -> ProcessedResponse:
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
            self.logger.error(f"Error in control room processing: {str(e)}")
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