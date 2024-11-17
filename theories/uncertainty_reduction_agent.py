
from typing import Dict, Optional
from theories.base_theory_agent import TheoryAgent

class UncertaintyReductionTheoryAgent(TheoryAgent):
    """Agent specializing in Uncertainty Reduction Theory analysis"""
    
    def __init__(self, llm_config: dict):
        principles = [
            "People seek to reduce uncertainty in relationships",
            "Information gathering reduces uncertainty",
            "Uncertainty affects relationship development",
            "Predictability builds comfort and trust",
            "Communication patterns reflect uncertainty levels"
        ]
        
        guidelines = [
            "Address uncertainties directly",
            "Provide clear and consistent information",
            "Maintain appropriate transparency",
            "Use self-disclosure strategically",
            "Monitor uncertainty levels"
        ]
        
        super().__init__(
            name="uncertainty_reduction",
            theory_name="Uncertainty Reduction Theory",
            principles=principles,
            guidelines=guidelines,
            llm_config=llm_config
        )
        
        self.uncertainty_metrics = {
            "cognitive": 0.5,
            "behavioral": 0.4,
            "affective": 0.6
        }
    
    def _create_analysis_prompt(
        self,
        message: str,
        response: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Create uncertainty reduction-specific analysis prompt"""
        prompt = super()._create_analysis_prompt(message, response, context)
        
        prompt += f"""

Current Uncertainty Metrics:
{self.uncertainty_metrics}

Additional Considerations:
1. What uncertainties are present?
2. How effectively is uncertainty being addressed?
3. What information would reduce uncertainty?
4. How can predictability be enhanced?"""

        return prompt
