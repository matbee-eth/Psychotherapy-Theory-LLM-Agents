/**
 * EMOTIONAL COUNCIL INTERFACES
 * The Emotional Council acts as the central coordinator for emotional processing.
 * It manages the interactions between emotional agents and maintains overall emotional coherence.
 * 
 * Primary Responsibilities:
 * - Coordinates emotional agent interactions
 * - Maintains overall emotional state
 * - Manages control vector combinations
 * - Ensures personality consistency
 */

interface EmotionalCouncilInput {
    /** Raw message from user interaction */
    message: string;
    
    /** Contextual information for processing */
    context: {
        /** Previous messages in the conversation, including metadata 
         * Used for conversation flow and context understanding
         */
        conversation_history: Message[];
        
        /** Current stage of relationship development 
         * @values ["initial", "developing", "established", "close", "intimate"]
         * Influences depth and style of emotional responses
         */
        relationship_stage: string;
        
        /** Current emotional state of the system
         * Used as baseline for emotional transitions
         */
        current_state: EmotionalState;
        
        /** Timestamp of current interaction for temporal processing
         * Used for decay calculations and temporal dynamics
         */
        timestamp: DateTime;
    };
    
    /** Optional memory context for enhanced processing */
    memory_context?: {
        /** Relevant memories for current interaction
         * Retrieved based on emotional and contextual similarity
         */
        relevant_memories: Memory[];
        
        /** History of emotional vector states
         * Used for tracking emotional development and patterns
         */
        vector_history: VectorHistory[];
    };
}

interface EmotionalCouncilOutput {
    /** Collection of responses from all emotional agents
     * Each response includes emotion-specific processing
     */
    responses: EmotionalResponse[];
    
    /** Currently dominant emotion based on context and responses
     * Determined by combining agent influences and context
     */
    dominant_emotion: EmotionalState;
    
    /** Combined control vector from all emotional agents
     * @dimension 768 - Matches embedding space
     * @normalized true - Vector is normalized to unit length
     * Used to influence response generation and state transitions
     */
    combined_vector: number[];
    
    /** Updates to system state after processing */
    state_update: {
        /** New emotional state after processing
         * Includes primary and secondary emotions
         */
        new_state: EmotionalState;
        
        /** Confidence in current emotional state [0-1]
         * Based on agent agreement and context consistency
         */
        confidence: number;
        
        /** Influence levels of each emotion 
         * @key Emotion name
         * @value Influence level [0-1]
         * Represents current emotional mixture
         */
        influence_levels: Record<string, number>;
    };
}

/**
 * Supporting Types
 */
interface Message {
    content: string;
    timestamp: DateTime;
    metadata: {
        emotional_state: EmotionalState;
        relationship_stage: string;
        interaction_type: string;
    };
}

interface EmotionalState {
    /** Primary emotion currently active */
    primary: string;
    /** Secondary emotions influencing state */
    secondary: string[];
    /** Intensity of emotional state [0-1] */
    intensity: number;
    /** Emotional valence (positive/negative) [-1 to 1] */
    valence: number;
}

interface Memory {
    id: string;
    content: string;
    emotional_context: EmotionalState;
    timestamp: DateTime;
    significance: number;
}

interface VectorHistory {
    vector: number[];
    timestamp: DateTime;
    context: string;
    influence: number;
}

/**
 * Usage Example:
 * 
 * const council = new EmotionalCouncil(config);
 * 
 * const input: EmotionalCouncilInput = {
 *     message: "I'm feeling anxious about tomorrow",
 *     context: {
 *         conversation_history: [...],
 *         relationship_stage: "established",
 *         current_state: { primary: "neutral", ... },
 *         timestamp: new Date()
 *     }
 * };
 * 
 * const result = await council.processInput(input);
 * // result.dominant_emotion will reflect appropriate emotional response
 * // result.combined_vector will provide control vector for response generation
 */