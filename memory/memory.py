import numpy as np

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from base_agents import EmotionalAgent, EmotionalState, PersonalityTraits

@dataclass
class MemoryEntry:
    timestamp: datetime
    content: str
    emotion: EmotionalState
    importance: float
    context: Dict
    tags: List[str]

class MemorySystem:
    """Manages short-term and long-term memory for emotional agents"""
    
    def __init__(self, max_short_term: int = 50, max_long_term: int = 1000):
        self.short_term_memory: List[MemoryEntry] = []
        self.long_term_memory: List[MemoryEntry] = []
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        
    def add_memory(self, entry: MemoryEntry) -> None:
        """Add new memory to short-term storage"""
        self.short_term_memory.append(entry)
        
        # Consolidate memories if short-term is full
        if len(self.short_term_memory) >= self.max_short_term:
            self._consolidate_memories()
    
    def get_relevant_memories(
        self,
        query: str,
        emotion: Optional[EmotionalState] = None,
        time_window: Optional[timedelta] = None,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """Retrieve relevant memories based on query and filters"""
        # Combine short and long-term memories for search
        all_memories = self.short_term_memory + self.long_term_memory
        
        # Apply filters
        filtered_memories = self._filter_memories(all_memories, emotion, time_window)
        
        # Calculate relevance scores
        scored_memories = self._score_memories(filtered_memories, query)
        
        # Return top relevant memories
        return sorted(scored_memories, key=lambda x: x[1], reverse=True)[:limit]
    
    def _consolidate_memories(self) -> None:
        """Move important memories to long-term storage"""
        # Sort by importance
        sorted_memories = sorted(
            self.short_term_memory,
            key=lambda x: x.importance,
            reverse=True
        )
        
        # Keep top memories in long-term
        memories_to_keep = sorted_memories[:self.max_long_term - len(self.long_term_memory)]
        self.long_term_memory.extend(memories_to_keep)
        
        # Clear short-term memory
        self.short_term_memory = []
    
    def _filter_memories(
        self,
        memories: List[MemoryEntry],
        emotion: Optional[EmotionalState],
        time_window: Optional[timedelta]
    ) -> List[MemoryEntry]:
        """Filter memories based on emotion and time window"""
        filtered = memories
        
        if emotion:
            filtered = [m for m in filtered if m.emotion == emotion]
            
        if time_window:
            cutoff = datetime.now() - time_window
            filtered = [m for m in filtered if m.timestamp >= cutoff]
            
        return filtered
    
    def _score_memories(
        self,
        memories: List[MemoryEntry],
        query: str
    ) -> List[Tuple[MemoryEntry, float]]:
        """Score memories based on relevance to query"""
        # Simple keyword matching for now
        # Could be enhanced with embedding similarity
        query_words = set(query.lower().split())
        scored_memories = []
        
        for memory in memories:
            content_words = set(memory.content.lower().split())
            score = len(query_words & content_words) / len(query_words)
            scored_memories.append((memory, score))
            
        return scored_memories

class JoyAgent(EmotionalAgent):
    """Leader emotion that coordinates emotional responses"""
    
    def __init__(
        self,
        name: str,
        personality: PersonalityTraits,
        llm_config: dict,
        memory_system: MemorySystem
    ):
        super().__init__(
            name=name,
            emotion=EmotionalState.HAPPY,
            personality=personality,
            llm_config=llm_config,
            system_message=self._create_system_message()
        )
        self.memory_system = memory_system
        self.leadership_score = 1.0  # Measure of current leadership effectiveness
        
    async def process_message(self, message: str, context: Dict) -> str:
        """Process message as the leader emotion"""
        # Get relevant memories
        relevant_memories = self.memory_system.get_relevant_memories(
            query=message,
            time_window=timedelta(hours=24)
        )
        
        # Update context with memories
        context["relevant_memories"] = relevant_memories
        
        # Generate leader response
        response = await self._generate_leader_response(message, context)
        
        # Store interaction in memory
        self._store_interaction(message, response, context)
        
        return response
    
    async def evaluate_control_transfer(
        self,
        message: str,
        emotional_states: Dict[EmotionalState, float]
    ) -> Tuple[bool, Optional[EmotionalState]]:
        """Evaluate whether control should be transferred to another emotion"""
        # Calculate leadership effectiveness
        self._update_leadership_score(emotional_states)
        
        # Determine if transfer is needed
        if self.leadership_score < 0.3:  # Leadership threshold
            # Find emotion with highest activation
            next_emotion = max(emotional_states.items(), key=lambda x: x[1])[0]
            if next_emotion != EmotionalState.HAPPY:
                return True, next_emotion
        
        return False, None
    
    def _create_system_message(self) -> str:
        """Create the system message for Joy as leader"""
        return """You are Joy, the leader emotion responsible for coordinating emotional responses.
        Key responsibilities:
        1. Maintain overall emotional well-being
        2. Guide interactions toward positive outcomes
        3. Delegate control when other emotions are more appropriate
        4. Ensure responses align with personality traits
        Remember to stay positive while acknowledging other emotional needs."""
    
    async def _generate_leader_response(self, message: str, context: Dict) -> str:
        """Generate response as the leader emotion"""
        # Implementation using LLM to generate leader response
        # This would integrate personality traits, emotional state, and memories
        pass
    
    def _store_interaction(self, message: str, response: str, context: Dict) -> None:
        """Store interaction in memory system"""
        importance = self._calculate_importance(message, response)
        
        memory_entry = MemoryEntry(
            timestamp=datetime.now(),
            content=f"User: {message}\nResponse: {response}",
            emotion=self.emotion,
            importance=importance,
            context=context,
            tags=self._extract_tags(message, response)
        )
        
        self.memory_system.add_memory(memory_entry)
    
    def _update_leadership_score(self, emotional_states: Dict[EmotionalState, float]) -> None:
        """Update leadership effectiveness score"""
        # Factors affecting leadership:
        # 1. Emotional balance
        balance = self._calculate_emotional_balance(emotional_states)
        
        # 2. Recent success (stored in state)
        recent_success = self.state.confidence
        
        # 3. Energy level
        energy = self.state.energy
        
        # Combine factors
        self.leadership_score = (balance * 0.4 + recent_success * 0.3 + energy * 0.3)
    
    def _calculate_emotional_balance(self, emotional_states: Dict[EmotionalState, float]) -> float:
        """Calculate how well-balanced the emotional states are"""
        values = list(emotional_states.values())
        return 1.0 - np.std(values)  # Higher score for more balanced states
    
    def _calculate_importance(self, message: str, response: str) -> float:
        """Calculate importance score for memory storage"""
        # Factors affecting importance:
        # 1. Emotional content
        # 2. Length of interaction
        # 3. Presence of key topics
        # For now, using a simple length-based heuristic
        total_length = len(message) + len(response)
        return min(1.0, total_length / 1000)
    
    def _extract_tags(self, message: str, response: str) -> List[str]:
        """Extract relevant tags from interaction"""
        # Implementation for tag extraction
        # Could use NLP techniques for better tag extraction
        combined_text = f"{message} {response}".lower()
        # Simple keyword-based tagging for now
        tags = []
        if "happy" in combined_text or "joy" in combined_text:
            tags.append("positive_emotion")
        if "sad" in combined_text or "angry" in combined_text:
            tags.append("negative_emotion")
        if "help" in combined_text or "support" in combined_text:
            tags.append("support_needed")
        return tags

# Example usage
def initialize_joy_system(llm_config: dict) -> Tuple[JoyAgent, MemorySystem]:
    # Create memory system
    memory_system = MemorySystem()
    
    # Create personality
    personality = PersonalityTraits(
        openness=0.75,
        conscientiousness=0.8,
        extraversion=0.6,
        agreeableness=0.7,
        neuroticism=0.3
    )
    
    # Create Joy agent
    joy_agent = JoyAgent(
        name="joy",
        personality=personality,
        llm_config=llm_config,
        memory_system=memory_system
    )
    
    return joy_agent, memory_system