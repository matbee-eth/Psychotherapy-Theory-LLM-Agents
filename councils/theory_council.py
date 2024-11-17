import autogen

from typing import List

from base_agents import EmotionalResponse, TheoryValidation
from theories.base_theory_agent import TheoryAgent
from theories.emotional_intelligence_agent import EmotionalIntelligenceTheoryAgent
from theories.social_penetration_agent import SocialPenetrationTheoryAgent
from theories.theory_agents import AttachmentTheoryAgent
from theories.uncertainty_reduction_agent import UncertaintyReductionTheoryAgent


class TheoryCouncil:
    def __init__(self, theory_agents: List[TheoryAgent], llm_config: dict):
        self.group_chat = autogen.GroupChat(theory_agents, [])
    
    async def validate(
        self, 
        message: str, 
        emotional_responses: List[EmotionalResponse]
    ) -> TheoryValidation:
        # Run group chat discussion between theory agents
        validations = await self.group_chat.discuss({
            "message": message,
            "emotional_responses": emotional_responses
        })
        
        # Synthesize theory validations
        return self._synthesize_validations(validations)