import json
import autogen

from typing import Dict, List, Union, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from memoripy import MemoryManager, JSONStorage

class MemoryType(Enum):
    EPISODIC = "episodic"  # Specific interactions/events
    SEMANTIC = "semantic"   # General knowledge/facts about the user
    EMOTIONAL = "emotional" # Emotional patterns and responses
    BEHAVIORAL = "behavioral" # Behavior patterns and preferences

@dataclass
class Memory:
    """Base class for all memory types"""
    id: str
    content: Dict[str, Any]  # Raw memory content
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class MemoryStorageSystem:
    """Manages storage and retrieval of memories using memoripy"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        self.memories: Dict[str, Memory] = {}
        
        # Initialize memoripy MemoryManager
        self.memoripy_manager = MemoryManager(
            api_key=llm_config.get("api_key"),
            chat_model=llm_config.get("chat_model", "openai"),
            chat_model_name=llm_config.get("chat_model_name", "gpt-4"),
            embedding_model=llm_config.get("embedding_model", "openai"),
            embedding_model_name=llm_config.get("embedding_model_name", "text-embedding-ada-002"),
            storage=JSONStorage("memory_storage.json")
        )
        
        # Initialize LLM agent for memory processing
        self.memory_processor = autogen.AssistantAgent(
            name="memory_processor",
            llm_config=llm_config,
            system_message="""You are an expert at processing and analyzing memories,
            understanding their significance, and making meaningful connections between them.
            Consider psychological impact, personality development, and pattern formation.
            Process without predetermined categories - focus on raw significance and connections."""
        )
    
    async def store_memory(
        self,
        content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Store new memory with embedding"""
        try:
            # Process memory content with LLM
            processed_memory = await self._process_memory_content(content, context)
            
            # Create memory ID
            memory_id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create memory object
            memory = Memory(
                id=memory_id,
                content=processed_memory["content"],
                timestamp=datetime.now(),
                metadata={
                    **context,
                    "processing_result": processed_memory["analysis"]
                }
            )
            
            # Store memory in local dict
            self.memories[memory_id] = memory
            
            # Create combined text for embedding
            combined_text = json.dumps({
                "content": processed_memory["content"],
                "analysis": processed_memory["analysis"]
            })
            
            # Generate embedding and store in memoripy
            embedding = self.memoripy_manager.get_embedding(combined_text)
            concepts = self.memoripy_manager.extract_concepts(combined_text)
            
            self.memoripy_manager.add_interaction(
                prompt=memory_id,  # Use memory ID as reference
                response=combined_text,
                embedding=embedding,
                concepts=concepts
            )
            
            return memory_id
            
        except Exception as e:
            print(f"Error storing memory: {str(e)}")
            raise

    async def retrieve_memories(
        self,
        query: Union[str, Dict],
        limit: int = 5,
        min_similarity: float = 0.5
    ) -> List[Memory]:
        """Retrieve relevant memories using embedding similarity"""
        try:
            # Convert query to string if it's a dict
            query_str = query if isinstance(query, str) else json.dumps(query)
            
            # Get relevant interactions from memoripy
            relevant_interactions = self.memoripy_manager.retrieve_relevant_interactions(
                query_str,
                exclude_last_n=0,
                similarity_threshold=min_similarity
            )
            
            # Convert relevant interactions back to Memory objects
            memories = []
            for interaction in relevant_interactions[:limit]:
                memory_id = interaction.prompt  # Using memory ID stored as prompt
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    memories.append(memory)
            
            return memories
            
        except Exception as e:
            print(f"Error retrieving memories: {str(e)}")
            return []

    async def _process_memory_content(
        self,
        content: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process memory content using LLM"""
        try:
            # Create processing prompt
            prompt = f"""Analyze this memory content and context for psychological significance:

CONTENT:
{json.dumps(content, indent=2)}

CONTEXT:
{json.dumps(context, indent=2)}

Consider:
1. Psychological impact and meaning
2. Potential pattern development
3. Personality implications
4. Connection potential with other experiences

Provide analysis as open-ended JSON without predetermined categories."""
            
            # Get analysis from LLM
            response = await self.memory_processor.generate_response(prompt)
            analysis = json.loads(response)
            
            return {
                "content": content,
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"Error processing memory content: {str(e)}")
            return {
                "content": content,
                "analysis": {}
            }

    async def find_similar_experiences(
        self,
        experience: Dict[str, Any],
        min_similarity: float = 0.5,
        limit: int = 5
    ) -> List[Memory]:
        """Find similar past experiences using embedding similarity"""
        return await self.retrieve_memories(
            query=experience,
            limit=limit,
            min_similarity=min_similarity
        )

    async def find_connected_patterns(
        self,
        memory_ids: List[str],
        min_similarity: float = 0.7
    ) -> Dict[str, List[Memory]]:
        """Find patterns in connected memories"""
        try:
            pattern_memories = {}
            
            # Get base memories
            base_memories = [
                self.memories[mid] for mid in memory_ids 
                if mid in self.memories
            ]
            
            # Find similar memories for each base memory
            for memory in base_memories:
                similar = await self.retrieve_memories(
                    memory.content,
                    limit=10,
                    min_similarity=min_similarity
                )
                
                if similar:
                    pattern_memories[memory.id] = similar
            
            return pattern_memories
            
        except Exception as e:
            print(f"Error finding patterns: {str(e)}")
            return {}

# Example usage
async def test_memory_system():
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "model": "gpt-4",
        "api_key": "your-api-key"
    }
    
    memory_system = MemoryStorageSystem(llm_config)
    
    # Store a new memory
    content = {
        "type": "experience",
        "description": "First public speaking failure",
        "details": {
            "event": "presentation",
            "outcome": "negative",
            "emotional_response": "intense anxiety"
        }
    }
    
    context = {
        "situation": "professional",
        "significance": "high",
        "current_state": {
            "confidence": 0.7,
            "anxiety": 0.3
        }
    }
    
    memory_id = await memory_system.store_memory(content, context)
    
    # Find similar experiences
    similar = await memory_system.find_similar_experiences(content)
    
    print("\nStored Memory ID:", memory_id)
    print("\nSimilar Experiences:")
    for mem in similar:
        print(f"- {mem.id}: {mem.content.get('description', 'No description')}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_memory_system())