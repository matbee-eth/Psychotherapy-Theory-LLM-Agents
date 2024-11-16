from typing import Dict, List
from datetime import datetime
import json
import autogen

from agent_memory_integration import EmotionalMemory
from personalities.base_personality import PersonalityAdaptation, TraumaType


class AdaptivePersonalitySystem:
    """System that develops personality adaptations based on interaction history"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.emotional_memories: List[EmotionalMemory] = []
        self.personality_adaptations: Dict[str, PersonalityAdaptation] = {}
        self.current_emotional_state: Dict[str, float] = {}
        
        # Initialize LLM agents
        self.memory_processor = autogen.AssistantAgent(
            name="memory_processor",
            llm_config=llm_config,
            system_message="""You are an expert in analyzing emotional experiences and their impact on personality development.
            Your role is to:
            1. Identify emotional significance of interactions
            2. Recognize patterns of relational trauma
            3. Understand how experiences shape personality adaptations
            4. Track emotional and behavioral changes over time"""
        )
        
        self.adaptation_manager = autogen.AssistantAgent(
            name="adaptation_manager",
            llm_config=llm_config,
            system_message="""You are an expert in personality development and adaptation.
            Your role is to:
            1. Identify emerging personality patterns
            2. Track development of coping mechanisms
            3. Understand how adaptations influence behavior
            4. Maintain psychological coherence
            
            Consider attachment theory, object relations, and trauma response patterns."""
        )
    
    async def process_interaction(
        self,
        message: str,
        bot_response: str,
        context: Dict
    ) -> Dict:
        """Process an interaction for emotional impact and adaptation"""
        # Analyze interaction
        trauma_analysis = await self._analyze_interaction(
            message, bot_response, context
        )
        
        if trauma_analysis["significance"] > 0.3:  # Threshold for significance
            # Create and store emotional memory
            memory = self._create_emotional_memory(
                trauma_analysis, message, bot_response, context
            )
            self.emotional_memories.append(memory)
            
            # Process memory for adaptations
            await self._process_memory(memory)
            
            # Update personality adaptations
            await self._update_adaptations(memory)
        
        # Update emotional state
        self._update_emotional_state(trauma_analysis["emotional_impact"])
        
        return {
            "trauma_analysis": trauma_analysis,
            "current_adaptations": self._get_active_adaptations(),
            "emotional_state": self.current_emotional_state
        }
    
    async def _analyze_interaction(
        self,
        message: str,
        bot_response: str,
        context: Dict
    ) -> Dict:
        """Analyze interaction for emotional significance and trauma patterns"""
        analysis_prompt = f"""Analyze this interaction for emotional significance and potential trauma patterns:

MESSAGE: {message}
BOT RESPONSE: {bot_response}
CONTEXT: {json.dumps(context)}

Consider:
1. Is there emotional or relational significance?
2. Are there patterns of trauma (abandonment, criticism, etc.)?
3. What is the emotional impact?
4. How might this shape personality adaptation?

Provide analysis as JSON with:
- significance (0-1)
- trauma_types (list)
- emotional_impact (dict of emotions->intensity)
- behavioral_implications (list)"""

        try:
            response = await self.memory_processor.generate_response(analysis_prompt)
            return json.loads(response)
        except Exception as e:
            print(f"Error in interaction analysis: {str(e)}")
            return {
                "significance": 0.0,
                "trauma_types": [],
                "emotional_impact": {},
                "behavioral_implications": []
            }
    
    def _create_emotional_memory(
        self,
        analysis: Dict,
        message: str,
        bot_response: str,
        context: Dict
    ) -> EmotionalMemory:
        """Create emotional memory from interaction"""
        primary_trauma = (
            TraumaType(analysis["trauma_types"][0])
            if analysis["trauma_types"]
            else TraumaType.ATTACHMENT
        )
        
        return EmotionalMemory(
            timestamp=datetime.now(),
            interaction_type=primary_trauma,
            intensity=analysis["significance"],
            emotional_impact=analysis["emotional_impact"],
            user_behavior=message,
            bot_response=bot_response,
            context=context
        )
    
    async def _process_memory(self, memory: EmotionalMemory) -> None:
        """Process emotional memory for personality implications"""
        processing_prompt = f"""Process this emotional memory for personality implications:

MEMORY:
- Type: {memory.interaction_type.value}
- Intensity: {memory.intensity}
- Emotional Impact: {json.dumps(memory.emotional_impact)}
- User Behavior: {memory.user_behavior}
- Bot Response: {memory.bot_response}

Consider:
1. How does this experience reinforce or challenge existing adaptations?
2. What new adaptations might be forming?
3. How should this integrate with existing personality structure?

