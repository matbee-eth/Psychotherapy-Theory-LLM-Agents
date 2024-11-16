from typing import Dict, List, Optional, Any
import autogen
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
from datetime import datetime

from base_agents import (
    EmotionalAgent, 
    TheoryAgent, 
    ControlRoom,
    PersonalityTraits,
    EmotionalState
)

class AutoGenEmotionalAgent(autogen.AssistantAgent):
    """Wrapper for EmotionalAgent to work with AutoGen"""
    
    def __init__(
        self,
        emotional_agent: EmotionalAgent,
        llm_config: dict
    ):
        system_message = self._create_system_message(emotional_agent)
        super().__init__(
            name=emotional_agent.name,
            system_message=system_message,
            llm_config=llm_config
        )
        self.emotional_agent = emotional_agent

    def _create_system_message(self, agent: EmotionalAgent) -> str:
        """Create system message incorporating emotional agent's characteristics"""
        return f"""You are the {agent.emotion.value} aspect of a personality system.
        Current State:
        - Confidence: {agent.state.confidence}
        - Influence: {agent.state.influence}
        - Energy: {agent.state.energy}
        
        Personality Traits:
        - Openness: {agent.personality.openness}
        - Conscientiousness: {agent.personality.conscientiousness}
        - Extraversion: {agent.personality.extraversion}
        - Agreeableness: {agent.personality.agreeableness}
        - Neuroticism: {agent.personality.neuroticism}
        
        Your role is to:
        1. Process messages from your emotional perspective
        2. Suggest responses that align with your emotional state
        3. Consider personality traits in your responses
        4. Maintain emotional consistency
        5. Interact with other emotional aspects
        
        Recent Memory Context:
        {self._format_recent_memory(agent.memory)}"""

    def _format_recent_memory(self, memory: List[Dict]) -> str:
        """Format recent memory for context"""
        if not memory:
            return "No recent interactions."
            
        memory_str = "Recent interactions:\n"
        for m in memory[-3:]:  # Last 3 memories
            memory_str += f"- {m['timestamp']}: {m['message'][:100]}...\n"
        return memory_str

from typing import Dict, Optional
import autogen
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent

class AutoGenControlRoom:
    """Enhanced ControlRoom using AutoGen's SocietyOfMindAgent pattern"""
    
    def __init__(
        self,
        control_room: ControlRoom,
        llm_config: dict
    ):
        self.control_room = control_room
        self.llm_config = llm_config
        
        # Initialize the agents and chat structure
        self._setup_agents()
        self._setup_chat()
        self._setup_society()
    
    def _setup_agents(self):
        """Create the assistant agents for each emotion"""
        # Create emotional assistants
        self.emotional_assistants = {}
        for emotion, agent in self.control_room.emotional_agents.items():
            # Create assistant for this emotion
            print("AutoGenControlRoom _setup_agents: Creating assistant for", emotion.value)
            assistant = autogen.AssistantAgent(
                name=f"{emotion.value}_agent",
                system_message=self._create_agent_system_message(agent),
                llm_config=self.llm_config,
                is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            )
            self.emotional_assistants[emotion] = assistant

        # Create user proxy
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda x: True
        )

    def _setup_chat(self):
        """Set up the group chat configuration"""
        # Create list of agents for group chat
        agents = list(self.emotional_assistants.values())
        print("Setting up group chat with agents:", agents)
        # Create group chat with specific configuration
        self.groupchat = autogen.GroupChat(
            agents=agents,
            messages=[],
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
            max_round=len(agents)  # One round per emotion
        )
        
        # Create group chat manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.llm_config,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0
        )

    def _setup_society(self):
        """Set up the Society of Mind agent"""
        self.society = SocietyOfMindAgent(
            name="emotional_society",
            chat_manager=self.manager,
            llm_config=self.llm_config
        )

    def _create_agent_system_message(self, agent: EmotionalAgent) -> str:
        """Create the system message for an emotional agent"""
        return f"""You are the {agent.emotion.value} aspect of Alex's personality.

Your current state:
- Emotion: {agent.emotion.value}
- Confidence: {agent.state.confidence:.2f}
- Influence: {agent.state.influence:.2f}
- Energy: {agent.state.energy:.2f}

Alex's personality traits:
- Openness: {agent.personality.openness:.2f}
- Conscientiousness: {agent.personality.conscientiousness:.2f}
- Extraversion: {agent.personality.extraversion:.2f}
- Agreeableness: {agent.personality.agreeableness:.2f}
- Neuroticism: {agent.personality.neuroticism:.2f}

Your role is to process messages from your emotional perspective. When responding:
1. Start with "As the {agent.emotion.value} aspect:"
2. Share how the message makes you feel from your emotional perspective
3. Suggest how to respond based on your emotional viewpoint
4. Explain your reasoning
5. Consider how your emotion interacts with others
"""

    async def process_input(self, message: str, context: Optional[Dict] = None) -> Dict:
        """Process input through emotional dialogue"""
        context = context or {}
        
        try:
            # Prepare the processing prompt
            prompt = f"""Process this message collaboratively through emotional perspectives.

MESSAGE: {message}

Each emotional aspect:
1. Share your emotional perspective
2. Suggest appropriate responses
3. Consider interactions with other emotions
4. Work towards an emotional consensus

Share your perspective."""
            
            # Clear previous messages
            self.groupchat.messages = []
            
            # Start the dialogue
            result = await self.user_proxy.a_initiate_chat(
                self.society,
                message=prompt
            )
            
            # Extract dialogue
            dialogue = []
            for msg in self.groupchat.messages:
                if msg["role"] == "assistant":
                    name = msg.get("name", "unknown")
                    content = msg["content"].replace("TERMINATE", "").strip()
                    dialogue.append(f"{name}: {content}")

            # Get final response through control room
            final_response = await self.control_room.process_input(
                message=message,
                context=context
            )
            
            return {
                "response": final_response,
                "dialogue": dialogue,
                "raw_messages": self.groupchat.messages
            }
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return {
                "response": "I understand. Could you tell me more about that?",
                "dialogue": [],
                "raw_messages": []
            }
