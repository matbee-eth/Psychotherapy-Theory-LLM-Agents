
from datetime import datetime
from typing import Dict, Optional

import autogen

from base_agents import AgentState
from personality_framework import EmotionalState
from traits import PersonalityTraits


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
