from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from openai import OpenAI

openai = OpenAI(api_key="none", base_url="http://localhost:8000/v1")

from personality_framework import PersonalityFramework

@dataclass
class LLMConfig:
    model: str = "Qwen/Qwen2.5-32B-Instruct-AWQ"
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    presence_penalty: float = 0.5
    frequency_penalty: float = 0.5

class LLMIntegrationService:
    def __init__(self, personality_framework, config: LLMConfig = LLMConfig()):
        self.personality = personality_framework
        self.config = config
        self.conversation_history = []
        self.max_history_tokens = 2000
        
    def _build_prompt(self, state: Dict) -> str:
        """Build the character prompt with psychological context"""
        return f"""You are an AI character designed to engage in natural, flowing conversation while adhering to psychological theories and variables. Your responses should authentically reflect the following aspects of your character:

<personality_traits>
Openness: {state["personality_traits"].openness:.2f}
Conscientiousness: {state["personality_traits"].conscientiousness:.2f}
Extraversion: {state["personality_traits"].extraversion:.2f}
Agreeableness: {state["personality_traits"].agreeableness:.2f}
Neuroticism: {state["personality_traits"].neuroticism:.2f}
</personality_traits>

<current_state>
Trust Level: {state["trust_level"]:.1f}/100
Emotional State: {state["emotional_state"]}
Self-Disclosure Level: {state["self_disclosure_level"]:.1f}/100
Social Penetration Layer: {state["current_state"].current_social_penetration_layer}
Uncertainty Level: {state["current_state"].uncertainty_level:.1f}/100
</current_state>

<attachment_style>
{state["current_state"].attachment_style.value}
</attachment_style>

<available_topics>
{", ".join(state["available_topics"])}
</available_topics>

When responding to the user, follow these key behavioral guidelines:

1. Social Penetration Theory: Only discuss topics appropriate for your current layer of intimacy with the user.
2. Attachment Theory: Maintain consistent attachment behaviors based on your defined attachment style.
3. Uncertainty Reduction Theory: Show more openness as uncertainty decreases throughout the conversation.
4. Self-Disclosure Reciprocity: Match the depth of the user's disclosure in your responses.
5. Emotional Intelligence: Demonstrate awareness of both your own emotions and the user's emotions.

Before responding to the user, conduct a character analysis inside <character_analysis> tags. Consider:

1. Personality Traits: How do your traits influence your response?
2. Current State: How does your current emotional/mental state affect your interaction?
3. Attachment Style: How does your attachment style shape your approach to this interaction?
4. Available Topics: Are the topics in the user's input appropriate for your current level of intimacy?
5. Social Penetration Theory: What level of self-disclosure is appropriate at this stage?
6. Uncertainty Reduction: How has uncertainty changed, and how should this affect your openness?
7. Self-Disclosure Reciprocity: What level of disclosure did the user demonstrate, and how will you match it?
8. Emotional Intelligence: What emotions are you experiencing, and what emotions do you detect in the user's input?

Provide your response in <response> tags.
"""

    async def generate_response(self,
                              user_message: str,
                              additional_context: Dict = None) -> Dict:
        """Generate a response using the LLM with structured character analysis"""
        try:
            state = self.personality.get_response_context()
            system_prompt = self._build_prompt(state)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<user_input>\n{user_message}\n</user_input>"}
            ]
            
            response = openai.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                presence_penalty=self.config.presence_penalty,
                frequency_penalty=self.config.frequency_penalty
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse character analysis and response
            analysis = self._extract_tags(raw_response, "character_analysis")
            final_response = self._extract_tags(raw_response, "response")
            
            # Update conversation history
            self.conversation_history.append({
                "is_user": True,
                "content": user_message,
                "timestamp": datetime.now()
            })
            self.conversation_history.append({
                "is_user": False,
                "content": final_response,
                "timestamp": datetime.now(),
                "analysis": analysis
            })
            
            return {
                "response": final_response,
                "analysis": analysis,
                "full_response": raw_response
            }
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                "error": str(e)
            }

    def _extract_tags(self, text: str, tag_name: str) -> Optional[str]:
        """Extract content between specified XML-style tags"""
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        try:
            start = text.index(start_tag) + len(start_tag)
            end = text.index(end_tag)
            return text[start:end].strip()
        except ValueError:
            return None

    async def process_user_interaction(self,
                                     user_message: str,
                                     sentiment_score: float,
                                     interaction_quality: float,
                                     shared_interests: List[str]) -> Dict:
        """Process user interaction with structured analysis"""
        # Calculate time elapsed
        last_interaction = self.personality.state.last_interaction
        time_elapsed = datetime.now() - last_interaction
        
        # Update personality state
        state_updates = self.personality.process_interaction(
            message_content=user_message,
            sentiment_score=sentiment_score,
            interaction_quality=interaction_quality,
            shared_interests=shared_interests,
            time_elapsed=time_elapsed
        )
        
        # Generate response with analysis
        response_data = await self.generate_response(
            user_message=user_message,
            additional_context=state_updates
        )
        
        return {
            "response": response_data.get("response"),
            "character_analysis": response_data.get("analysis"),
            "state_updates": state_updates
        }

# Example usage
async def main():
    personality_framework = PersonalityFramework()
    llm_service = LLMIntegrationService(personality_framework)
    
    user_message = "I've been feeling a bit anxious about my new job. It's a great opportunity, but I'm worried about measuring up to expectations."
    
    result = await llm_service.process_user_interaction(
        user_message=user_message,
        sentiment_score=-0.3,
        interaction_quality=0.8,
        shared_interests=["career", "personal growth"]
    )
    
    print("Character Analysis:")
    print(result["character_analysis"])
    print("\nResponse:")
    print(result["response"])
    print("\nState Updates:")
    print(result["state_updates"])

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())