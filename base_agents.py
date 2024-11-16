from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional
import autogen
from datetime import datetime

from councils.theory_council import TheoryCouncil
from personality_framework import EmotionalState
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
    """Final processed response with metadata"""
    content: str
    dominant_emotion: EmotionalState
    controlling_emotion: EmotionalState  # Current controller's emotion
    emotional_states: Dict[EmotionalState, float]
    theory_scores: Dict[str, float]
    confidence: float
    processing_time: float
    context: Dict[str, Any]

class EmotionalAgent(autogen.AssistantAgent):
    """Base class for emotion-driven agents"""
    
    def __init__(
        self,
        name: str,
        emotion: EmotionalState,
        personality: PersonalityTraits,
        llm_config: dict,
        system_message: Optional[str] = None
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )
        self.emotion = emotion
        self.personality = personality
        self.state = AgentState(
            emotional_state=emotion,
            confidence=0.5,
            influence=0.5,
            energy=1.0,
            last_active=datetime.now()
        )
        self.memory = []  # List of recent interactions
        
    async def process_message(self, message: str, context: Dict) -> str:
        """Process incoming message based on emotional state"""
        # Update state based on message content
        self._update_state(message)
        
        # Generate response using LLM with emotional context
        response = await self._generate_response(message, context)
        
        # Update memory
        self._update_memory(message, response)
        
        return response
    
    def _update_state(self, message: str) -> None:
        """Update agent's internal state based on message"""
        # Implementation will vary by emotion
        pass
    
    async def _generate_response(self, message: str, context: Dict) -> str:
        """Generate emotionally-appropriate response"""
        # Implementation will vary by emotion
        pass
    
    def _update_memory(self, message: str, response: str) -> None:
        """Update agent's memory with interaction"""
        self.memory.append({
            "timestamp": datetime.now(),
            "message": message,
            "response": response,
            "state": self.state
        })
        # Keep only recent memory (last 10 interactions)
        if len(self.memory) > 10:
            self.memory.pop(0)

from typing import Dict, List, Optional, Any
import json
import autogen
from datetime import datetime

