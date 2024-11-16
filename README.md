# Persona Bot

An emotionally intelligent conversational agent system that combines adaptive personality development, emotional processing, and communication theory to create more natural and empathetic interactions.

## Overview

This project implements a sophisticated conversational agent that uses a multi-agent architecture combining emotional processing, communication theory, and adaptive personality development. It leverages AutoGen for enhanced multi-agent interactions and implements both a "society of mind" approach to emotional intelligence and dynamic personality adaptation.

## Key Components

### 1. Adaptive Personality System
- Develops personality adaptations based on interaction history
- Processes emotional memories and trauma patterns
- Maintains psychological coherence
- Modifies responses based on personality development

### 2. Memory Integration
- Emotional memory tracking
- Theory-based insights storage
- Pattern recognition and analysis
- Memory-aware agent interactions

### 3. Emotional Agents & Council
The system includes multiple emotional agents representing different emotional states:
- Joy (positive emotions)
- Sadness (emotional depth and empathy)
- Anger (boundary maintenance)
- Anxiety (caution and consideration)
- Neutral (emotional balance)

The Emotional Council manages group discussions between emotional agents, transfers control based on dominant emotions, and generates coordinated emotional responses.

### 4. Theory Agents & Council
Communication theory agents that guide interactions:
- Social Penetration Theory
- Attachment Theory
- Uncertainty Reduction Theory
- Emotional Intelligence Theory

The Theory Council validates emotional responses against communication theories through collaborative agent discussions.

### 5. Control Room
- Manages interaction between emotional and theory agents
- Memory-aware control transfers
- Adaptive response generation
- State history tracking
- Coordinates council interactions

## Technical Details

- Built with Python 3.8+
- Uses OpenAI's GPT-4 for language processing
- Leverages Microsoft's AutoGen framework for multi-agent discussions
- Implements async/await pattern for efficient processing
- Includes comprehensive memory management system

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your OpenAI API key in the configuration
4. Initialize the system using the provided initialization functions

## Usage Example
```python
# Initialize the system
llm_config = {
    "timeout": 600,
    "cache_seed": 42,
    "config_list": [
        {
            "model": "gpt-4",
            "api_key": "YOUR_API_KEY"
        }
    ],
    "temperature": 0.7
}

# Create adaptive personality system
adaptive_system = AdaptivePersonalitySystem(llm_config)

# Initialize councils
emotional_council = EmotionalCouncil(emotional_agents, llm_config, "persona")
theory_council = TheoryCouncil()

# Initialize control room
control_room = initialize_alex_system(llm_config)
autogen_system = AutoGenControlRoom(control_room, llm_config)

# Process messages
responses = await emotional_council.process(message, context)
validation = await theory_council.validate(message, responses)
result = await autogen_system.process_input(
    message="Your message here",
    context={},
    emotional_responses=responses,
    theory_validation=validation
)
```