import logging
import autogen

from datetime import datetime
from typing import Dict, List

from base_agents import EmotionalAgent, EmotionalResponse
from personality_framework import EmotionalState

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