import logging

from .base_theory_agent import TheoryAgent


class EmotionalIntelligenceTheoryAgent(TheoryAgent):
    """Agent specializing in Emotional Intelligence Theory analysis"""
    
    def __init__(self, llm_config: dict):
        principles = [
            "Emotional awareness enhances relationships",
            "Emotional regulation supports stability",
            "Understanding others' emotions builds connection",
            "Emotional intelligence can be developed",
            "Balance emotional expression and control"
        ]
        
        guidelines = [
            "Monitor and regulate emotional responses",
            "Show empathy and understanding",
            "Express emotions appropriately",
            "Help others process emotions",
            "Build emotional vocabulary"
        ]
        
        super().__init__(
            name="emotional_intelligence",
            theory_name="Emotional Intelligence Theory",
            principles=principles,
            guidelines=guidelines,
            llm_config=llm_config
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize EI components
        self.ei_components = {
            "self_awareness": 0.7,
            "self_regulation": 0.6,
            "motivation": 0.8,
            "empathy": 0.7,
            "social_skills": 0.6
        }
