from typing import Dict, Optional

from .base_theory_agent import TheoryAgent


class AttachmentTheoryAgent(TheoryAgent):
    """Agent specializing in Attachment Theory analysis"""
    
    def __init__(self, llm_config: dict):
        principles = [
            "Early attachment patterns influence current relationships",
            "Secure base enables exploration and growth",
            "Consistency builds trust and security",
            "Emotional availability supports connection",
            "Balance autonomy and connection needs"
        ]
        
        guidelines = [
            "Provide consistent emotional responses",
            "Acknowledge and validate emotions",
            "Maintain appropriate boundaries",
            "Offer support while respecting independence",
            "Address attachment-related anxieties"
        ]
        
        super().__init__(
            name="attachment_theory",
            theory_name="Attachment Theory",
            principles=principles,
            guidelines=guidelines,
            llm_config=llm_config
        )
        
        # Initialize attachment-specific state
        self.attachment_patterns = {
            "secure": 0.7,
            "anxious": 0.2,
            "avoidant": 0.1
        }
    
    def _create_analysis_prompt(
        self,
        message: str,
        response: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Create attachment-specific analysis prompt"""
        # Get base prompt
        prompt = super()._create_analysis_prompt(message, response, context)
        
        # Add attachment-specific considerations
        prompt += f"""

Current Attachment Patterns:
{self.attachment_patterns}

Additional Considerations:
1. How does this reflect current attachment patterns?
2. What attachment needs are being expressed?
3. How well does this support secure attachment?
4. What attachment-based interventions might help?"""

        return prompt
