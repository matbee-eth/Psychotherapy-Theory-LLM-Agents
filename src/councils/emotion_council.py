import logging
import autogen

from datetime import datetime
from typing import Dict, List

from ..base_agents import EmotionalResponse
from ..emotions.base_emotion_agent import EmotionalAgent
from ..personality_framework import EmotionalState

class EmotionalCouncil:
    """Manages emotional agent discussions and response generation"""
    
    def __init__(self, emotional_agents: List[EmotionalAgent], llm_config: dict, persona_name: str):
        self.agents = {agent.emotion: agent for agent in emotional_agents}
        self.llm_config = llm_config
        self.persona_name = persona_name
        self.logger = logging.getLogger(__name__)
        self.current_controller = self.agents[EmotionalState.NEUTRAL]
        
        # Create user proxy to initiate discussions
        self.user_proxy = autogen.UserProxyAgent(
            name="EmotionalCouncil",
            system_message="Coordinator for emotional agent discussions",
            human_input_mode="NEVER"
        )

        # Initialize AutoGen group chat
        self.group_chat = autogen.GroupChat(
            agents=[self.user_proxy] + list(self.agents.values()),
            messages=[],
            max_round=len(self.agents),
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False
        )
        
        # Create chat manager
        self.chat_manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config,
            human_input_mode="NEVER"
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
            
            # Run group discussion using initiate_chat instead of run
            chat_result = self.user_proxy.initiate_chat(self.chat_manager, message=prompt)
            # Process and structure responses
            responses = await self._process_chat_result(chat_result, context)
            
            # Log processing
            self.logger.info(
                f"Emotional council generated {len(responses)} responses for {self.persona_name}"
            )
            
            return responses
            
        except Exception as e:
            self.logger.error(f"Error in emotional council processing: {str(e)}", exc_info=True)
            return [self._create_fallback_response()]
        
    def _create_discussion_prompt(self, message: str, context: Dict) -> str:
        """Create a prompt for the emotional agents' discussion"""
        prompt = (
            f"As emotional aspects of {self.persona_name}'s personality, discuss how to respond "
            f"to the following message while considering the current context.\n\n"
            f"Message: {message}\n"
            f"Current emotion: {self.current_controller.emotion}\n"
            "Context: " + ", ".join(f"{k}: {v}" for k, v in context.items()) + "\n\n"
            "Each agent should propose a response aligned with their emotional perspective. "
            "Consider:\n"
            "1. The emotional impact of the message\n"
            "2. How your emotional state would react\n"
            "3. An appropriate response maintaining personality consistency\n\n"
            "Provide responses in the format:\n"
            "Emotion: [your emotion]\n"
            "Response: [your suggested response]\n"
            "Confidence: [0.0-1.0 score if you are confident that your emotional response is appropriate]\n"
        )
        return prompt

    async def _process_chat_result(self, chat_result: dict, context: Dict) -> List[EmotionalResponse]:
        """Process the group chat results into structured emotional responses"""
        responses = []
        print("Emotional Council _process_chat_result:", chat_result)
        try:
            # Extract responses from chat results
            chat_messages = chat_result.chat_history  # Access the chat_history attribute directly
            
            for message in chat_messages:
                # Skip system or non-agent messages
                if not isinstance(message.get("content"), str):
                    continue
                ""
                content = message["content"]
                
                # Parse message content for emotional response components
                try:
                    # Basic parsing - could be enhanced with regex
                    emotion_line = [l for l in content.split("\n") if l.startswith("Emotion:")][0]
                    response_line = [l for l in content.split("\n") if l.startswith("Response:")][0]
                    confidence_line = [l for l in content.split("\n") if l.startswith("Confidence:")][0]
                    
                    emotion = emotion_line.split(":")[1].strip()
                    response_text = response_line.split(":")[1].strip()
                    confidence = float(confidence_line.split(":")[1].strip())
                    
                    response = EmotionalResponse(
                        content=response_text,
                        emotion=message["name"],
                        confidence=confidence,
                        influence=0.5,  # Added
                        intensity=0.5,  # Added
                        reasoning="Response generated from emotional discussion",  # Added
                        suggestions=[],  # Added
                        timestamp=datetime.now()  # Added
                    )
                    responses.append(response)
                    
                except (IndexError, ValueError) as e:
                    self.logger.warning(f"Failed to parse agent response: {str(e)}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error processing chat results: {str(e)}", exc_info=True)
            responses.append(self._create_fallback_response())
        
        return responses

    def _create_fallback_response(self) -> EmotionalResponse:
        """Create a neutral fallback response for error cases"""
        return EmotionalResponse(
            content="I'm not sure how to respond to that right now.",
            emotion=EmotionalState.NEUTRAL,
            confidence=0.5,
            influence=0.5,  # Added
            intensity=0.5,  # Added
            reasoning="Fallback response due to error",  # Added
            suggestions=[],  # Added
            timestamp=datetime.now()  # Added
        )

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
            return self.current_controller.emotion
        except Exception as e:
            self.logger.error(f"Error determining dominant emotion: {str(e)}", exc_info=True)
            return self.current_controller.emotion