from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from enum import Enum
import autogen

class MemoryType(Enum):
    EPISODIC = "episodic"  # Specific interactions/events
    SEMANTIC = "semantic"   # General knowledge/facts about the user
    EMOTIONAL = "emotional" # Emotional patterns and responses
    BEHAVIORAL = "behavioral" # Behavior patterns and preferences

class MemoryPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Memory:
    """Base class for all memory types"""
    id: str
    type: MemoryType
    content: Dict[str, Any]
    timestamp: datetime
    priority: MemoryPriority
    last_accessed: datetime
    access_count: int = 0
    emotional_valence: float = 0.0  # -1 to 1
    associations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MemoryStorageSystem:
    """Manages storage and retrieval of memories"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.memories: Dict[str, Memory] = {}
        self.memory_embeddings: Dict[str, List[float]] = {}
        
        # Initialize LLM agent for memory processing
        self.memory_agent = autogen.AssistantAgent(
            name="memory_processor",
            llm_config=llm_config,
            system_message="""You are an expert at processing and analyzing memories,
            understanding their significance, and making meaningful connections between them.
            You help maintain a coherent and psychologically sound memory structure."""
        )
    
    async def store_memory(
        self,
        content: Dict[str, Any],
        memory_type: MemoryType,
        priority: MemoryPriority,
        context: Dict[str, Any]
    ) -> str:
        """Store a new memory with metadata"""
        try:
            # Process memory content
            processed_memory = await self._process_memory_content(content, context)
            
            # Create memory object
            memory_id = self._generate_memory_id()
            memory = Memory(
                id=memory_id,
                type=memory_type,
                content=processed_memory["content"],
                timestamp=datetime.now(),
                priority=priority,
                last_accessed=datetime.now(),
                emotional_valence=processed_memory["emotional_valence"],
                associations=processed_memory["associations"],
                tags=processed_memory["tags"],
                metadata=context
            )
            
            # Store memory
            self.memories[memory_id] = memory
            
            # Update embeddings
            self.memory_embeddings[memory_id] = await self._generate_embedding(memory)
            
            # Consolidate memories if needed
            await self._consolidate_memories()
            
            return memory_id
            
        except Exception as e:
            print(f"Error storing memory: {str(e)}")
            raise

    async def retrieve_memories(
        self,
        query: Union[str, Dict],
        memory_type: Optional[MemoryType] = None,
        limit: int = 5,
        min_relevance: float = 0.5
    ) -> List[Memory]:
        """Retrieve relevant memories based on query"""
        try:
            # Generate query embedding
            query_embedding = await self._generate_query_embedding(query)
            
            # Calculate relevance scores
            scored_memories = await self._score_memories(
                query_embedding,
                memory_type
            )
            
            # Filter and sort memories
            relevant_memories = [
                (memory, score) for memory, score in scored_memories
                if score >= min_relevance
            ]
            relevant_memories.sort(key=lambda x: x[1], reverse=True)
            
            # Update access metrics
            for memory, _ in relevant_memories[:limit]:
                self._update_access_metrics(memory)
            
            return [memory for memory, _ in relevant_memories[:limit]]
            
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            return []

    async def update_memory(
        self,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update an existing memory"""
        if memory_id not in self.memories:
            return False
            
        try:
            memory = self.memories[memory_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)
            
            # Update last accessed
            memory.last_accessed = datetime.now()
            
            # Update embedding if content changed
            if "content" in updates:
                self.memory_embeddings[memory_id] = await self._generate_embedding(memory)
            
            return True
            
        except Exception as e:
            print(f"Error updating memory: {str(e)}")
            return False

    async def _process_memory_content(
        self,
        content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process memory content to extract metadata"""
        try:
            # Create processing prompt
            prompt = f"""Analyze this memory content and context to extract:
            1. Emotional valence (-1 to 1)
            2. Key associations
            3. Relevant tags
            4. Enhanced content with psychological insights
            
            Content: {json.dumps(content)}
            Context: {json.dumps(context)}
            
            Provide analysis as JSON with these fields."""
            
            # Get analysis from LLM
            response = await self.memory_agent.generate_response(prompt)
            analysis = json.loads(response)
            
            return {
                "content": content | {"insights": analysis.get("insights", [])},
                "emotional_valence": analysis.get("emotional_valence", 0.0),
                "associations": analysis.get("associations", []),
                "tags": analysis.get("tags", [])
            }
            
        except Exception as e:
            print(f"Error processing memory content: {str(e)}")
            return {
                "content": content,
                "emotional_valence": 0.0,
                "associations": [],
                "tags": []
            }

    async def _generate_embedding(self, memory: Memory) -> List[float]:
        """Generate embedding for a memory"""
        # Implementation would use appropriate embedding model
        # For now, return placeholder
        return [0.0] * 128

    async def _generate_query_embedding(
        self,
        query: Union[str, Dict]
    ) -> List[float]:
        """Generate embedding for a query"""
        # Implementation would use appropriate embedding model
        # For now, return placeholder
        return [0.0] * 128

    async def _score_memories(
        self,
        query_embedding: List[float],
        memory_type: Optional[MemoryType]
    ) -> List[tuple[Memory, float]]:
        """Score memories based on relevance to query"""
        scored_memories = []
        
        for memory_id, memory in self.memories.items():
            # Filter by type if specified
            if memory_type and memory.type != memory_type:
                continue
            
            # Calculate relevance score
            embedding = self.memory_embeddings[memory_id]
            score = self._calculate_similarity(query_embedding, embedding)
            
            scored_memories.append((memory, score))
        
        return scored_memories

    def _calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between embeddings"""
        # Implementation would calculate actual similarity
        # For now, return placeholder
        return 0.5

    async def _consolidate_memories(self) -> None:
        """Consolidate and organize memories"""
        try:
            # Get memories to consolidate
            recent_memories = self._get_recent_memories(hours=24)
            
            if len(recent_memories) < 2:
                return
            
            # Create consolidation prompt
            prompt = f"""Analyze these recent memories for:
            1. Common patterns
            2. Related themes
            3. Psychological insights
            4. Potential consolidated memory
            
            Memories: {json.dumps([m.content for m in recent_memories])}
            
            Provide analysis as JSON with these fields."""
            
            # Get analysis from LLM
            response = await self.memory_agent.generate_response(prompt)
            analysis = json.loads(response)
            
            # Create consolidated memory if valuable
            if analysis.get("should_consolidate", False):
                await self.store_memory(
                    content=analysis["consolidated_memory"],
                    memory_type=MemoryType.SEMANTIC,
                    priority=MemoryPriority.MEDIUM,
                    context={"consolidated_from": [m.id for m in recent_memories]}
                )
                
        except Exception as e:
            print(f"Error consolidating memories: {str(e)}")

    def _get_recent_memories(self, hours: int = 24) -> List[Memory]:
        """Get memories from recent time period"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            memory for memory in self.memories.values()
            if memory.timestamp >= cutoff
        ]

    def _update_access_metrics(self, memory: Memory) -> None:
        """Update memory access metrics"""
        memory.last_accessed = datetime.now()
        memory.access_count += 1

    def _generate_memory_id(self) -> str:
        """Generate unique memory ID"""
        return f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.memories)}"

class MemoryManager:
    """High-level interface for memory operations"""
    
    def __init__(self, llm_config: dict):
        self.storage = MemoryStorageSystem(llm_config)
        self.llm_config = llm_config
    
    async def store_interaction(
        self,
        message: str,
        response: str,
        context: Dict[str, Any]
    ) -> str:
        """Store an interaction memory"""
        content = {
            "message": message,
            "response": response,
            "interaction_type": "dialogue"
        }
        
        return await self.storage.store_memory(
            content=content,
            memory_type=MemoryType.EPISODIC,
            priority=MemoryPriority.MEDIUM,
            context=context
        )
    
    async def store_emotional_pattern(
        self,
        emotion: str,
        intensity: float,
        trigger: str,
        context: Dict[str, Any]
    ) -> str:
        """Store an emotional pattern memory"""
        content = {
            "emotion": emotion,
            "intensity": intensity,
            "trigger": trigger,
            "pattern_type": "emotional_response"
        }
        
        return await self.storage.store_memory(
            content=content,
            memory_type=MemoryType.EMOTIONAL,
            priority=MemoryPriority.HIGH,
            context=context
        )
    
    async def store_user_preference(
        self,
        preference_type: str,
        value: Any,
        context: Dict[str, Any]
    ) -> str:
        """Store a user preference memory"""
        content = {
            "preference_type": preference_type,
            "value": value,
            "source": "observed_behavior"
        }
        
        return await self.storage.store_memory(
            content=content,
            memory_type=MemoryType.BEHAVIORAL,
            priority=MemoryPriority.MEDIUM,
            context=context
        )
    
    async def get_relevant_memories(
        self,
        current_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, List[Memory]]:
        """Get memories relevant to current interaction"""
        results = {}
        
        # Get episodic memories
        results["episodic"] = await self.storage.retrieve_memories(
            query=current_message,
            memory_type=MemoryType.EPISODIC
        )
        
        # Get emotional memories
        results["emotional"] = await self.storage.retrieve_memories(
            query=context.get("emotional_state", {}),
            memory_type=MemoryType.EMOTIONAL
        )
        
        # Get behavioral memories
        results["behavioral"] = await self.storage.retrieve_memories(
            query=context.get("behavioral_cues", {}),
            memory_type=MemoryType.BEHAVIORAL
        )
        
        return results

# Example usage
async def test_memory_system():
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 800,
        "model": "gpt-4"
    }
    
    memory_manager = MemoryManager(llm_config)
    
    # Store an interaction
    interaction_id = await memory_manager.store_interaction(
        message="I've been feeling anxious about my new job",
        response="That's understandable. Starting a new job can be stressful...",
        context={"emotional_state": "anxious", "trust_level": 0.6}
    )
    
    # Store an emotional pattern
    pattern_id = await memory_manager.store_emotional_pattern(
        emotion="anxiety",
        intensity=0.7,
        trigger="work-related changes",
        context={"situation": "new job discussion"}
    )
    
    # Get relevant memories
    memories = await memory_manager.get_relevant_memories(
        current_message="I'm worried about my job performance",
        context={"emotional_state": "anxious"}
    )
    
    print("Retrieved Memories:", json.dumps(
        {k: [m.content for m in v] for k, v in memories.items()},
        indent=2
    ))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_memory_system())