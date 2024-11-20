import autogen

from typing import Dict, List

from ..base_agents import EmotionalResponse, TheoryValidation
from ..theories.base_theory_agent import TheoryAgent

class TheoryCouncil:
    def __init__(self, theory_agents: List[TheoryAgent], llm_config: dict):
        # Convert theory agents to autogen AssistantAgents
        
        # Create user proxy to initiate discussions
        self.user_proxy = autogen.UserProxyAgent(
            name="TheoryCoordinator",
            system_message="Coordinator for theory validation discussions",
            human_input_mode="NEVER"
        )
        
        # Initialize the group chat
        self.group_chat = autogen.GroupChat(
            agents=[self.user_proxy] + theory_agents,
            messages=[],
            max_round=5  # Adjust as needed
        )
        
        # Create group chat manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config
        )
    

    async def validate(
        self, 
        message: str, 
        emotional_responses: List[EmotionalResponse],
        context: dict
    ) -> TheoryValidation:
        # Prepare the initial message for discussion
        initial_message = self._create_validation_prompt(message, emotional_responses, context)
        
        # Initiate the group chat discussion
        chat_result = self.user_proxy.initiate_chat(
            self.manager,
            message=initial_message
        )
        
        # Extract and synthesize the validations from the chat result
        return self._synthesize_validations(chat_result)

    def _create_validation_prompt(
        self,
        message: str,
        emotional_responses: List[EmotionalResponse],
        context: dict
    ) -> str:
        """Create the initial prompt for the theory validation discussion"""
        return f"""
        Please analyze this interaction based on your theoretical framework:
        
        User Message: {message}
        
        Emotional Responses: {emotional_responses}
        
        Context: {context}
        
        Each theory agent should:
        1. Evaluate how well the interaction aligns with your theory
        2. Provide specific recommendations based on your theoretical framework
        3. Assign a confidence score (0-1) to your analysis
        
        Discuss and reach a consensus on the best theoretical approach.
        """
    
    def _synthesize_validations(self, chat_result: Dict) -> TheoryValidation:
        """Convert the group chat results into a TheoryValidation object"""
        # You'll need to implement the logic to extract relevant information
        # from the chat_result and create a TheoryValidation object
        return [TheoryValidation(
            theory_name="Social Penetration Theory",
            alignment_score=0.5,
            suggestions=["Consider social events"],
            concerns=["Lack of social events"],
            modifications=["Adjust social events"],
            rationale="Social events align with theory"
        )]