from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import asyncio

from enhanced_memory_system import MemoryManager, Memory, MemoryType, MemoryPriority
from base_agents import EmotionalAgent, TheoryAgent, ControlRoom, EmotionalState
from personality_framework import PersonalityFramework

@dataclass
class EmotionalMemory:
    """Structured emotional memory for agents"""
    emotion: EmotionalState
    intensity: float
    trigger: str
    context: Dict[str, Any]
    timestamp: datetime
    agent_id: str

@dataclass
class TheoryInsight:
    """Structured theory-based insight"""
    theory_name: str
    pattern_observed: str
    recommendation: str
    confidence: float
    context: Dict[str, Any]
    timestamp: datetime

class MemoryAwareEmotionalAgent(EmotionalAgent):
    """Emotional agent with memory integration"""
    
    def __init__(self, name: str, emotion: EmotionalState, personality: PersonalityFramework, 
                 llm_config: dict, memory_manager: MemoryManager):
        super().__init__(name, emotion, personality.personality_traits, llm_config)
        self.memory_manager = memory_manager
        self.emotional_history: List[EmotionalMemory] = []
        
    async def process_message(self, message: str, context: Dict) -> str:
        """Process message with memory integration"""
        # Get relevant memories
        memories = await self.memory_manager.get_relevant_memories(message, context)
        
        # Update context with memories
        enhanced_context = self._enhance_context_with_memories(context, memories)
        
        # Generate response using enhanced context
        response = await super().process_message(message, enhanced_context)
        
        # Store emotional memory
        await self._store_emotional_memory(message, response, context)
        
        return response
    
    def _enhance_context_with_memories(
        self,
        context: Dict,
        memories: Dict[str, List[Memory]]
    ) -> Dict:
        """Enhance context using relevant memories"""
        return {
            **context,
            "emotional_patterns": self._extract_emotional_patterns(memories),
            "interaction_history": self._extract_interaction_history(memories),
            "behavioral_patterns": self._extract_behavioral_patterns(memories)
        }
    
    def _extract_emotional_patterns(self, memories: Dict[str, List[Memory]]) -> List[Dict]:
        """Extract emotional patterns from memories"""
        emotional_memories = memories.get("emotional", [])
        patterns = []
        
        for memory in emotional_memories:
            if isinstance(memory.content, dict):
                patterns.append({
                    "emotion": memory.content.get("emotion"),
                    "intensity": memory.content.get("intensity"),
                    "trigger": memory.content.get("trigger"),
                    "timestamp": memory.timestamp
                })
        
        return patterns
    
    def _extract_interaction_history(self, memories: Dict[str, List[Memory]]) -> List[Dict]:
        """Extract interaction history from memories"""
        episodic_memories = memories.get("episodic", [])
        return [memory.content for memory in episodic_memories 
                if isinstance(memory.content, dict)]
    
    def _extract_behavioral_patterns(self, memories: Dict[str, List[Memory]]) -> List[Dict]:
        """Extract behavioral patterns from memories"""
        behavioral_memories = memories.get("behavioral", [])
        return [memory.content for memory in behavioral_memories 
                if isinstance(memory.content, dict)]
    
    async def _store_emotional_memory(
        self,
        message: str,
        response: str,
        context: Dict
    ) -> None:
        """Store emotional memory of interaction"""
        emotional_memory = EmotionalMemory(
            emotion=self.state.emotional_state,
            intensity=self.state.influence,
            trigger=message,
            context={
                "response": response,
                "state": self.state.__dict__,
                **context
            },
            timestamp=datetime.now(),
            agent_id=self.name
        )
        
        self.emotional_history.append(emotional_memory)
        
        # Store in memory system
        await self.memory_manager.store_emotional_pattern(
            str(emotional_memory.emotion),
            emotional_memory.intensity,
            emotional_memory.trigger,
            emotional_memory.context
        )

