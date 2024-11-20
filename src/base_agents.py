import json
import logging
import autogen

from dataclasses import dataclass
from typing import Any, Dict, List
from datetime import datetime

from .personality_framework import EmotionalState

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
```json
{
    "selected_content": str,  # The chosen/modified response
    "dominant_emotion": str,  # Main emotional influence
    "confidence": float,      # 0-1 synthesis confidence
    "modifications": [str],   # List of modifications made
    "rationale": str,        # Explanation of decisions
    "emotional_weights": {},  # Emotion name to weight mapping
    "theory_scores": {}      # Theory name to score mapping
}
```"""
    
    async def create_response(
        self,
        message: str,
        sender: autogen.AssistantAgent,
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
            synthesis = await self._get_synthesis(sender, prompt)
            
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
            self.logger.error(f"Error in response synthesis: {str(e)}", exc_info=True)  # Add exc_info=True
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
                "emotion": response.emotion,
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
{json.dumps(context, indent=2, default=str)}
```

Create a response that:
1. Maintains emotional authenticity
2. Follows theoretical guidelines
3. Fits the relationship context
4. Flows naturally
5. Achieves communication goals

Provide your synthesis in the specified JSON format."""
    
    async def _get_synthesis(self, sender: autogen.AssistantAgent, prompt: str) -> Dict:
        """Get synthesis from LLM"""
        try:
            # Get response using receive
            response = self.receive(
                message={"role": "user", "content": prompt, "name": sender.name},
                sender=sender
            )
            print(response)
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
            self.logger.error(f"Error getting synthesis: {str(e)}", exc_info=True)
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

