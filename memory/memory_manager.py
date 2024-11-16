from typing import Dict, List, Any
from datetime import datetime
import json
import autogen

from enhanced_memory_system import Memory, MemoryType
from interaction_context import InteractionContext
from state_management import GeneratedResponse

class MemoryAwareResponseGenerator:
    """Generates responses with awareness of past interactions and patterns"""
    
    def __init__(self, llm_config: dict):
        self.llm_config = llm_config
        
        # Initialize specialized LLM agent for response generation
        self.generation_agent = autogen.AssistantAgent(
            name="response_generator",
            llm_config=llm_config,
            system_message="""You are an expert at generating contextually appropriate 
            responses that incorporate past experiences and maintain consistent personality 
            traits. You reference relevant memories naturally while maintaining 
            conversational flow."""
        )
        
        # Response generation prompt template
        self.generation_prompt = """Generate a response considering the following context:

MESSAGE: {message}

ANALYSIS:
{analysis}

RELEVANT MEMORIES:
Emotional Patterns:
{emotional_memories}

Past Interactions:
{episodic_memories}

User Preferences/Behaviors:
{behavioral_memories}

CURRENT STATE:
{current_state}

Generate a response that:
1. Maintains emotional consistency
2. References relevant past interactions naturally
3. Shows understanding of user's patterns
4. Aligns with relationship stage
5. Demonstrates appropriate self-disclosure

Provide response in JSON format with:
1. content: The actual response
2. confidence: Float 0-1
3. emotion: Primary emotion expressed
4. memory_references: List of memory IDs referenced
5. reasoning: Explanation of response choices"""
    
    async def generate_response(
        self,
        context: InteractionContext,
        current_state: Dict[str, Any]
    ) -> GeneratedResponse:
        """Generate a response using available context and memories"""
        try:
            # Format memories for prompt
            emotional_summary = self._summarize_emotional_memories(
                context.relevant_memories.get("emotional", [])
            )
            
            episodic_summary = self._summarize_episodic_memories(
                context.relevant_memories.get("episodic", [])
            )
            
            behavioral_summary = self._summarize_behavioral_memories(
                context.relevant_memories.get("behavioral", [])
            )
            
            # Create generation prompt
            prompt = self.generation_prompt.format(
                message=context.raw_message,
                analysis=json.dumps(context.message_analysis.__dict__, indent=2),
                emotional_memories=emotional_summary,
                episodic_memories=episodic_summary,
                behavioral_memories=behavioral_summary,
                current_state=json.dumps(current_state, indent=2)
            )
            
            # Generate response
            response_json = await self._generate_response_with_llm(prompt)
            
            # Create response object
            return GeneratedResponse(
                content=response_json["content"],
                confidence=response_json["confidence"],
                emotion=response_json["emotion"],
                memory_references=response_json["memory_references"],
                reasoning=response_json["reasoning"]
            )
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return self._create_fallback_response()
    
    def _summarize_emotional_memories(self, memories: List[Memory]) -> str:
        """Create a summary of emotional patterns from memories"""
        if not memories:
            return "No significant emotional patterns found."
            
        summary_parts = []
        for memory in memories:
            if isinstance(memory.content, dict):
                summary_parts.append(
                    f"- {memory.content.get('emotion', 'unknown')} "
                    f"(intensity: {memory.content.get('intensity', 0)}) "
                    f"in response to {memory.content.get('trigger', 'unknown')}"
                )
        
        return "\n".join(summary_parts) if summary_parts else "No emotional patterns found."
    
    def _summarize_episodic_memories(self, memories: List[Memory]) -> str:
        """Create a summary of relevant past interactions"""
        if not memories:
            return "No relevant past interactions found."
            
        summary_parts = []
        for memory in memories:
            if isinstance(memory.content, dict):
                summary_parts.append(
                    f"- User: {memory.content.get('message', '')}\n"
                    f"  Response: {memory.content.get('response', '')}\n"
                    f"  Context: {memory.content.get('interaction_type', 'conversation')}"
                )
        
        return "\n".join(summary_parts) if summary_parts else "No past interactions found."
    
    def _summarize_behavioral_memories(self, memories: List[Memory]) -> str:
        """Create a summary of user preferences and behaviors"""
        if not memories:
            return "No established behavioral patterns."
            
        summary_parts = []
        for memory in memories:
            if isinstance(memory.content, dict):
                summary_parts.append(
                    f"- {memory.content.get('preference_type', 'preference')}: "
                    f"{memory.content.get('value', 'unknown')}"
                )
        
        return "\n".join(summary_parts) if summary_parts else "No behavioral patterns found."
    
    async def _generate_response_with_llm(self, prompt: str) -> Dict[str, Any]:
        """Generate response using LLM"""
        try:
            response = await self.generation_agent.generate_response(prompt)
            return json.loads(response)
            
        except json.JSONDecodeError:
            print("Error parsing LLM response as JSON")
            return self._create_fallback_response().__dict__
            
        except Exception as e:
            print(f"Error in LLM response generation: {str(e)}")
            return self._create_fallback_response().__dict__
    
    def _create_fallback_response(self) -> GeneratedResponse:
        """Create a safe fallback response"""
        return GeneratedResponse(
            content="I understand. Could you tell me more about that?",
            confidence=0.5,
            emotion="neutral",
            memory_references=[],
            reasoning="Fallback response due to error in generation"
        )

# Example usage
async def test_memory_response_generator():
    # Initialize with LLM config
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 800,
        "model": "gpt-4"
    }
    
    generator = MemoryAwareResponseGenerator(llm_config)
    
    # Create test memories
    test_memories = {
        "emotional": [
            Memory(
                id="em1",
                type=MemoryType.EMOTIONAL,
                content={
                    "emotion": "anxiety",
                    "intensity": 0.7,
                    "trigger": "work discussions"
                },
                timestamp=datetime.now(),
                priority=2,
                last_accessed=datetime.now()
            )
        ],
        "episodic": [
            Memory(
                id="ep1",
                type=MemoryType.EPISODIC,
                content={
                    "message": "I'm worried about my presentation tomorrow",
                    "response": "It's natural to feel nervous. Remember how well you handled the last presentation?",
                    "interaction_type": "emotional_support"
                },
                timestamp=datetime.now(),
                priority=2,
                last_accessed=datetime.now()
            )
        ],
        "behavioral": [
            Memory(
                id="bh1",
                type=MemoryType.BEHAVIORAL,
                content={
                    "preference_type": "communication_style",
                    "value": "prefers detailed explanations"
                },
                timestamp=datetime.now(),
                priority=2,
                last_accessed=datetime.now()
            )
        ]
    }
    
    # Create test context
    context = InteractionContext(
        message_id="test1",
        timestamp=datetime.now(),
        raw_message="I have another big presentation coming up and I'm feeling stressed.",
        relevant_memories=test_memories
    )
    
    # Test response generation
    current_state = {
        "trust_level": 0.7,
        "relationship_stage": "friend",
        "emotional_state": "supportive"
    }
    
    response = await generator.generate_response(context, current_state)
    
    print("Generated Response:", json.dumps(response.__dict__, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_memory_response_generator())