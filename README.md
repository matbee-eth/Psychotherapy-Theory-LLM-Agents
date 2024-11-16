# Persona Bot

An emotionally intelligent conversational agent system that combines emotional processing with communication theory to create more natural and empathetic interactions.

## Overview

This project implements a sophisticated conversational agent named Alex using a combination of emotional processing agents and communication theory agents. It leverages AutoGen for enhanced multi-agent interactions and implements a "society of mind" approach to emotional intelligence.

## Key Components

### 1. Emotional Agents
The system includes multiple emotional agents representing different emotional states:
- Joy (positive emotions)
- Sadness (emotional depth and empathy)
- Anger (boundary maintenance)
- Anxiety (caution and consideration)
- Neutral (emotional balance)

### 2. Theory Agents
Communication theory agents that guide interactions:
- Social Penetration Theory
- Attachment Theory
- Uncertainty Reduction Theory
- Emotional Intelligence Theory

### 3. Control Room
Manages the interaction between emotional and theory agents to produce coherent responses.

### 4. AutoGen Enhancement
Implements AutoGen's SocietyOfMindAgent for improved multi-agent coordination and dialogue.

## Technical Details

- Built with Python
- Uses OpenAI's GPT-4 for language processing
- Leverages Microsoft's AutoGen framework
- Implements async/await pattern for efficient processing

## Setup

1. Clone the repository
2. Install dependencies
3. Configure your OpenAI API key in the configuration
4. Initialize the system using the provided initialization functions

## Usage

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

control_room = initialize_alex_system(llm_config)
autogen_system = AutoGenControlRoom(control_room, llm_config)

# Process messages
result = await autogen_system.process_input(
    message="Your message here",
    context={}
)
```
## Features

- Emotionally aware responses
- Theory-guided interactions  
- Multi-agent coordination
- Personality consistency
- Memory context awareness
- Fallback mechanisms for error handling