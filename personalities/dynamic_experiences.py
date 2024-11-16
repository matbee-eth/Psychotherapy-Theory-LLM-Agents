
import autogen
import json

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

@dataclass
class FormativeExperience:
    """A significant experience that shapes personality development"""
    id: str
    timestamp: datetime
    description: str
    memory_content: Dict[str, any]  # Raw content/details of the experience
    significance: float  # 0-1 scale
    processing_state: Dict = field(default_factory=dict)  # Current processing status

@dataclass
class PersonalityStructure:
    """Current state of personality development"""
    experiences: List[FormativeExperience] = field(default_factory=list)
    adaptations: Dict[str, any] = field(default_factory=dict)
    core_beliefs: Dict[str, any] = field(default_factory=dict)
    current_state: Dict[str, any] = field(default_factory=dict)

class ExperienceProcessor:
    """Processes experiences using LLM for dynamic adaptation development"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.personality = PersonalityStructure()
        
        # Initialize LLM analyzer
        self.analyzer = autogen.AssistantAgent(
            name="experience_analyzer",
            llm_config=llm_config,
            system_message="""You are an expert in personality development, trauma response, and psychological adaptation.
            Your role is to analyze experiences and their impact on personality development with attention to:
            
            1. Psychological impact and meaning
            2. Development of adaptive and maladaptive patterns
            3. Formation of core beliefs and defenses
            4. Integration with existing personality structure
            
            Consider developmental psychology, trauma theory, and personality development research.
            Analyze without judgment of healthy vs unhealthy - focus on actual impact and adaptation."""
        )
    
    async def process_experience(
        self,
        experience_content: Dict,
        current_state: Dict
    ) -> Dict:
        """Process a new experience and its impact on personality"""
        
        # Create experience record
        experience = FormativeExperience(
            id=f"exp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now(),
            description=experience_content.get("description", ""),
            memory_content=experience_content,
            significance=0.0  # Will be determined by analysis
        )
        
        # Analyze experience impact
        analysis = await self._analyze_experience(experience, current_state)
        
        # Update experience with analysis
        experience.significance = analysis.get("significance", 0.0)
        experience.processing_state = analysis
        
        # Store experience
        self.personality.experiences.append(experience)
        
        # Process adaptations
        if analysis.get("significance", 0) > 0.3:  # Threshold for adaptation processing
            await self._process_adaptations(experience, analysis)
        
        return {
            "experience_id": experience.id,
            "analysis": analysis,
            "current_state": self.personality.current_state
        }
    
    async def _analyze_experience(
        self,
        experience: FormativeExperience,
        current_state: Dict
    ) -> Dict:
        """Have LLM analyze experience impact"""
        
        analysis_prompt = f"""Analyze this experience and its psychological impact:

EXPERIENCE: 
```json
{json.dumps(experience.memory_content)}

```

CURRENT PERSONALITY STATE:
```json
{json.dumps(current_state, indent=2)}
```

EXISTING ADAPTATIONS:
```json
{json.dumps(self.personality.adaptations, indent=2)}
```

Consider:
1. What is the psychological significance and meaning?
2. How might this impact personality development?
3. What adaptations might form or be reinforced?
4. How does this interact with existing patterns?
5. What defenses or coping responses might develop?

Provide detailed analysis in JSON format covering:
- significance (0-1 scale)
- psychological_impact (detailed assessment)
- potential_adaptations
- defense_responses
- core_belief_changes
- integration_notes"""

        try:
            response = await self.analyzer.generate_response(analysis_prompt)
            return json.loads(response)
        except Exception as e:
            print(f"Error in experience analysis: {str(e)}")
            return {"significance": 0.0}
    
    async def _process_adaptations(
        self,
        experience: FormativeExperience,
        analysis: Dict
    ) -> None:
        """Process experience for adaptation development using LLM"""
        
        adaptation_prompt = f"""Process this experience for personality adaptation:

EXPERIENCE ANALYSIS:
```json
{json.dumps(analysis, indent=2)}
```

CURRENT ADAPTATIONS:
```json
{json.dumps(self.personality.adaptations, indent=2)}
```

PERSONALITY STATE:
```json
{json.dumps(self.personality.current_state, indent=2)}
```

Consider:
1. Should new adaptations form?
2. How should existing adaptations evolve?
3. What are the functional/survival benefits?
4. What are secondary gains or maintenance factors?
5. How do adaptations interact or conflict?

Provide adaptation analysis in JSON format covering:
- new_adaptations (if any)
- adaptation_updates
- integration_strategy
- maintenance_factors"""

        try:
            response = await self.analyzer.generate_response(adaptation_prompt)
            adaptation_result = json.loads(response)
            
            # Integrate adaptation changes
            self._integrate_adaptation_changes(adaptation_result)
            
        except Exception as e:
            print(f"Error in adaptation processing: {str(e)}")
    
    def _integrate_adaptation_changes(self, adaptation_result: Dict) -> None:
        """Integrate adaptation changes into personality structure"""
        # Add new adaptations
        new_adaptations = adaptation_result.get("new_adaptations", {})
        self.personality.adaptations.update(new_adaptations)
        
        # Update existing adaptations
        updates = adaptation_result.get("adaptation_updates", {})
        for adapt_id, changes in updates.items():
            if adapt_id in self.personality.adaptations:
                self.personality.adaptations[adapt_id].update(changes)
        
        # Update personality state
        self.personality.current_state.update(
            adaptation_result.get("integration_strategy", {})
        )

# Example usage
async def test_experience_processor():
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "model": "gpt-4"
    }
    
    processor = ExperienceProcessor(llm_config)
    
    # Test experience
    experience = {
        "description": "Trusted friend betrayed confidence",
        "context": {
            "relationship": "close friend",
            "duration": "2 years",
            "impact": "public humiliation",
            "response": "social withdrawal"
        },
        "emotional_intensity": 0.8,
        "resolution": "friendship ended"
    }
    
    # Current state
    current_state = {
        "trust_level": 0.7,
        "social_engagement": 0.6,
        "emotional_regulation": 0.5
    }
    
    # Process experience
    result = await processor.process_experience(experience, current_state)
    
    print("\nExperience Processing Result:")
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_experience_processor())
