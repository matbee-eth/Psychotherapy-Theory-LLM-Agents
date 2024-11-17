from typing import Dict, Optional
from theories.base_theory_agent import TheoryAgent

class SocialPenetrationTheoryAgent(TheoryAgent):
    """Agent specializing in Social Penetration Theory analysis"""
    
    def __init__(self, llm_config: dict):
        principles = [
            "Relationships develop through gradual self-disclosure",
            "Disclosure progresses from shallow to deep",
            "Reciprocity drives relationship development",
            "Trust develops through mutual disclosure",
            "Different relationship stages have different norms"
        ]
        
        guidelines = [
            "Match disclosure level to relationship stage",
            "Progress gradually in intimacy",
            "Maintain appropriate pace of disclosure",
            "Encourage reciprocal sharing",
            "Respect personal boundaries"
        ]
        
        super().__init__(
            name="social_penetration",
            theory_name="Social Penetration Theory",
            principles=principles,
            guidelines=guidelines,
            llm_config=llm_config
        )
        
        # Initialize relationship layers
        self.layers = {
            "peripheral": 0.8,
            "intermediate": 0.4,
            "central": 0.2,
            "inner_core": 0.1
        }
    
    def _create_analysis_prompt(
        self,
        message: str,
        response: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Create social penetration-specific analysis prompt"""
        prompt = super()._create_analysis_prompt(message, response, context)
        
        prompt += f"""

Current Relationship Layers:
{self.layers}

Additional Considerations:
1. What layer of disclosure is being accessed?
2. Is the disclosure level appropriate?
3. How well is reciprocity being maintained?
4. What depth of sharing should be encouraged?"""

        return prompt