class MemoryAwareTheoryAgent(TheoryAgent):
    """Theory agent with memory integration"""
    
    def __init__(self, name: str, theory_name: str, principles: List[str],
                 guidelines: List[str], llm_config: dict, memory_manager: MemoryManager):
        super().__init__(name, theory_name, principles, guidelines, llm_config)
        self.memory_manager = memory_manager
        self.insights: List[TheoryInsight] = []
    
    async def evaluate_response(
        self,
        message: str,
        proposed_response: str,
        context: Dict
    ) -> Dict:
        """Evaluate response with memory-based insights"""
        # Get relevant memories
        memories = await self.memory_manager.get_relevant_memories(message, context)
        
        # Analyze with theory considering memories
        evaluation = await self._analyze_with_memories(
            message, proposed_response, context, memories
        )
        
        # Store theory insight
        await self._store_theory_insight(evaluation, context)
        
        return evaluation
    
    async def _analyze_with_memories(
        self,
        message: str,
        response: str,
        context: Dict,
        memories: Dict[str, List[Memory]]
    ) -> Dict:
        """Analyze interaction using memories and theory"""
        try:
            # Create analysis prompt with memory context
            prompt = f"""Analyze this interaction using {self.theory_name}:
            Message: {message}
            Proposed Response: {response}
            
            Recent Emotional Patterns:
            {self._format_emotional_patterns(memories)}
            
            Past Interactions:
            {self._format_interaction_history(memories)}
            
            Consider:
            1. How does this interaction align with past patterns?
            2. Does it follow theoretical principles?
            3. What improvements are suggested by the theory?
            
            Provide analysis as JSON with 'alignment_score' and 'recommendations'."""
            
            # Get analysis from LLM
            response = await self._analyze_alignment(message, response)
            
            return {
                "theory_name": self.theory_name,
                "alignment_score": response.get("alignment_score", 0.5),
                "suggestions": response.get("recommendations", []),
                "memory_based_insights": response.get("pattern_insights", [])
            }
            
        except Exception as e:
            print(f"Error in theory analysis: {str(e)}")
            return {
                "theory_name": self.theory_name,
                "alignment_score": 0.5,
                "suggestions": ["Error in analysis"],
                "memory_based_insights": []
            }
    
    def _format_emotional_patterns(self, memories: Dict[str, List[Memory]]) -> str:
        """Format emotional patterns for analysis"""
        emotional_memories = memories.get("emotional", [])
        patterns = []
        
        for memory in emotional_memories:
            if isinstance(memory.content, dict):
                patterns.append(
                    f"- {memory.content.get('emotion')} "
                    f"(intensity: {memory.content.get('intensity')}) "
                    f"triggered by: {memory.content.get('trigger')}"
                )
        
        return "\n".join(patterns) if patterns else "No emotional patterns found."
    
    def _format_interaction_history(self, memories: Dict[str, List[Memory]]) -> str:
        """Format interaction history for analysis"""
        episodic_memories = memories.get("episodic", [])
        interactions = []
        
        for memory in episodic_memories:
            if isinstance(memory.content, dict):
                interactions.append(
                    f"- User: {memory.content.get('message')}\n"
                    f"  Response: {memory.content.get('response')}"
                )
        
        return "\n".join(interactions) if interactions else "No interaction history found."
    
    async def _store_theory_insight(self, evaluation: Dict, context: Dict) -> None:
        """Store theory-based insight"""
        insight = TheoryInsight(
            theory_name=self.theory_name,
            pattern_observed=evaluation.get("memory_based_insights", [""])[0],
            recommendation=evaluation.get("suggestions", [""])[0],
            confidence=evaluation.get("alignment_score", 0.5),
            context=context,
            timestamp=datetime.now()
        )
        
        self.insights.append(insight)
        
        # Store in memory system as semantic memory
        await self.memory_manager.storage.store_memory(
            content={
                "theory": self.theory_name,
                "pattern": insight.pattern_observed,
                "recommendation": insight.recommendation,
                "confidence": insight.confidence
            },
            memory_type=MemoryType.SEMANTIC,
            priority=MemoryPriority.MEDIUM,
            context=context
        )