class TheoryAgent(autogen.AssistantAgent):
    """Base class for psychological theory agents with AutoGen integration"""
    
    def __init__(
        self,
        name: str,
        theory_name: str,
        principles: List[str],
        guidelines: List[str],
        llm_config: dict
    ):
        # Create theory-specific system message
        system_message = self._create_system_message(
            theory_name,
            principles,
            guidelines
        )
        
        # Initialize AutoGen assistant
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )
        
        self.theory_name = theory_name
        self.principles = principles
        self.guidelines = guidelines
        
        # Initialize timestamp
        self.last_analysis = datetime.now()
    
    def _create_system_message(
        self,
        theory_name: str,
        principles: List[str],
        guidelines: List[str]
    ) -> str:
        """Create the system message for this theory agent"""
        principles_str = "\n".join(f"- {p}" for p in principles)
        guidelines_str = "\n".join(f"- {g}" for g in guidelines)
        
        return f"""You are an expert in {theory_name}, analyzing interactions and guiding responses.

Key Principles:
{principles_str}

Guidelines:
{guidelines_str}

Your role is to:
1. Analyze messages through the lens of {theory_name}
2. Evaluate response alignment with theoretical principles
3. Suggest improvements based on theory
4. Consider relationship development
5. Monitor theory compliance

Always structure your responses as JSON with:
{{
    "analysis": {{
        "alignment_score": <float 0-1>,
        "theory_principles": [<list of relevant principles>],
        "guidelines_applied": [<list of relevant guidelines>],
        "concerns": [<list of theoretical concerns>],
        "suggestions": [<list of theory-based improvements>]
    }},
    "rationale": <explanation of analysis>,
    "intervention": {{
        "needed": <boolean>,
        "type": <string>,
        "suggestions": [<list of interventions>]
    }},
    "relationship": {{
        "current_stage": <string>,
        "development_path": <string>,
        "next_actions": [<list of recommended actions>]
    }}
}}"""

    async def analyze_message(
        self, 
        message: str,
        response: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """Analyze a message/response pair through theoretical lens"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(message, response, context)
            
            # Get analysis using AutoGen's chat completion
            result = await self.generate_response(prompt)
            
            try:
                # Parse JSON response
                analysis = json.loads(result)
                self.last_analysis = datetime.now()
                return analysis
                
            except json.JSONDecodeError:
                return self._create_fallback_analysis()
                
        except Exception as e:
            print(f"Error in theory analysis: {str(e)}")
            return self._create_fallback_analysis()
    
    def _create_analysis_prompt(
        self,
        message: str,
        response: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Create prompt for theoretical analysis"""
        # Base message context
        prompt = f"""Analyze this interaction using {self.theory_name}:

MESSAGE: {message}"""

        # Add response if provided
        if response:
            prompt += f"\n\nRESPONSE: {response}"
            
        # Add context if provided
        if context:
            prompt += f"\n\nCONTEXT: {json.dumps(context, indent=2)}"
            
        prompt += """

Consider:
1. How well does this align with theoretical principles?
2. What theory-specific patterns are present?
3. What interventions might be needed?
4. How does this affect relationship development?

Provide analysis in the specified JSON format."""

        return prompt
    
    def _create_fallback_analysis(self) -> Dict:
        """Create a safe fallback analysis"""
        return {
            "analysis": {
                "alignment_score": 0.5,
                "theory_principles": [self.principles[0]],
                "guidelines_applied": [self.guidelines[0]],
                "concerns": ["Unable to perform complete analysis"],
                "suggestions": ["Consider reviewing interaction"]
            },
            "rationale": "Fallback analysis due to processing error",
            "intervention": {
                "needed": False,
                "type": "none",
                "suggestions": []
            },
            "relationship": {
                "current_stage": "unknown",
                "development_path": "maintain",
                "next_actions": ["Continue normal interaction"]
            }
        }
    
    async def evaluate_response(
        self,
        message: str,
        proposed_response: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Evaluate if a proposed response aligns with theory"""
        analysis = await self.analyze_message(
            message,
            proposed_response,
            context
        )
        
        return {
            "theory_name": self.theory_name,
            "alignment_score": analysis["analysis"]["alignment_score"],
            "suggestions": analysis["analysis"]["suggestions"],
            "concerns": analysis["analysis"]["concerns"],
            "rationale": analysis["rationale"]
        }
    
class EmotionalCouncil:
    """Manages emotional agent discussions and response generation"""
    
    def __init__(self, emotional_agents: List[EmotionalAgent], llm_config: dict, persona_name: str):
        self.agents = {agent.emotion: agent for agent in emotional_agents}
        self.llm_config = llm_config
        self.persona_name = persona_name
        self.logger = logging.getLogger(__name__)
        self.current_controller = self.agents[EmotionalState.NEUTRAL]
        
        # Initialize AutoGen group chat
        self.group_chat = autogen.GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=len(self.agents),
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False
        )
        
        # Create chat manager
        self.chat_manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config
        )
    
    async def transfer_control(self, new_emotion: EmotionalState) -> None:
        """Transfer control to a different emotional agent"""
        if new_emotion not in self.agents:
            self.logger.warning(
                f"Emotion {new_emotion} not found in agents. Defaulting to NEUTRAL"
            )
            new_emotion = EmotionalState.NEUTRAL
            
        if self.current_controller:
            # Decrease influence of previous controller
            self.current_controller.state.influence *= 0.8
            
        self.current_controller = self.agents[new_emotion]
        self.current_controller.state.influence = 1.0
        self.current_controller.state.last_active = datetime.now()
        
        self.logger.info(
            f"Control transferred to {new_emotion} agent for {self.persona_name}"
        )
    
    async def process(self, message: str, context: Dict) -> List[EmotionalResponse]:
        """Generate emotional responses through group discussion"""
        try:
            # Determine dominant emotion
            dominant_emotion = await self._determine_dominant_emotion(message, context)
            
            # Transfer control if needed
            if dominant_emotion != self.current_controller.emotion:
                await self.transfer_control(dominant_emotion)
            
            # Create discussion prompt
            prompt = self._create_discussion_prompt(message, context)
            
            # Run group discussion
            chat_result = await self.chat_manager.run(prompt)
            
            # Process and structure responses
            responses = await self._process_chat_result(chat_result, context)
            
            # Log processing
            self.logger.info(
                f"Emotional council generated {len(responses)} responses for {self.persona_name}"
            )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error in emotional council processing: {str(e)}")
            return [self._create_fallback_response()]
    
    async def _determine_dominant_emotion(
        self,
        message: str,
        context: Dict
    ) -> EmotionalState:
        """Determine which emotion should handle the message"""
        try:
            # This would be replaced with actual emotion detection logic
            # For now, maintaining current controller with some probability
            if self.current_controller.state.confidence > 0.7:
                return self.current_controller.emotion
            return EmotionalState.NEUTRAL
        except Exception as e:
            self.logger.error(f"Error determining dominant emotion: {str(e)}")
            return EmotionalState.NEUTRAL

class ResponseSynthesizer:
    """Synthesizes emotional responses and theory validations"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.logger = logging.getLogger(__name__)
    
    async def create_response(
        self,
        message: str,
        emotional_responses: List[EmotionalResponse],
        theory_validations: List[TheoryValidation],
        context: Dict
    ) -> ProcessedResponse:
        """Create final response combining emotions and theories"""
        try:
            # Score responses against validations
            scored_responses = self._score_responses(
                emotional_responses,
                theory_validations
            )
            
            # Select best response
            selected_response = self._select_response(scored_responses)
            
            # Apply theory modifications
            modified_response = self._apply_theory_modifications(
                selected_response,
                theory_validations
            )
            
            # Create processed response
            return ProcessedResponse(
                content=modified_response,
                dominant_emotion=self._determine_dominant_emotion(
                    emotional_responses
                ),
                emotional_states=self._calculate_emotional_states(
                    emotional_responses
                ),
                theory_scores=self._calculate_theory_scores(
                    theory_validations
                ),
                confidence=self._calculate_confidence(
                    scored_responses,
                    theory_validations
                ),
                processing_time=context.get("processing_time", 0.0),
                context=context
            )
            
        except Exception as e:
            self.logger.error(f"Error in response synthesis: {str(e)}")
            return self._create_fallback_processed_response()

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