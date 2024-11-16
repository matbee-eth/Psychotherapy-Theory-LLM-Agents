from dataclasses import dataclass
import re
from typing import Dict, List, Optional
from enum import Enum
import autogen
from datetime import datetime

class EmotionalState(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    CONTENT = "content"

@dataclass
class PersonalityTraits:
    openness: float  # 0-1
    conscientiousness: float  # 0-1
    extraversion: float  # 0-1
    agreeableness: float  # 0-1
    neuroticism: float  # 0-1

@dataclass
class AgentState:
    emotional_state: EmotionalState
    confidence: float  # 0-1
    influence: float  # 0-1
    energy: float  # 0-1
    last_active: datetime

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

class TheoryAgent(autogen.AssistantAgent):
    """Base class for psychological theory agents"""
    
    def __init__(
        self,
        name: str,
        theory_name: str,
        principles: List[str],
        guidelines: List[str],
        llm_config: dict
    ):
        system_message = self._create_system_message(theory_name, principles, guidelines)
        super().__init__(
            name=name,
            llm_config=llm_config,
            system_message=system_message
        )
        self.theory_name = theory_name
        self.principles = principles
        self.guidelines = guidelines
        
    def _create_system_message(
        self,
        theory_name: str,
        principles: List[str],
        guidelines: List[str]
    ) -> str:
        """Create the system message for this theory agent"""
        principles_str = "\n".join(f"- {p}" for p in principles)
        guidelines_str = "\n".join(f"- {g}" for g in guidelines)
        
        return f"""You are an expert in {theory_name} guiding conversational responses.

Key Principles:
{principles_str}

Guidelines:
{guidelines_str}

Your role is to:
1. Evaluate messages and responses
2. Ensure alignment with theoretical principles
3. Suggest improvements when needed
4. Maintain theoretical consistency
5. Guide relationship development

Always respond in valid JSON format with the following structure:
{{
    "score": <float between 0 and 1>,
    "suggestions": [<list of specific improvements>],
    "rationale": <theoretical justification>
}}"""
    
    async def evaluate_response(self, message: str, proposed_response: str) -> Dict:
        """Evaluate if response aligns with psychological theory"""
        try:
            # Get analysis from _analyze_alignment
            evaluation = await self._analyze_alignment(message, proposed_response)
            
            if evaluation is None:
                # Return default evaluation if analysis fails
                return {
                    "theory_name": self.theory_name,
                    "alignment_score": 0.7,  # Default moderate alignment
                    "suggestions": ["Consider reviewing response for theoretical alignment"],
                }
            
            return {
                "theory_name": self.theory_name,
                "alignment_score": evaluation.get("score", 0.7),
                "suggestions": evaluation.get("suggestions", [])
            }
            
        except Exception as e:
            print(f"Error in theory evaluation: {str(e)}")
            return {
                "theory_name": self.theory_name,
                "alignment_score": 0.7,  # Default moderate alignment
                "suggestions": ["Error in theoretical analysis"]
            }
        
    async def _analyze_alignment(self, message: str, response: str) -> Dict:
        """Analyze how well response aligns with theory"""
        try:
            analysis_prompt = f"""Analyze this interaction using {self.theory_name}:

USER MESSAGE: {message}
PROPOSED RESPONSE: {response}

Consider:
1. How well does the response align with theoretical principles?
2. What aspects could be improved?
3. Are there any risks or concerns?
4. What opportunities exist for relationship development?

Respond in JSON format with:
{{
    "score": <float between 0 and 1>,
    "suggestions": [<list of specific improvements>],
    "rationale": <theoretical justification>
}}"""

            # Create a chat message
             # Use autogen's chat completion directly
            messages = [{
                "role": "user",
                "content": analysis_prompt
            }]
            
            # Get completion from the configured LLM
            response = self.client.create(
                context=messages[-1]["content"],
                messages=messages
            )
            
            try:
                # Try to parse as JSON
                import json
                # Get the content from the response
                response_content = response.choices[0].message.content
                analysis = json.loads(response_content)
                
                return {
                    "score": min(1.0, max(0.0, float(analysis.get("score", 0.7)))),
                    "suggestions": analysis.get("suggestions", []),
                    "rationale": analysis.get("rationale", "")
                }

            except json.JSONDecodeError:
                # If JSON parsing fails, extract score and create basic analysis
                response_text = response.message.content if hasattr(response, 'message') else response.content
                # Look for score in the response
                score_match = re.search(r"score:\s*(0\.\d+|1\.0)", response_text)
                score = float(score_match.group(1)) if score_match else 0.7
                
                return {
                    "score": score,
                    "suggestions": ["Response format error - using basic analysis"],
                    "rationale": "Basic alignment analysis due to parsing error"
                }
                
        except Exception as e:
            import traceback
            print(f"Error in alignment analysis: {str(e)}")
            print("Stack trace:") 
            print(traceback.format_exc())
            return {
                "score": 0.7,  # Default moderate alignment
                "suggestions": ["Error occurred during analysis"],
                "rationale": "Analysis error fallback"
            }

class ControlRoom:
    """Manages emotional agents and coordinates responses"""
    
    def __init__(self, emotional_agents: List[EmotionalAgent], theory_agents: List[TheoryAgent]):
        # Convert list to dictionary with enum keys
        self.emotional_agents = {agent.emotion: agent for agent in emotional_agents}
        self.theory_agents = {agent.theory_name: agent for agent in theory_agents}
        self.current_controller = self.emotional_agents[EmotionalState.NEUTRAL]

        self.state_history = []
        
    async def process_input(self, message: str, context: Dict) -> str:
        """Process input through emotional agents and generate response"""
        print("ControlRoom process_input", message)
        # Analyze message to determine appropriate emotional response
        dominant_emotion = await self._determine_dominant_emotion(message)
        
        if dominant_emotion is None:
            # Default to neutral if no dominant emotion determined
            dominant_emotion = EmotionalState.NEUTRAL
            
        # Ensure we have a valid emotion that exists in our agents
        if dominant_emotion not in self.emotional_agents:
            dominant_emotion = EmotionalState.NEUTRAL
        
        # Transfer control if needed
        if self.current_controller is None or dominant_emotion != self.current_controller.emotion:
            await self._transfer_control(dominant_emotion)
        
        # Generate response from current controller
        response = await self.current_controller.process_message(message, context)
        
        # Validate response with theory agents
        validated_response = await self._validate_response(message, response)
        
        # Update state history
        self._update_history(message, validated_response, dominant_emotion)
        
        return validated_response
    
    async def _determine_dominant_emotion(self, message: str) -> Optional[EmotionalState]:
        """Determine which emotion should handle the message"""
        try:
            # Simple emotion detection for now - should be enhanced with proper NLP
            # Returns NEUTRAL by default
            return EmotionalState.NEUTRAL
        except Exception as e:
            print(f"Error determining dominant emotion: {str(e)}")
            return EmotionalState.NEUTRAL
    
    async def _transfer_control(self, new_emotion: EmotionalState) -> None:
        """Transfer control to a different emotional agent"""
        if new_emotion not in self.emotional_agents:
            print(f"Warning: Emotion {new_emotion} not found in agents. Defaulting to NEUTRAL")
            new_emotion = EmotionalState.NEUTRAL
            
        if self.current_controller:
            self.current_controller.state.influence *= 0.8  # Decrease influence of previous controller
            
        self.current_controller = self.emotional_agents[new_emotion]
        self.current_controller.state.influence = 1.0
        self.current_controller.state.last_active = datetime.now()

    def _update_emotional_states(self, emotional_states: Dict[EmotionalState, float]) -> None:
        """Update emotional states of agents"""
        for emotion, influence in emotional_states.items():
            if emotion in self.emotional_agents:
                self.emotional_agents[emotion].state.influence = influence

    async def _validate_response(self, message: str, response: str) -> str:
        """Validate response against psychological theories"""
        try:
            evaluations = []
            for theory_agent in self.theory_agents.values():
                evaluation = await theory_agent.evaluate_response(message, response)
                if evaluation:  # Only add valid evaluations
                    evaluations.append(evaluation)
            
            # If no valid evaluations, return original response
            if not evaluations:
                return response
                
            # Check if any evaluation scores are low
            if any(eval.get("alignment_score", 1.0) < 0.5 for eval in evaluations):
                # For now, just log the suggestions
                print("Theory suggestions:", [
                    sugg for eval in evaluations 
                    for sugg in eval.get("suggestions", [])
                ])
                # Could implement response adjustment logic here
                
            return response

        except Exception as e:
            import traceback
            print(f"Error validating response: {str(e)}")
            print("Stack trace:") 
            print(traceback.format_exc())
            return response  # Return original response if validation fails
    
    def _update_history(self, message: str, response: str, emotion: EmotionalState) -> None:
        """Update control room history"""
        try:
            self.state_history.append({
                "timestamp": datetime.now(),
                "message": message,
                "response": response,
                "controlling_emotion": emotion,
                "emotional_states": {
                    e: agent.state for e, agent in self.emotional_agents.items()
                }
            })
        except Exception as e:
            print(f"Error updating history: {str(e)}")

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