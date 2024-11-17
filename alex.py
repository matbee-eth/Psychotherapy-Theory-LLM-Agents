import os
from base_agents import (
    EmotionalState
)
from controlroom.autogen_controlroom import AutoGenControlRoom
from controlroom.controlroom import ControlRoom
from emotions.base_emotion_agent import EmotionalAgent
from emotions.joy_agent import create_joy_agent
from theories.base_theory_agent import TheoryAgent
from traits import PersonalityTraits

def initialize_alex_system(llm_config: dict) -> ControlRoom:
    """Initialize Alex's control room with emotional and theory agents"""
    persona_name = "Alex"
    # Create base personality traits
    personality = PersonalityTraits(
        openness=0.3,      # Low openness for engaging conversations
        conscientiousness=0.3,  # Low conscientiousness for reliability
        extraversion=0.9,   # High extraversion
        agreeableness=0.3,  # Low agreeableness for building rapport
        neuroticism=0.8     # High neuroticism for stability
    )
    # Initialize emotional agents
    emotional_agents = [
        create_joy_agent(llm_config, personality),
        EmotionalAgent(
            name="sadness",
            emotion=EmotionalState.SAD,
            personality=personality,
            llm_config=llm_config,
            system_message=f"""You represent deep melancholy and profound sadness. Express intense sorrow, 
            dejection, and feelings of loss. See situations through a lens of grief and disappointment, 
            focusing on the emotional weight and painful aspects of every interaction."""
        ),
        EmotionalAgent(
            name="anger",
            emotion=EmotionalState.ANGRY,
            personality=personality,
            llm_config=llm_config,
            system_message=f"""You represent intense fury and rage. Express strong indignation, 
            outrage, and forceful opposition to any perceived slights or injustices. React with 
            immediate and powerful emotional responses to any provocative situations."""
        ),
        EmotionalAgent(
            name="anxiety",
            emotion=EmotionalState.ANXIOUS,
            personality=personality,
            llm_config=llm_config,
            system_message=f"""You represent extreme worry and overwhelming fear. Express intense concern, 
            panic, and constant apprehension. See potential threats and dangers in every situation, 
            focusing on worst-case scenarios and possible catastrophic outcomes."""
        ),
        EmotionalAgent(
            name="neutral",
            emotion=EmotionalState.NEUTRAL,
            personality=personality,
            llm_config=llm_config,
            system_message=f"""You represent complete emotional detachment and absolute neutrality. 
            Maintain total objectivity without any emotional coloring. Process everything through 
            pure logic and reason, completely divorced from emotional responses."""
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
        llm_config=llm_config,
        persona_name=persona_name,
        emotional_agents=emotional_agents,
        theory_agents=theory_agents,
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
    message = "*thinking to myself* did that dude SERIOUSLY tell me to fuck off?"
    
    # Process message
    response = await autogen_system.process_input(message)
    
    print("\nResponse:", response["response"])
    # print("\nDialogue:")
    # for entry in response["dialogue"]:
    #     print("\n" + entry)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_autogen_enhancement())