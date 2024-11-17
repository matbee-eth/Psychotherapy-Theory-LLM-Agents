
import json
import math
import autogen
from datetime import datetime
from typing import Dict, List, Optional

from agent_memory_integration import EmotionalIntensity, EmotionalMemory, EmotionalValence
from personality_framework import EmotionalState

class EmotionalMemorySystem:
    """Manages emotional memories and their influence on personality"""
    
    def __init__(self, llm_config: dict):
        self.memories: List[EmotionalMemory] = []
        self.llm_config = llm_config
        
        # Initialize memory processor
        self.memory_processor = autogen.AssistantAgent(
            name="memory_processor",
            llm_config=llm_config,
            system_message="""You are an expert in emotional processing and memory formation.
            Your role is to analyze interactions for:
            1. Emotional significance and impact
            2. Potential personality influences
            3. Associated thought patterns
            4. Memory consolidation needs
            
            Consider attachment theory, emotional processing theory, and memory consolidation research."""
        )

    async def process_interaction(
        self,
        content: str,
        current_emotion: EmotionalState,
        context: Dict
    ) -> Optional[EmotionalMemory]:
        """Process an interaction for potential emotional memory formation"""
        # Analyze interaction
        analysis = await self._analyze_interaction(content, current_emotion, context)
        
        if analysis["significance"] > 0.5:  # Threshold for memory formation
            memory = self._create_memory(content, current_emotion, analysis, context)
            self.memories.append(memory)
            await self._consolidate_memories()
            return memory
            
        return None

    async def _analyze_interaction(
        self,
        content: str,
        emotion: EmotionalState,
        context: Dict
    ) -> Dict:
        """Analyze interaction for emotional significance"""
        analysis_prompt = f"""Analyze this interaction for emotional significance and memory formation:

CONTENT: {content}
CURRENT EMOTION: {emotion.value}
CONTEXT: {context}

Consider:
1. How significant is this interaction emotionally?
2. What is the valence and intensity?
3. What thought patterns might be associated?
4. How might this influence personality development?

Provide analysis as JSON with:
- significance (0-1)
- valence (positive/negative/neutral/mixed)
- intensity (low/moderate/high/extreme)
- associated_thoughts (list)
- personality_impacts (dict of aspect->impact)"""

        try:
            response = await self.memory_processor.generate_response(analysis_prompt)
            return json.loads(response)
        except Exception as e:
            print(f"Error in memory analysis: {str(e)}")
            return {
                "significance": 0.0,
                "valence": "neutral",
                "intensity": "low",
                "associated_thoughts": [],
                "personality_impacts": {}
            }

    def _create_memory(
        self,
        content: str,
        emotion: EmotionalState,
        analysis: Dict,
        context: Dict
    ) -> EmotionalMemory:
        """Create new emotional memory"""
        return EmotionalMemory(
            id=f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now(),
            content=content,
            emotion=emotion,
            valence=EmotionalValence[analysis["valence"].upper()],
            intensity=EmotionalIntensity[analysis["intensity"].upper()],
            context=context,
            impact_scores=analysis["personality_impacts"],
            associated_thoughts=analysis["associated_thoughts"]
        )

    async def _consolidate_memories(self) -> None:
        """Consolidate and organize memories"""
        if len(self.memories) < 2:
            return

        recent_memories = [
            {
                "content": m.content,
                "emotion": m.emotion.value,
                "impact_scores": m.impact_scores
            } for m in self.memories[-5:]  # Last 5 memories
        ]

        consolidation_prompt = f"""Analyze these recent memories for consolidation:

MEMORIES:
{recent_memories}

Consider:
1. Are there repeated patterns?
2. How do these memories relate?
3. Should any memories be combined?
4. What broader patterns are emerging?

Provide analysis as JSON with:
- patterns (list)
- consolidation_suggestions (list)
- emerging_themes (dict)"""

        try:
            response = await self.memory_processor.generate_response(
                consolidation_prompt
            )
            consolidation = json.loads(response)
            
            # Update memory impact scores based on patterns
            self._update_memory_impacts(consolidation["patterns"])
            
        except Exception as e:
            print(f"Error in memory consolidation: {str(e)}")

    def _update_memory_impacts(self, patterns: List[Dict]) -> None:
        """Update memory impact scores based on identified patterns"""
        for pattern in patterns:
            pattern_type = pattern.get("type", "")
            impact = pattern.get("impact", 0.0)
            
            for memory in self.memories:
                if pattern_type in memory.impact_scores:
                    memory.update_impact(pattern_type, impact)

    def get_influential_memories(
        self,
        emotion: Optional[EmotionalState] = None,
        limit: int = 5
    ) -> List[EmotionalMemory]:
        """Get most influential memories, optionally filtered by emotion"""
        # Calculate influence scores
        scored_memories = []
        for memory in self.memories:
            if emotion and memory.emotion != emotion:
                continue
                
            # Calculate decay based on time
            days_old = (datetime.now() - memory.timestamp).days
            decay = math.exp(-memory.decay_rate * days_old)
            
            # Calculate influence score
            influence = (
                sum(memory.impact_scores.values()) * 
                decay * 
                (1 + memory.reinforcement_count * 0.1)  # Reinforcement bonus
            )
            
            scored_memories.append((memory, influence))
        
        # Sort by influence and return top memories
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored_memories[:limit]]

    def update_memory_context(
        self,
        memory_id: str,
        new_context: Dict
    ) -> bool:
        """Update context for a specific memory"""
        for memory in self.memories:
            if memory.id == memory_id:
                memory.context.update(new_context)
                memory.last_accessed = datetime.now()
                return True
        return False
    
async def test_emotional_memory():
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "model": "gpt-4"
    }
    
    memory_system = EmotionalMemorySystem(llm_config)
    
    # Test processing an interaction
    content = "I felt really hurt when you said that. It reminded me of past rejections."
    current_emotion = EmotionalState.SAD
    context = {
        "relationship_stage": "developing",
        "trust_level": 0.7,
        "recent_interactions": ["positive", "supportive", "conflictual"]
    }
    
    memory = await memory_system.process_interaction(
        content, current_emotion, context
    )
    
    if memory:
        print("\nCreated Memory:")
        print(f"Content: {memory.content}")
        print(f"Emotion: {memory.emotion.value}")
        print(f"Valence: {memory.valence.value}")
        print(f"Intensity: {memory.intensity.value}")
        print(f"Impact Scores: {memory.impact_scores}")
        print(f"Associated Thoughts: {memory.associated_thoughts}")
    
    # Get influential memories
    influential = memory_system.get_influential_memories(limit=3)
    print("\nInfluential Memories:")
    for mem in influential:
        print(f"- {mem.content} ({mem.emotion.value})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_emotional_memory())
