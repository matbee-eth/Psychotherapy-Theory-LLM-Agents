
import asyncio
import logging

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from interactions.interaction_context import InteractionContext, InteractionContextManager
from memory.enhanced_memory_system import MemoryManager
from personality_framework import PersonalityFramework
from base_agents import EmotionalState
from state_management import StateManager

from agent_memory_integration import (
    MemoryAwareEmotionalAgent,
    MemoryAwareTheoryAgent,
    MemoryAwareControlRoom
)

@dataclass
class SystemConfig:
    """Configuration for the integrated system"""
    llm_config: dict
    memory_config: Optional[dict] = None
    personality_config: Optional[dict] = None
    state_config: Optional[dict] = None

class IntegratedSystem:
    """Main system integration layer"""
    
    def __init__(self, config: SystemConfig):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialize core components
        self.memory_manager = MemoryManager(config.llm_config)
        self.personality = PersonalityFramework()
        self.state_manager = StateManager()
        self.context_manager = InteractionContextManager()
        
        # Initialize emotional agents with memory awareness
        self.emotional_agents = self._initialize_emotional_agents(config)
        
        # Initialize theory agents with memory awareness
        self.theory_agents = self._initialize_theory_agents(config)
        
        # Initialize memory-aware control room
        self.control_room = MemoryAwareControlRoom(
            emotional_agents=self.emotional_agents,
            theory_agents=self.theory_agents,
            memory_manager=self.memory_manager
        )
        
        self.logger.info("Integrated system initialized successfully")
    
    def _initialize_emotional_agents(self, config: SystemConfig) -> List[MemoryAwareEmotionalAgent]:
        """Initialize memory-aware emotional agents"""
        emotional_agents = []
        
        # Create agents for each emotional state
        emotions = [
            (EmotionalState.HAPPY, "joy"),
            (EmotionalState.SAD, "sadness"),
            (EmotionalState.ANGRY, "anger"),
            (EmotionalState.ANXIOUS, "anxiety"),
            (EmotionalState.NEUTRAL, "neutral")
        ]
        
        for emotion, name in emotions:
            agent = MemoryAwareEmotionalAgent(
                name=name,
                emotion=emotion,
                personality=self.personality,
                llm_config=config.llm_config,
                memory_manager=self.memory_manager
            )
            emotional_agents.append(agent)
        
        return emotional_agents
    
    def _initialize_theory_agents(self, config: SystemConfig) -> List[MemoryAwareTheoryAgent]:
        """Initialize memory-aware theory agents"""
        theory_configs = [
            {
                "name": "social_penetration",
                "theory_name": "Social Penetration Theory",
                "principles": [
                    "Relationships develop through self-disclosure",
                    "Disclosure moves from shallow to deep",
                    "Reciprocity is key to development"
                ],
                "guidelines": [
                    "Match disclosure level",
                    "Progress gradually",
                    "Maintain appropriate intimacy"
                ]
            },
            {
                "name": "attachment",
                "theory_name": "Attachment Theory",
                "principles": [
                    "Early attachments influence relationship patterns",
                    "Secure attachment enables healthy relationships",
                    "Consistency builds trust"
                ],
                "guidelines": [
                    "Provide consistent responses",
                    "Acknowledge emotions",
                    "Offer appropriate support"
                ]
            }
        ]
        
        theory_agents = []
        for config in theory_configs:
            agent = MemoryAwareTheoryAgent(
                name=config["name"],
                theory_name=config["theory_name"],
                principles=config["principles"],
                guidelines=config["guidelines"],
                llm_config=config.llm_config,
                memory_manager=self.memory_manager
            )
            theory_agents.append(agent)
        
        return theory_agents
    
    async def process_interaction(self, message: str) -> Dict[str, Any]:
        """Process a single interaction through the integrated system"""
        try:
            # Create interaction context
            context = self.context_manager.create_context(message)
            self.logger.info(f"Processing interaction {context.message_id}")
            
            # Get relevant memories
            memories = await self.memory_manager.get_relevant_memories(
                message,
                self._create_memory_context(context)
            )
            context.relevant_memories = memories
            
            # Process through control room
            response = await self.control_room.process_input(
                message,
                self._create_control_context(context)
            )
            
            # Update state
            state_update = await self._update_system_state(context, response)
            
            # Store interaction memory
            await self._store_interaction_memory(context, response, state_update)
            
            # Prepare result
            result = self._prepare_interaction_result(
                context, response, state_update
            )
            
            self.logger.info(f"Interaction {context.message_id} processed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing interaction: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _create_memory_context(self, context: InteractionContext) -> Dict:
        """Create context for memory retrieval"""
        return {
            "message": context.raw_message,
            "current_state": self.state_manager.get_state(),
            "personality": self.personality.get_response_context(),
            "timestamp": context.timestamp
        }
    
    def _create_control_context(self, context: InteractionContext) -> Dict:
        """Create context for control room"""
        return {
            "message": context.raw_message,
            "memories": context.relevant_memories,
            "current_state": self.state_manager.get_state(),
            "personality": self.personality.get_response_context(),
            "interaction_history": context.interaction_history
        }
    
    async def _update_system_state(
        self,
        context: InteractionContext,
        response: str
    ) -> Dict[str, Any]:
        """Update system state based on interaction"""
        # Get current emotional state from control room
        current_emotion = self.control_room.current_controller.emotion
        
        # Update personality framework
        personality_update = self.personality.process_interaction(
            message_content=context.raw_message,
            sentiment_score=0.0,  # Would come from sentiment analysis
            interaction_quality=0.8,  # Would be calculated
            shared_interests=[],  # Would be extracted
            time_elapsed=datetime.now() - self.personality.state.last_interaction
        )
        
        # Update state manager
        state_update = self.state_manager.process_interaction(
            interaction_quality=0.8,  # Would be calculated
            shared_interests=[],  # Would be extracted
            emotional_depth=0.5,  # Would be calculated
            self_disclosure_level=0.5  # Would be calculated
        )
        
        return {
            "personality": personality_update,
            "state": state_update,
            "emotional_state": current_emotion
        }
    
    async def _store_interaction_memory(
        self,
        context: InteractionContext,
        response: str,
        state_update: Dict[str, Any]
    ) -> None:
        """Store interaction in memory system"""
        await self.memory_manager.store_interaction(
            message=context.raw_message,
            response=response,
            context={
                "state_update": state_update,
                "interaction_id": context.message_id,
                "timestamp": context.timestamp
            }
        )
    
    def _prepare_interaction_result(
        self,
        context: InteractionContext,
        response: str,
        state_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare final result of interaction"""
        return {
            "message_id": context.message_id,
            "response": response,
            "emotional_state": str(self.control_room.current_controller.emotion),
            "state_changes": {
                "personality": state_update["personality"],
                "relationship": state_update["state"]
            },
            "status": "success"
        }
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

# Example usage
async def main():
    # Create system configuration
    config = SystemConfig(
        llm_config={
            "temperature": 0.7,
            "max_tokens": 800,
            "model": "gpt-4"
        }
    )
    
    # Initialize integrated system
    system = IntegratedSystem(config)
    
    # Test interaction
    result = await system.process_interaction(
        "I've been feeling anxious about my new job, but I'm excited about the opportunity."
    )
    
    print("Interaction Result:", result)

if __name__ == "__main__":
    asyncio.run(main())