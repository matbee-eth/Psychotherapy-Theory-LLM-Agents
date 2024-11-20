/**
 * EMOTIONAL AGENT INTERFACES
 * Individual emotional agents represent distinct emotional aspects of the system.
 * Each agent maintains its own state, control vector, and processing logic.
 * 
 * Primary Responsibilities:
 * - Process messages from emotional perspective
 * - Maintain emotional state consistency
 * - Generate emotion-specific responses
 * - Contribute to overall emotional state
 */

interface EmotionalAgentInput {
    /** Raw message to process
     * Original user input for emotional analysis
     */
    message: string;
    
    /** Agent's current context */
    context: {
        /** Current state of this emotional agent
         * Includes influence level and confidence
         */
        current_state: AgentState;
        
        /** Personality traits influencing behavior
         * @normalized Each trait is normalized [0-1]
         * Affects emotional expression and response style
         */
        personality_traits: PersonalityTraits;
        
        /** Current relationship context
         * Used to adjust emotional expression appropriately
         */
        relationship_context: RelationshipContext;
    };
    
    /** Current control vector for this agent
     * @dimension 768 - Embedding space dimension
     * @normalized true - Unit length
     * Base vector for emotional influence
     */
    control_vector: number[];
    
    /** Optional memory context */
    memory_context?: {
        /** History of this agent's vector states
         * Used for emotional continuity
         */
        agent_history: VectorHistory[];
        
        /** Detected emotional patterns
         * Influences response generation
         */
        emotional_patterns: EmotionalPattern[];
    };
}

interface EmotionalAgentOutput {
    /** Agent's response */
    response: {
        /** Generated response text
         * Emotion-specific response content
         */
        content: string;
        
        /** Emotional state of response
         * Agent's emotional contribution
         */
        emotion: EmotionalState;
        
        /** Confidence in response [0-1]
         * Based on context match and emotional clarity
         */
        confidence: number;
        
        /** Emotional intensity of response [0-1]
         * How strongly the emotion is expressed
         */
        intensity: number;
    };
    
    /** Agent's modified control vector 
     * @dimension 768
     * @normalized true
     * Updated based on processing
     */
    control_vector: number[];
    
    /** State updates for this agent */
    state_update: {
        /** Current influence level [0-1]
         * How much this emotion affects system
         */
        influence: number;
        
        /** Current energy level [0-1]
         * Affects emotional expression intensity
         */
        energy: number;
        
        /** Modifications to control vector
         * @dimension 768
         * @normalized true
         * Changes based on processing
         */
        vector_modification: number[];
    };
}

/**
 * Supporting Types
 */
interface AgentState {
    /** Current influence level [0-1] */
    influence: number;
    /** Confidence in current state [0-1] */
    confidence: number;
    /** Energy level for expression [0-1] */
    energy: number;
    /** Last active timestamp */
    last_active: DateTime;
}

interface PersonalityTraits {
    /** Openness to experience [0-1] */
    openness: number;
    /** Conscientiousness level [0-1] */
    conscientiousness: number;
    /** Extraversion level [0-1] */
    extraversion: number;
    /** Agreeableness level [0-1] */
    agreeableness: number;
    /** Neuroticism level [0-1] */
    neuroticism: number;
}

interface RelationshipContext {
    /** Current relationship stage */
    stage: string;
    /** Trust level [0-1] */
    trust_level: number;
    /** Number of interactions */
    interaction_count: number;
    /** Last interaction time */
    last_interaction: DateTime;
    /** Important relationship events */
    significant_events: Event[];
}

interface EmotionalPattern {
    /** Type of pattern */
    pattern_type: string;
    /** Pattern frequency */
    frequency: number;
    /** Pattern confidence [0-1] */
    confidence: number;
    /** Supporting examples */
    examples: string[];
}

/**
 * Usage Example:
 * 
 * const joyAgent = new EmotionalAgent({
 *     emotion: "joy",
 *     personality: defaultPersonality,
 *     baseVector: joyVector
 * });
 * 
 * const input: EmotionalAgentInput = {
 *     message: "I got the job!",
 *     context: {
 *         current_state: { influence: 0.8, ... },
 *         personality_traits: { openness: 0.7, ... },
 *         relationship_context: { stage: "established", ... }
 *     },
 *     control_vector: currentVector
 * };
 * 
 * const result = await joyAgent.processInput(input);
 * // result.response will contain joy-influenced reply
 * // result.control_vector will reflect emotional state
 */