import autogen

from typing import Dict, Optional
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent

from controlroom.controlroom import ControlRoom
from emotions.base_emotion_agent import EmotionalAgent

class AutoGenControlRoom:
    """Enhanced ControlRoom using AutoGen's SocietyOfMindAgent pattern"""
    
    def __init__(
        self,
        control_room: ControlRoom,
        llm_config: dict,
        persona_name: str = "Alex"
    ):
        self.control_room = control_room
        self.llm_config = llm_config
        self.persona_name = persona_name
        
        # Initialize the agents and chat structure
        self._setup_agents()
        self._setup_chat()
        # self._setup_society()
    
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
        return f"""You are the {agent.emotion.value} aspect of {self.persona_name}'s personality.

Your current state:
- Emotion: {agent.emotion.value}
- Confidence: {agent.state.confidence:.2f}
- Influence: {agent.state.influence:.2f}
- Energy: {agent.state.energy:.2f}

{self.persona_name}'s personality traits:
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
                self.manager,
                message=prompt
            )
            
            # Extract dialogue  
            dialogue = []
            for agent, messages in self.manager.chat_messages.items():
                for msg in messages:
                    if msg.get("role") in ["assistant"]:
                        name = msg.get("name", "unknown")
                        content = msg.get("content", "").replace("TERMINATE", "").strip()
                        dialogue.append(f"{name}: {content}")
                        # print(f"{name}: {content}")

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
            import traceback
            print(f"Error in AutoGenControlRoom process_input: {str(e)}")
            print("Stack trace:") 
            print(traceback.format_exc())
            return {
                "response": "I understand. Could you tell me more about that?",
                "dialogue": [],
                "raw_messages": []
            }
