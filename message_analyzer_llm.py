from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
from interaction_context import MessageAnalysis, InteractionType
import autogen

class MessageAnalyzer:
    """Analyzes messages using LLM for deep understanding"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.analysis_prompt = """Analyze the following message and provide a detailed analysis in JSON format. Include:
1. sentiment_score: Float from -1 to 1 representing overall sentiment
2. emotional_intensity: Float from 0 to 1 representing emotional intensity
3. topics: List of relevant topics discussed
4. interaction_type: One of ["message", "question", "disclosure", "emotional_expression", "request", "feedback"]
5. disclosure_level: Float from 0 to 1 representing how personal/intimate the disclosure is
6. uncertainty_level: Float from 0 to 1 representing how uncertain/tentative the message is
7. emotional_indicators: Dictionary mapping emotions to their intensity (0-1)
8. key_entities: List of important entities mentioned

Message: {message}

Provide your analysis as valid JSON that matches this structure exactly.
"""
        
        # Initialize LLM agent for analysis
        self.analysis_agent = autogen.AssistantAgent(
            name="message_analyzer",
            llm_config=llm_config,
            system_message="""You are an expert at analyzing human messages for emotional content, 
            intent, and psychological significance. You provide analysis in clean, valid JSON format."""
        )
    
    async def analyze_message(self, message: str) -> MessageAnalysis:
        """Perform complete analysis of a message using LLM"""
        try:
            # Get LLM analysis
            analysis_result = await self._get_llm_analysis(message)
            
            # Parse analysis into MessageAnalysis object
            return MessageAnalysis(
                sentiment_score=analysis_result["sentiment_score"],
                emotional_intensity=analysis_result["emotional_intensity"],
                topics=analysis_result["topics"],
                intent=InteractionType(analysis_result["interaction_type"]),
                disclosure_level=analysis_result["disclosure_level"],
                uncertainty_level=analysis_result["uncertainty_level"],
                key_entities=analysis_result["key_entities"],
                emotional_indicators=analysis_result["emotional_indicators"]
            )
            
        except Exception as e:
            print(f"Error analyzing message: {str(e)}")
            # Return neutral analysis in case of error
            return self._create_neutral_analysis()
    
    async def _get_llm_analysis(self, message: str) -> Dict:
        """Get analysis from LLM"""
        # Create analysis request
        prompt = self.analysis_prompt.format(message=message)
        
        try:
            # Get response from LLM
            response = await self.analysis_agent.generate_response(
                prompt,
                max_tokens=500
            )
            
            # Parse JSON response
            analysis = json.loads(response)
            return analysis
            
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")
    
    def _create_neutral_analysis(self) -> MessageAnalysis:
        """Create neutral analysis for fallback"""
        return MessageAnalysis(
            sentiment_score=0.0,
            emotional_intensity=0.0,
            topics=[],
            intent=InteractionType.MESSAGE,
            disclosure_level=0.0,
            uncertainty_level=0.5,
            key_entities=[],
            emotional_indicators={
                "joy": 0.0,
                "sadness": 0.0,
                "anger": 0.0,
                "fear": 0.0,
                "surprise": 0.0
            }
        )

class ContextEnricher:
    """Enriches message analysis with additional context using LLM"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.enrichment_prompt = """Given the following message analysis and conversation history,
provide additional insights about:
1. Relationship dynamics
2. Psychological patterns
3. Potential underlying needs
4. Suggested therapeutic approaches

Message: {message}
Current Analysis: {current_analysis}
Recent History: {recent_history}

Provide your enrichment analysis as valid JSON.
"""
        
        self.enrichment_agent = autogen.AssistantAgent(
            name="context_enricher",
            llm_config=llm_config,
            system_message="""You are an expert at understanding deeper psychological 
            patterns and relationship dynamics in conversations. You provide nuanced insights 
            while maintaining therapeutic awareness."""
        )
    
    async def enrich_analysis(
        self,
        message: str,
        current_analysis: MessageAnalysis,
        recent_history: List[Dict]
    ) -> Dict:
        """Enrich the current analysis with additional context and insights"""
        try:
            # Create enrichment request
            prompt = self.enrichment_prompt.format(
                message=message,
                current_analysis=current_analysis.__dict__,
                recent_history=recent_history
            )
            
            # Get enrichment from LLM
            response = await self.enrichment_agent.generate_response(
                prompt,
                max_tokens=800
            )
            
            # Parse and return enrichment
            return json.loads(response)
            
        except Exception as e:
            print(f"Error enriching analysis: {str(e)}")
            return {}

class TheoryIntegrator:
    """Integrates psychological theories into message analysis"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.theory_prompt = """Given the following message analysis and psychological theories,
provide theory-based insights and recommendations:

Message Analysis: {analysis}
Active Theories: {theories}

Consider how each theory explains the interaction and what it suggests for the response.
Provide your theory integration as valid JSON.
"""
        
        self.theory_agent = autogen.AssistantAgent(
            name="theory_integrator",
            llm_config=llm_config,
            system_message="""You are an expert at applying psychological theories to 
            understand human interactions. You provide clear, theory-based insights and 
            practical recommendations."""
        )
    
    async def integrate_theories(
        self,
        analysis: MessageAnalysis,
        active_theories: List[str]
    ) -> Dict:
        """Integrate psychological theories into the analysis"""
        try:
            # Create theory integration request
            prompt = self.theory_prompt.format(
                analysis=analysis.__dict__,
                theories=active_theories
            )
            
            # Get theory insights from LLM
            response = await self.theory_agent.generate_response(
                prompt,
                max_tokens=800
            )
            
            # Parse and return theory integration
            return json.loads(response)
            
        except Exception as e:
            print(f"Error integrating theories: {str(e)}")
            return {}

# Example usage
async def test_message_analysis():
    # Initialize with LLM config
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 800,
        "model": "gpt-4"  # Or your chosen model
    }
    
    analyzer = MessageAnalyzer(llm_config)
    enricher = ContextEnricher(llm_config)
    theory_integrator = TheoryIntegrator(llm_config)
    
    # Test message
    message = "I've been feeling anxious about sharing my feelings, but I trust you enough to tell you."
    
    # Get base analysis
    analysis = await analyzer.analyze_message(message)
    
    # Enrich analysis with context
    enrichment = await enricher.enrich_analysis(
        message,
        analysis,
        recent_history=[{"message": "Previous message", "analysis": "Previous analysis"}]
    )
    
    # Integrate psychological theories
    theory_insights = await theory_integrator.integrate_theories(
        analysis,
        active_theories=["Attachment Theory", "Social Penetration Theory"]
    )
    
    # Print results
    print("Base Analysis:", analysis)
    print("\nEnrichment:", enrichment)
    print("\nTheory Insights:", theory_insights)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_message_analysis())