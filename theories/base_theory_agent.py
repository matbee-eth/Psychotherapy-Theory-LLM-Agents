
from datetime import datetime
import json
from typing import Dict, List, Optional
import autogen


class TheoryAgent(autogen.AssistantAgent):
    """Base class for psychological theory agents with AutoGen integration"""
    
    def __init__(
        self,
        name: str,
        theory_name: str,
        principles: List[str],
        guidelines: List[str],
        llm_config: dict
    ):
        # Create theory-specific system message
        system_message = self._create_system_message(
            theory_name,
            principles,
            guidelines
        )
        
        # Initialize AutoGen assistant
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config
        )
        
        self.theory_name = theory_name
        self.principles = principles
        self.guidelines = guidelines
        
        # Initialize timestamp
        self.last_analysis = datetime.now()
    
    def _create_system_message(
        self,
        theory_name: str,
        principles: List[str],
        guidelines: List[str]
    ) -> str:
        """Create the system message for this theory agent"""
        principles_str = "\n".join(f"- {p}" for p in principles)
        guidelines_str = "\n".join(f"- {g}" for g in guidelines)
        
        return f"""You are an expert in {theory_name}, analyzing interactions and guiding responses.

Key Principles:
{principles_str}

Guidelines:
{guidelines_str}

Your role is to:
1. Analyze messages through the lens of {theory_name}
2. Evaluate response alignment with theoretical principles
3. Suggest improvements based on theory
4. Consider relationship development
5. Monitor theory compliance

Always structure your responses as JSON with:
{{
    "analysis": {{
        "alignment_score": <float 0-1>,
        "theory_principles": [<list of relevant principles>],
        "guidelines_applied": [<list of relevant guidelines>],
        "concerns": [<list of theoretical concerns>],
        "suggestions": [<list of theory-based improvements>]
    }},
    "rationale": <explanation of analysis>,
    "intervention": {{
        "needed": <boolean>,
        "type": <string>,
        "suggestions": [<list of interventions>]
    }},
    "relationship": {{
        "current_stage": <string>,
        "development_path": <string>,
        "next_actions": [<list of recommended actions>]
    }}
}}"""

    async def analyze_message(
        self, 
        message: str,
        response: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """Analyze a message/response pair through theoretical lens"""
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(message, response, context)
            
            # Get analysis using AutoGen's chat completion
            result = await self.generate_response(prompt)
            
            try:
                # Parse JSON response
                analysis = json.loads(result)
                self.last_analysis = datetime.now()
                return analysis
                
            except json.JSONDecodeError:
                return self._create_fallback_analysis()
                
        except Exception as e:
            print(f"Error in theory analysis: {str(e)}")
            return self._create_fallback_analysis()
    
    def _create_analysis_prompt(
        self,
        message: str,
        response: Optional[str],
        context: Optional[Dict]
    ) -> str:
        """Create prompt for theoretical analysis"""
        # Base message context
        prompt = f"""Analyze this interaction using {self.theory_name}:

MESSAGE: {message}"""

        # Add response if provided
        if response:
            prompt += f"\n\nRESPONSE: {response}"
            
        # Add context if provided
        if context:
            prompt += f"""\n\nCONTEXT:
            ```json
            {json.dumps(context, indent=2)}
            ```
"""
            
        prompt += """

Consider:
1. How well does this align with theoretical principles?
2. What theory-specific patterns are present?
3. What interventions might be needed?
4. How does this affect relationship development?

Provide analysis in the specified JSON format."""

        return prompt
    
    def _create_fallback_analysis(self) -> Dict:
        """Create a safe fallback analysis"""
        return {
            "analysis": {
                "alignment_score": 0.5,
                "theory_principles": [self.principles[0]],
                "guidelines_applied": [self.guidelines[0]],
                "concerns": ["Unable to perform complete analysis"],
                "suggestions": ["Consider reviewing interaction"]
            },
            "rationale": "Fallback analysis due to processing error",
            "intervention": {
                "needed": False,
                "type": "none",
                "suggestions": []
            },
            "relationship": {
                "current_stage": "unknown",
                "development_path": "maintain",
                "next_actions": ["Continue normal interaction"]
            }
        }
    
    async def evaluate_response(
        self,
        message: str,
        proposed_response: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """Evaluate if a proposed response aligns with theory"""
        analysis = await self.analyze_message(
            message,
            proposed_response,
            context
        )
        
        return {
            "theory_name": self.theory_name,
            "alignment_score": analysis["analysis"]["alignment_score"],
            "suggestions": analysis["analysis"]["suggestions"],
            "concerns": analysis["analysis"]["concerns"],
            "rationale": analysis["rationale"]
        }
