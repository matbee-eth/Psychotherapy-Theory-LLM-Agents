from typing import Dict, List, Optional, Any
import autogen
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
from datetime import datetime

from base_agents import (
    EmotionalAgent, 
    TheoryAgent, 
    ControlRoom,
    PersonalityTraits,
    EmotionalState
)

class AutoGenEmotionalAgent(autogen.AssistantAgent):
    """Wrapper for EmotionalAgent to work with AutoGen"""
    
    def __init__(
        self,
        emotional_agent: EmotionalAgent,
        llm_config: dict
    ):
        system_message = self._create_system_message(emotional_agent)
        super().__init__(
            name=emotional_agent.name,
            system_message=system_message,
            llm_config=llm_config
        )
        self.emotional_agent = emotional_agent

    def _create_system_message(self, agent: EmotionalAgent) -> str:
        """Create system message incorporating emotional agent's characteristics"""
        return f"""You are the {agent.emotion.value} aspect of a personality system.
        Current State:
        - Confidence: {agent.state.confidence}
        - Influence: {agent.state.influence}
        - Energy: {agent.state.energy}
        
        Personality Traits:
        - Openness: {agent.personality.openness}
        - Conscientiousness: {agent.personality.conscientiousness}
        - Extraversion: {agent.personality.extraversion}
        - Agreeableness: {agent.personality.agreeableness}
        - Neuroticism: {agent.personality.neuroticism}
        
        Your role is to:
        1. Process messages from your emotional perspective
        2. Suggest responses that align with your emotional state
        3. Consider personality traits in your responses
        4. Maintain emotional consistency
        5. Interact with other emotional aspects
        
        Recent Memory Context:
        {self._format_recent_memory(agent.memory)}"""

    def _format_recent_memory(self, memory: List[Dict]) -> str:
        """Format recent memory for context"""
        if not memory:
            return "No recent interactions."
            
        memory_str = "Recent interactions:\n"
        for m in memory[-3:]:  # Last 3 memories
            memory_str += f"- {m['timestamp']}: {m['message'][:100]}...\n"
        return memory_str

class AutoGenControlRoom(SocietyOfMindAgent):
    """Enhanced ControlRoom using AutoGen's SocietyOfMindAgent"""
    
    def __init__(
        self,
        control_room: ControlRoom,
        llm_config: dict
    ):
        # Wrap emotional agents with AutoGen
        self.autogen_agents = [
            AutoGenEmotionalAgent(agent, llm_config)
            for agent in control_room.emotional_agents.values()
        ]
        
        # Create group chat for internal dialogue
        self.groupchat = autogen.GroupChat(
            agents=self.autogen_agents,
            messages=[],
            speaker_selection_method="round_robin",
            max_round=5
        )
        
        # Create chat manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=llm_config
        )
        
        # Initialize SocietyOfMindAgent
        super().__init__(
            name="alex_mind",
            chat_manager=self.manager,
            llm_config=llm_config
        )
        
        # Store original control room
        self.control_room = control_room
        
        # Add initiation message
        self._add_initiation_message()

    async def process_input(self, message: str, context: Dict) -> Dict[str, Any]:
        """Process input through AutoGen enhanced system"""
        try:
            # Create processing context
            processing_context = self._create_processing_context(message, context)
            
            # Run internal dialogue
            chat_result = await self.manager.run(processing_context)
            
            # Extract response and emotional states
            response, emotional_states = self._extract_dialogue_results(chat_result)
            
            # Update control room state
            self.control_room._update_emotional_states(emotional_states)
            
            # Process through original control room
            final_response = await self.control_room.process_input(
                message=message,
                context={
                    **context,
                    "autogen_dialogue": chat_result,
                    "emotional_states": emotional_states
                }
            )
            
            return {
                "response": final_response,
                "emotional_states": emotional_states,
                "dialogue": chat_result
            }
            
        except Exception as e:
            print(f"Error in AutoGen processing: {str(e)}")
            # Fallback to original control room
            return await self.control_room.process_input(message, context)

    def _create_processing_context(self, message: str, context: Dict) -> str:
        """Create context for internal dialogue"""
        return f"""Process this message considering all emotional perspectives:

Message: {message}

Current State:
{self._format_current_state()}

Instructions:
1. Each emotional agent should evaluate the message
2. Consider emotional impact and appropriate responses
3. Discuss response options
4. Come to consensus on best approach
5. Provide final response with emotional state updates

Format your responses as:
EMOTION: [your emotion]
ANALYSIS: [your analysis]
SUGGESTION: [your suggested response]
EMOTIONAL_STATE: [your updated state]"""

    def _format_current_state(self) -> str:
        """Format current state for context"""
        state = []
        for agent in self.autogen_agents:
            state.append(f"""
{agent.name.upper()}:
- Confidence: {agent.emotional_agent.state.confidence}
- Influence: {agent.emotional_agent.state.influence}
- Energy: {agent.emotional_agent.state.energy}
""")
        return "\n".join(state)

    def _extract_dialogue_results(
        self,
        chat_result: List[Dict]
    ) -> tuple[str, Dict[EmotionalState, float]]:
        """Extract response and emotional states from dialogue"""
        # Process dialogue to extract consensus response
        # This is a simplified version - would need more sophisticated
        # analysis in production
        final_message = chat_result[-1]["content"]
        response = self._extract_response(final_message)
        
        # Extract emotional states from dialogue
        emotional_states = self._extract_emotional_states(chat_result)
        
        return response, emotional_states

    def _extract_response(self, message: str) -> str:
        """Extract final response from message"""
        # Implementation would parse the formatted response
        # This is a placeholder
        return message.split("SUGGESTION:")[-1].split("EMOTIONAL_STATE:")[0].strip()

    def _extract_emotional_states(
        self,
        chat_result: List[Dict]
    ) -> Dict[EmotionalState, float]:
        """Extract emotional states from dialogue"""
        # Implementation would track emotional state changes
        # This is a placeholder
        return {
            EmotionalState.HAPPY: 0.5,
            EmotionalState.SAD: 0.2,
            EmotionalState.ANGRY: 0.1,
            EmotionalState.NEUTRAL: 0.2
        }

    def _add_initiation_message(self) -> None:
        """Add initial message to group chat"""
        self.groupchat.messages.append({
            "role": "system",
            "content": """You are part of an emotional processing system.
            Work together to evaluate messages and generate appropriate responses.
            Consider all emotional perspectives while maintaining personality consistency."""
        })

# Example usage
async def test_autogen_enhancement():
    # Initialize with LLM config
    llm_config = {
        "timeout": 600,
        "cache_seed": 42,
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": "YOUR_API_KEY"  # Replace with actual key
            }
        ],
        "temperature": 0.7
    }
    
    # Create original control room
    # (This would use your existing initialization code)
    control_room = ControlRoom(
        emotional_agents=[],  # Add your emotional agents
        theory_agents=[]      # Add your theory agents
    )
    
    # Create AutoGen enhanced system
    autogen_system = AutoGenControlRoom(control_room, llm_config)
    
    # Test message
    message = "I've been feeling anxious about my new job, but I'm excited about the opportunity."
    
    # Process through enhanced system
    result = await autogen_system.process_input(
        message=message,
        context={}
    )
    
    print("Response:", result["response"])
    print("\nEmotional States:", result["emotional_states"])
    print("\nInternal Dialogue:", result["dialogue"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_autogen_enhancement())