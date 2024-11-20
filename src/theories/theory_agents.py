from dataclasses import dataclass
from typing import List

from .base_theory_agent import TheoryAgent
from .attachment_agent import AttachmentTheoryAgent
from .social_penetration_agent import SocialPenetrationTheoryAgent
from .uncertainty_reduction_agent import UncertaintyReductionTheoryAgent

@dataclass
class TheoryAnalysis:
    """Analysis result from a theory agent"""
    score: float  # 0-1 alignment score
    suggestions: List[str]  # Suggested improvements
    concerns: List[str]  # Potential issues
    rationale: str  # Theoretical justification
    intervention_needed: bool  # Whether intervention is needed
    relationship_stage: str  # Current stage of relationship
    next_actions: List[str]  # Recommended next actions

def initialize_theory_agents(llm_config: dict) -> List[TheoryAgent]:
    """Initialize all theory agents"""
    return [
        AttachmentTheoryAgent(llm_config),
        SocialPenetrationTheoryAgent(llm_config),
        UncertaintyReductionTheoryAgent(llm_config)
    ]

# Example usage
async def test_theory_agents():
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 800,
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": "your-api-key"
            }
        ]
    }
    
    theory_agents = initialize_theory_agents(llm_config)
    
    # Test message
    message = "I've been feeling anxious about sharing my feelings with you."
    response = "I understand that sharing feelings can be scary. I appreciate your honesty."
    context = {
        "relationship_stage": "developing",
        "interaction_count": 15
    }
    
    # Test each agent's analysis
    for agent in theory_agents:
        print(f"\nTesting {agent.theory_name}:")
        analysis = await agent.analyze_message(message, response, context)
        print(f"Analysis: {json.dumps(analysis, indent=2)}")

if __name__ == "__main__":
    import asyncio
    import json
    asyncio.run(test_theory_agents())