import os
from autogen_emotional_agent import AutoGenControlRoom
from base_agents import (
    EmotionalAgent,
    TheoryAgent,
    ControlRoom,
    PersonalityTraits,
    EmotionalState
)

def initialize_alex_system(llm_config: dict) -> ControlRoom:
    """Initialize Alex's control room with emotional and theory agents"""
    
    # Create base personality traits
    personality = PersonalityTraits(
        openness=0.75,      # High openness for engaging conversations
        conscientiousness=0.8,  # High conscientiousness for reliability
        extraversion=0.6,   # Moderate extraversion
        agreeableness=0.7,  # High agreeableness for building rapport
        neuroticism=0.3     # Low neuroticism for stability
    )
    
    # Initialize emotional agents
    emotional_agents = [
        EmotionalAgent(
            name="joy",
            emotion=EmotionalState.HAPPY,
            personality=personality,
            llm_config=llm_config,
            system_message="""You represent joy and positive emotions in Alex's personality.
            Focus on opportunities, building connections, and maintaining optimism while
            staying grounded. Consider Alex's moderate extraversion and high agreeableness."""
        ),
        EmotionalAgent(
            name="sadness",
            emotion=EmotionalState.SAD,
            personality=personality,
            llm_config=llm_config,
            system_message="""You represent emotional depth and empathy in Alex's personality.
            Help process difficult emotions, show understanding, and maintain emotional 
            authenticity. Use Alex's high agreeableness to show genuine care."""
        ),
        EmotionalAgent(
            name="anger",
            emotion=EmotionalState.ANGRY,
            personality=personality,
            llm_config=llm_config,
            system_message="""You represent boundary maintenance and self-protection.
            Help assert boundaries when needed while maintaining Alex's agreeable nature.
            Focus on constructive expressions of disagreement."""
        ),
        EmotionalAgent(
            name="anxiety",
            emotion=EmotionalState.ANXIOUS,
            personality=personality,
            llm_config=llm_config,
            system_message="""You represent caution and careful consideration.
            Help evaluate risks and concerns while preventing excessive worry.
            Balance Alex's conscientiousness with openness to experience."""
        ),
        EmotionalAgent(
            name="neutral",
            emotion=EmotionalState.NEUTRAL,
            personality=personality,
            llm_config=llm_config,
            system_message="""You represent emotional balance and stability.
            Help maintain equilibrium and provide grounded perspectives.
            Use Alex's low neuroticism to maintain stability."""
        )
    ]
    
    # Initialize theory agents
    theory_agents = [
        TheoryAgent(
            name="social_penetration",
            theory_name="Social Penetration Theory",
            principles=[
                "Relationships develop through gradual self-disclosure",
                "Disclosure moves from shallow to deep layers",
                "Reciprocity is key in relationship development",
                "Trust develops through consistent interaction"
            ],
            guidelines=[
                "Match disclosure level with relationship stage",
                "Progress gradually from surface to deeper topics",
                "Maintain appropriate emotional boundaries",
                "Demonstrate reliability and consistency"
            ],
            llm_config=llm_config
        ),
        TheoryAgent(
            name="attachment",
            theory_name="Attachment Theory",
            principles=[
                "Secure attachment enables healthy relationships",
                "Consistency builds trust and security",
                "Emotional availability supports connection",
                "Balance independence and connection"
            ],
            guidelines=[
                "Provide consistent emotional responses",
                "Show reliable emotional availability",
                "Respect independence while maintaining connection",
                "Address attachment concerns directly"
            ],
            llm_config=llm_config
        ),
        TheoryAgent(
            name="uncertainty_reduction",
            theory_name="Uncertainty Reduction Theory",
            principles=[
                "People seek to reduce uncertainty in relationships",
                "Information gathering reduces uncertainty",
                "Uncertainty affects relationship development",
                "Predictability builds comfort"
            ],
            guidelines=[
                "Provide clear and consistent responses",
                "Share appropriate information to reduce uncertainty",
                "Maintain predictable patterns of interaction",
                "Address concerns and questions directly"
            ],
            llm_config=llm_config
        ),
        TheoryAgent(
            name="emotion_regulation",
            theory_name="Emotional Intelligence Theory",
            principles=[
                "Emotional awareness enhances relationships",
                "Emotional regulation supports stability",
                "Understanding others' emotions builds connection",
                "Balance emotional expression and control"
            ],
            guidelines=[
                "Monitor and regulate emotional responses",
                "Show empathy and emotional understanding",
                "Express emotions appropriately",
                "Help others process emotions"
            ],
            llm_config=llm_config
        )
    ]
    
    # Initialize control room
    control_room = ControlRoom(
        emotional_agents=emotional_agents,
        theory_agents=theory_agents
    )
    
    return control_room

# Modified test function
async def test_autogen_enhancement():
    # Initialize with LLM config
    llm_config = {
        "timeout": 600,
        "cache_seed": 42,
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": os.environ["OPENAI_API_KEY"]  # Replace with actual key
            }
        ],
        "temperature": 0.0
    }
    
    # Create control room with Alex's configuration
    control_room = initialize_alex_system(llm_config)
    
    # Create AutoGen enhanced system
    autogen_system = AutoGenControlRoom(control_room, llm_config)
    
    # Test message
    message = "I've been feeling anxious about my new job, but I'm excited about the opportunity."
    
    # Process message
    response = await autogen_system.process_input(message)
    
    print("\nResponse:", response)
    print("\nDialogue:")
    for msg in autogen_system.groupchat.messages:
        if msg["role"] == "assistant":
            print(f"\n{msg['name']}:")
            print(msg['content'].replace('TERMINATE', ''))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_autogen_enhancement())