Provide analysis as JSON with:
- adaptation_updates (dict of adaptation->impact)
- new_adaptations (list)
- integration_notes (string)"""

        try:
            response = await self.memory_processor.generate_response(
                processing_prompt
            )
            processing_result = json.loads(response)
            
            # Update existing adaptations
            for adapt_name, impact in processing_result["adaptation_updates"].items():
                if adapt_name in self.personality_adaptations:
                    adaptation = self.personality_adaptations[adapt_name]
                    adaptation.update_activation(impact)
                    adaptation.associated_memories.append(memory.timestamp.isoformat())
            
            # Create new adaptations if needed
            for new_adapt in processing_result["new_adaptations"]:
                if new_adapt["name"] not in self.personality_adaptations:
                    self.personality_adaptations[new_adapt["name"]] = PersonalityAdaptation(
                        name=new_adapt["name"],
                        trigger_types=set(TraumaType(t) for t in new_adapt["triggers"]),
                        activation_level=new_adapt["initial_activation"],
                        formation_date=datetime.now(),
                        behavioral_manifestations=new_adapt["manifestations"]
                    )
            
            memory.processed = True
            
        except Exception as e:
            print(f"Error processing memory: {str(e)}")
    
    async def _update_adaptations(self, memory: EmotionalMemory) -> None:
        """Update personality adaptations based on new memory"""
        adaptation_prompt = f"""Update personality adaptations based on new experience:

MEMORY:
```json

{json.dumps(memory.__dict__, indent=2, default=str)}
```

CURRENT ADAPTATIONS:
```json
{json.dumps({name: adapt.__dict__ for name, adapt in self.personality_adaptations.items()}, indent=2, default=str)}
```

Consider:
1. How should existing adaptations evolve?
2. Are new adaptations needed?
3. How do adaptations interact?

Provide updates as JSON with:
- adaptation_changes (dict of adaptation->change)
- new_adaptations (list)
- removal_suggestions (list)"""

        try:
            response = await self.adaptation_manager.generate_response(
                adaptation_prompt
            )
            updates = json.loads(response)
            
            # Apply adaptation changes
            for adapt_name, change in updates["adaptation_changes"].items():
                if adapt_name in self.personality_adaptations:
                    self.personality_adaptations[adapt_name].update_activation(change)
            
            # Add new adaptations
            for new_adapt in updates["new_adaptations"]:
                if new_adapt["name"] not in self.personality_adaptations:
                    self.personality_adaptations[new_adapt["name"]] = PersonalityAdaptation(
                        name=new_adapt["name"],
                        trigger_types=set(TraumaType(t) for t in new_adapt["triggers"]),
                        activation_level=new_adapt["initial_activation"],
                        formation_date=datetime.now()
                    )
            
            # Remove suggested adaptations
            for adapt_name in updates["removal_suggestions"]:
                if adapt_name in self.personality_adaptations:
                    del self.personality_adaptations[adapt_name]
                    
        except Exception as e:
            print(f"Error updating adaptations: {str(e)}")
    
    def _update_emotional_state(self, emotional_impact: Dict[str, float]) -> None:
        """Update current emotional state"""
        # Decay existing emotions
        for emotion in self.current_emotional_state:
            self.current_emotional_state[emotion] *= 0.8
        
        # Add new emotional impacts
        for emotion, intensity in emotional_impact.items():
            if emotion in self.current_emotional_state:
                self.current_emotional_state[emotion] = max(
                    self.current_emotional_state[emotion],
                    intensity
                )
            else:
                self.current_emotional_state[emotion] = intensity
    
    def _get_active_adaptations(self) -> Dict[str, Dict]:
        """Get currently active personality adaptations"""
        active = {}
        for name, adaptation in self.personality_adaptations.items():
            if adaptation.activation_level > 0.3:  # Activation threshold
                active[name] = {
                    "activation_level": adaptation.activation_level,
                    "reinforcement_count": adaptation.reinforcement_count,
                    "behavioral_manifestations": adaptation.behavioral_manifestations
                }
        return active
    
    async def modify_response(
        self,
        original_response: str,
        context: Dict
    ) -> str:
        """Modify response based on current personality adaptations"""
        active_adaptations = self._get_active_adaptations()
        
        if not active_adaptations:
            return original_response
            
        modification_prompt = f"""Modify this response based on active personality adaptations:

ORIGINAL RESPONSE: {original_response}

ACTIVE ADAPTATIONS:
```json

{json.dumps(active_adaptations, indent=2, default=str)}
```
EMOTIONAL STATE:
```json

{json.dumps(self.current_emotional_state, indent=2, default=str)}
```
CONTEXT:
```json

{json.dumps(context, indent=2, default=str)}
```
Modify the response to reflect:
1. Active personality adaptations
2. Current emotional state
3. Behavioral manifestations
4. Maintaining psychological coherence

Provide modified response that naturally incorporates these elements."""

        try:
            response = await self.adaptation_manager.generate_response(
                modification_prompt
            )
            return response.strip()
        except Exception as e:
            print(f"Error modifying response: {str(e)}")
            return original_response

async def test_adaptive_personality():
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "model": "gpt-4"
    }
    
    system = AdaptivePersonalitySystem(llm_config)
    
    # Test interaction that might trigger abandonment fears
    message = "I'm going to be away for a while and won't be able to talk."
    bot_response = "I understand. I'll be here when you return."
    context = {
        "relationship_stage": "established",
        "interaction_count": 50,
        "recent_emotions": {
            "anxiety": 0.6,
            "attachment": 0.8
        }
    }
    
    # Process interaction
    result = await system.process_interaction(message, bot_response, context)
    
    # Get modified response based on adaptations
    modified_response = await system.modify_response(bot_response, context)
    
    print("\nAnalysis Result:")
    print(json.dumps(result, indent=2))
    print("\nOriginal Response:", bot_response)
    print("\nModified Response:", modified_response)
    print("\nActive Adaptations:")
    print(json.dumps(system._get_active_adaptations(), indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_adaptive_personality())
