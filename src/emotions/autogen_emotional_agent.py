import autogen

from typing import Dict, List

from emotions.base_emotion_agent import EmotionalAgent
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
