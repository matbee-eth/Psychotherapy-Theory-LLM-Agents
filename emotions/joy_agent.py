from base_agents import EmotionalAgent, EmotionalState
from personality_framework import PersonalityTraits

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