class MemoryAwareControlRoom(ControlRoom):
    """Control room with memory integration"""
    
    def __init__(self, emotional_agents: List[EmotionalAgent], 
                 theory_agents: List[TheoryAgent],
                 memory_manager: MemoryManager):
        super().__init__(emotional_agents, theory_agents)
        self.memory_manager = memory_manager
        
    async def process_input(self, message: str, context: Dict) -> str:
        """Process input with memory-aware control"""
        # Get relevant memories
        memories = await self.memory_manager.get_relevant_memories(message, context)
        
        # Determine dominant emotion considering memory patterns
        dominant_emotion = await self._determine_dominant_emotion_with_memory(
            message, memories
        )
        
        # Transfer control if needed
        if (self.current_controller is None or 
            dominant_emotion != self.current_controller.emotion):
            await self._transfer_control_with_memory(dominant_emotion, memories)
        
        # Generate response from current controller
        response = await self.current_controller.process_message(
            message,
            self._enhance_context_with_control_history(context, memories)
        )
        
        # Store control room state
        await self._store_control_state(message, response, dominant_emotion)
        
        return response
    
    async def _determine_dominant_emotion_with_memory(
        self,
        message: str,
        memories: Dict[str, List[Memory]]
    ) -> EmotionalState:
        """Determine dominant emotion using memory patterns"""
        # Extract recent emotional patterns
        emotional_patterns = []
        for memory in memories.get("emotional", []):
            if isinstance(memory.content, dict):
                emotional_patterns.append({
                    "emotion": memory.content.get("emotion"),
                    "intensity": memory.content.get("intensity"),
                    "trigger": memory.content.get("trigger")
                })
        
        # Consider patterns in emotion selection
        selected_emotion = await self._determine_dominant_emotion(message)
        
        # Modify selection based on patterns if needed
        if emotional_patterns:
            # Implementation of pattern-based modification
            pass
        
        return selected_emotion
    
    async def _transfer_control_with_memory(
        self,
        new_emotion: EmotionalState,
        memories: Dict[str, List[Memory]]
    ) -> None:
        """Transfer control with memory awareness"""
        if self.current_controller:
            # Store previous control state
            await self._store_control_transfer(
                self.current_controller.emotion,
                new_emotion,
                memories
            )
            
            # Adjust influence based on past patterns
            self.current_controller.state.influence *= self._calculate_influence_decay(
                memories
            )
        
        # Transfer control
        await self._transfer_control(new_emotion)
    
    def _calculate_influence_decay(self, memories: Dict[str, List[Memory]]) -> float:
        """Calculate influence decay based on memory patterns"""
        # Default decay
        decay = 0.8
        
        # Modify based on emotional patterns
        emotional_memories = memories.get("emotional", [])
        if emotional_memories:
            # Implementation of pattern-based modification
            pass
        
        return decay
    
    def _enhance_context_with_control_history(
        self,
        context: Dict,
        memories: Dict[str, List[Memory]]
    ) -> Dict:
        """Enhance context with control history"""
        return {
            **context,
            "control_history": self.state_history,
            "emotional_patterns": self._extract_emotional_patterns(memories)
        }
    
    async def _store_control_state(
        self,
        message: str,
        response: str,
        emotion: EmotionalState
    ) -> None:
        """Store control room state"""
        await self.memory_manager.storage.store_memory(
            content={
                "message": message,
                "response": response,
                "controlling_emotion": str(emotion),
                "emotional_states": {
                    str(e): agent.state.influence 
                    for e, agent in self.emotional_agents.items()
                }
            },
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.MEDIUM,
            context={"interaction_type": "control_transfer"}
        )