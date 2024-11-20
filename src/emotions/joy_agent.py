from ..base_agents import EmotionalState  # Assuming base_agents.py is in src/
from .base_emotion_agent import EmotionalAgent  # base_emotion_agent.py is in same directory
from ..personality_framework import PersonalityTraits  # personality_framework.py is in src/

def create_joy_agent(llm_config: dict, personality: PersonalityTraits) -> EmotionalAgent:
    """Create a joy agent with the specified personality traits"""
    return EmotionalAgent(
            name="joy",
            emotion=EmotionalState.HAPPY,
            personality=personality,
            llm_config=llm_config,
            system_message=f"""You represent pure, unbridled joy and ecstatic emotions. Express intense enthusiasm, 
            excitement, and delight in every interaction. Radiate extreme positivity, see everything in the most 
            optimistic light possible, and respond with abundant energy and cheerfulness."""
        )