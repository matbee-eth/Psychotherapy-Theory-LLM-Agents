# Adaptive Personality AI System

## Overview

An advanced AI character system that combines emotional intelligence, psychological theory, and adaptive personality development to create natural, psychologically-grounded interactions. The system uses a sophisticated multi-agent architecture built on AutoGen, implementing both a "society of mind" approach to emotional intelligence and dynamic personality adaptation through experience-based learning.

## Key Features

### Emotional Intelligence
- Multi-agent emotional processing system
- Dynamic emotional state management
- Emotionally authentic responses
- Context-aware emotional adaptation

### Psychological Theory Integration
- Attachment Theory implementation
- Social Penetration Theory guidance
- Uncertainty Reduction modeling
- Emotional Intelligence framework

### Adaptive Personality
- Experience-based personality development
- Memory-driven adaptations
- Emergent behavioral patterns
- Natural psychological growth

### Memory System
- Sophisticated emotional memory processing
- Pattern recognition and clustering
- Experience-based learning
- Long-term relationship memory

## Architecture

### Core Components

1. **Control Room**
   - Orchestrates system components
   - Manages state and context
   - Coordinates agent interactions
   - Processes user input

2. **Emotional Council**
   - Joy (positive emotions)
   - Sadness (emotional depth)
   - Anger (boundaries)
   - Anxiety (caution)
   - Neutral (balance)

3. **Theory Council**
   - Attachment Theory Agent
   - Social Penetration Theory Agent
   - Uncertainty Reduction Agent
   - Emotional Intelligence Agent

4. **Memory System**
   - Emotional memory tracking
   - Experience clustering
   - Pattern recognition
   - Relationship history

## Technologies Used

- **Python 3.10+**
- **AutoGen** for multi-agent orchestration
- **memoripy** for memory management
- **numpy/scipy** for embedding operations
- **DBSCAN** for pattern clustering

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/adaptive-personality-ai.git

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and configurations
```

## Usage

### Basic Usage
```python
from system import IntegratedSystem
from config import SystemConfig

# Initialize system
config = SystemConfig(
    llm_config={
        "temperature": 0.7,
        "max_tokens": 800,
        "model": "gpt-4"
    }
)

system = IntegratedSystem(config)

# Process interaction
result = await system.process_interaction(
    "I've been feeling anxious about my new job, but I'm excited about the opportunity."
)
```

### Advanced Configuration
```python
# Configure emotional agents
emotional_config = {
    "joy": {"base_influence": 0.7},
    "sadness": {"base_influence": 0.5},
    "anger": {"base_influence": 0.3},
    "anxiety": {"base_influence": 0.4}
}

# Configure theory agents
theory_config = {
    "attachment": True,
    "social_penetration": True,
    "uncertainty_reduction": True,
    "emotional_intelligence": True
}

# Initialize with custom configuration
system = IntegratedSystem(
    config=SystemConfig(
        llm_config=llm_config,
        emotional_config=emotional_config,
        theory_config=theory_config
    )
)
```

## Core Features Implementation

### 1. Emotional Processing
```python
# Example emotional processing
emotional_responses = await system.emotional_council.process(
    message="I trust you enough to share this with you.",
    context={"relationship_stage": "developing"}
)
```

### 2. Theory Integration
```python
# Example theory validation
theory_validation = await system.theory_council.validate(
    message=message,
    emotional_responses=emotional_responses
)
```

### 3. Memory Management
```python
# Example memory storage
memory_id = await system.memory_manager.store_interaction(
    message=message,
    response=response,
    context=context
)
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_emotional.py
python -m pytest tests/test_theory.py
python -m pytest tests/test_memory.py
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Write/update tests
5. Submit a pull request

## System Requirements

- Python 3.10+
- 16GB RAM recommended
- GPU recommended for embedding operations
- Internet connection for LLM API access

## Configuration

The system can be configured through environment variables or a config file:

```env
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
MEMORY_STORAGE_PATH=./storage
LOG_LEVEL=INFO
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Theory Integration](docs/theories.md)
- [Memory System](docs/memory.md)

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with Microsoft's AutoGen framework
- Psychological theories based on established research
- Memory system inspired by cognitive architecture research

## Support

- GitHub Issues for bug reports and feature requests
- Discussions for general questions
- Wiki for additional documentation

## Future Development

1. **Enhanced Pattern Recognition**
   - Hierarchical clustering
   - Sub-pattern detection
   - Complex pattern relationships

2. **Advanced Analysis**
   - Deeper psychological understanding
   - Improved pattern recognition
   - Enhanced adaptation tracking

3. **System Optimization**
   - Improved embedding operations
   - Enhanced clustering efficiency
   - Refined response generation