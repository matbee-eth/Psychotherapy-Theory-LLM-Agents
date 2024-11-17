import asyncio
import logging
import json

from typing import Dict, List, Any
from datetime import datetime

from interaction_context import (
    InteractionContext, 
    InteractionContextManager,
    MessageAnalysis
)
from memory.memory_manager import MemoryAwareResponseGenerator
from message_analyzer_llm import (
    MessageAnalyzer,
    ContextEnricher,
    TheoryIntegrator
)

from state_management import GeneratedResponse
from state_management import StateManager
from base_agents import EmotionalAgent, ControlRoom

class InteractionManager:
    """Orchestrates all components of the interaction system"""
    
    def __init__(self, llm_config: dict):
        # Initialize components
        self.context_manager = InteractionContextManager()
        self.message_analyzer = MessageAnalyzer(llm_config)
        self.context_enricher = ContextEnricher(llm_config)
        self.theory_integrator = TheoryIntegrator(llm_config)
        self.response_generator = MemoryAwareResponseGenerator(llm_config)
        self.state_manager = StateManager()
        
        # Initialize control room with emotional agents
        self.control_room = ControlRoom(
            emotional_agents=self._initialize_emotional_agents(llm_config),
            theory_agents=self._initialize_theory_agents(llm_config)
        )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Interaction metrics
        self.metrics = {
            "total_interactions": 0,
            "average_response_time": 0,
            "successful_interactions": 0,
            "failed_interactions": 0
        }
    
    async def process_interaction(self, message: str) -> Dict[str, Any]:
        """Process a single interaction from start to finish"""
        interaction_start = datetime.now()
        
        try:
            # Create interaction context
            context = self.context_manager.create_context(message)
            self.logger.info(f"Processing interaction {context.message_id}")
            
            # Step 1: Analyze message
            analysis = await self._analyze_message(message, context)
            context.message_analysis = analysis
            
            # Step 2: Update state based on analysis
            state_update = await self._update_state(analysis, context)
            context.current_state = state_update
            
            # Step 3: Generate and select response
            response = await self._generate_response(context)
            
            # Step 4: Update control room state
            await self._update_control_room(context, response)
            
            # Step 5: Finalize interaction
            result = await self._finalize_interaction(
                context, response, interaction_start
            )
            
            # Update metrics
            self._update_metrics(True, interaction_start)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing interaction: {str(e)}")
            self._update_metrics(False, interaction_start)
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def _analyze_message(
        self,
        message: str,
        context: InteractionContext
    ) -> MessageAnalysis:
        """Perform comprehensive message analysis"""
        try:
            # Get base analysis
            analysis = await self.message_analyzer.analyze_message(message)
            
            # Enrich with context
            enrichment = await self.context_enricher.enrich_analysis(
                message,
                analysis,
                context.interaction_history
            )
            
            # Integrate psychological theories
            theory_insights = await self.theory_integrator.integrate_theories(
                analysis,
                self.state_manager.get_active_theories()
            )
            
            # Log analysis results
            self.logger.debug(f"Message analysis completed for {context.message_id}")
            context.add_processing_step("Message analysis completed")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in message analysis: {str(e)}")
            raise
    
    async def _update_state(
        self,
        analysis: MessageAnalysis,
        context: InteractionContext
    ) -> Dict:
        """Update system state based on message analysis"""
        try:
            # Calculate interaction metrics
            interaction_quality = self._calculate_interaction_quality(analysis)
            shared_interests = self._extract_shared_interests(analysis)
            emotional_depth = analysis.emotional_intensity
            
            # Update state
            state_update = self.state_manager.process_interaction(
                interaction_quality=interaction_quality,
                shared_interests=shared_interests,
                emotional_depth=emotional_depth,
                self_disclosure_level=analysis.disclosure_level
            )
            
            # Log state update
            self.logger.debug(f"State updated for {context.message_id}")
            context.add_processing_step("State update completed")
            
            return state_update
            
        except Exception as e:
            self.logger.error(f"Error updating state: {str(e)}")
            raise
    
    async def _generate_response(
        self,
        context: InteractionContext
    ) -> GeneratedResponse:
        """Generate appropriate response"""
        try:
            # Generate response using response generator
            response = await self.response_generator.generate_response(
                context,
                self.state_manager
            )
            
            # Log response generation
            self.logger.debug(f"Response generated for {context.message_id}")
            context.add_processing_step("Response generation completed")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    async def _update_control_room(
        self,
        context: InteractionContext,
        response: GeneratedResponse
    ) -> None:
        """Update control room state"""
        try:
            # Process input through control room
            await self.control_room.process_input(
                context.raw_message,
                {
                    "analysis": context.message_analysis,
                    "state": context.current_state,
                    "response": response
                }
            )
            
            # Log control room update
            self.logger.debug(f"Control room updated for {context.message_id}")
            context.add_processing_step("Control room update completed")
            
        except Exception as e:
            self.logger.error(f"Error updating control room: {str(e)}")
            raise
    
    async def _finalize_interaction(
        self,
        context: InteractionContext,
        response: GeneratedResponse,
        start_time: datetime
    ) -> Dict:
        """Finalize interaction and prepare result"""
        try:
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Finalize context
            context.finalize()
            self.context_manager.save_context(context)
            
            # Prepare result
            result = {
                "message_id": context.message_id,
                "response": response.content,
                "emotional_state": {
                    "controlling_emotion": context.controlling_emotion,
                    "emotional_states": context.emotional_states
                },
                "relationship_state": {
                    "stage": self.state_manager.get_state()["relationship_stage"],
                    "trust_level": self.state_manager.get_state()["variables"]["trust"].value
                },
                "processing_time": processing_time,
                "confidence": response.confidence,
                "status": "success"
            }
            
            # Log completion
            self.logger.info(f"Interaction {context.message_id} completed successfully")
            context.add_processing_step("Interaction completed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error finalizing interaction: {str(e)}")
            raise
    
    def _initialize_emotional_agents(
        self,
        llm_config: dict
    ) -> List[EmotionalAgent]:
        """Initialize emotional agents"""
        # Implementation from previous base_agents.py
        pass
    
    def _initialize_theory_agents(
        self,
        llm_config: dict
    ) -> List[EmotionalAgent]:
        """Initialize theory agents"""
        # Implementation from previous base_agents.py
        pass
    
    def _calculate_interaction_quality(
        self,
        analysis: MessageAnalysis
    ) -> float:
        """Calculate interaction quality score"""
        # Combine multiple factors
        sentiment_factor = (analysis.sentiment_score + 1) / 2  # Convert to 0-1
        disclosure_factor = analysis.disclosure_level
        certainty_factor = 1 - analysis.uncertainty_level
        
        return (sentiment_factor * 0.4 + 
                disclosure_factor * 0.3 + 
                certainty_factor * 0.3)
    
    def _extract_shared_interests(
        self,
        analysis: MessageAnalysis
    ) -> List[str]:
        """Extract shared interests from analysis"""
        return analysis.topics
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _update_metrics(
        self,
        success: bool,
        start_time: datetime
    ) -> None:
        """Update interaction metrics"""
        self.metrics["total_interactions"] += 1
        
        if success:
            self.metrics["successful_interactions"] += 1
        else:
            self.metrics["failed_interactions"] += 1
        
        # Update average response time
        processing_time = (datetime.now() - start_time).total_seconds()
        current_avg = self.metrics["average_response_time"]
        total = self.metrics["total_interactions"]
        self.metrics["average_response_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )

# Example usage
async def test_interaction_manager():
    # Initialize with LLM config
    llm_config = {
        "temperature": 0.7,
        "max_tokens": 800,
        "model": "gpt-4"  # Or your chosen model
    }
    
    manager = InteractionManager(llm_config)
    
    # Test interaction
    message = "I've been feeling anxious about my new job, but I'm excited about the opportunity."
    
    result = await manager.process_interaction(message)
    
    print("Interaction Result:", json.dumps(result, indent=2))
    print("\nMetrics:", json.dumps(manager.metrics, indent=2))

if __name__ == "__main__":
    asyncio.run(test_interaction_manager())