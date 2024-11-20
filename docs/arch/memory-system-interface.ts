/**
 * MEMORY SYSTEM INTERFACES
 * Manages storage, retrieval, and pattern recognition for emotional and interaction memories.
 * Provides contextual awareness and learning capabilities to the system.
 * 
 * Primary Responsibilities:
 * - Store interaction memories
 * - Track emotional patterns
 * - Maintain vector history
 * - Detect behavioral patterns
 * - Provide contextual retrieval
 */

interface MemorySystemInput {
    /** New memory content */
    content: {
        /** Original user message */
        message: string;
        
        /** System's response */
        response: string;
        
        /** Emotional state during interaction */
        emotional_state: EmotionalState;
        
        /** Optional metadata */
        metadata?: {
            /** Any attached files/media */
            attachments?: string[];
            /** External references */
            references?: string[];
            /** User-specific context */
            user_context?: Record<string, any>;
        };
    };
    
    /** Associated control vector
     * @dimension 768
     * @normalized true
     * Links memory to emotional state
     */
    control_vector: number[];
    
    /** Memory context */
    context: {
        /** Creation timestamp */
        timestamp: DateTime;
        
        /** Relationship stage when created */
        relationship_stage: string;
        
        /** Type of interaction */
        interaction_type: string;
        
        /** Memory significance [0-1]
         * Influences storage priority
         */
        significance: number;
        
        /** Required retention time
         * How long to maintain in active memory
         */
        retention_period?: number;
    };
    
    /** Optional vector data for pattern matching */
    vector_data?: {
        /** Previous control vectors 
         * For pattern recognition
         */
        previous_vectors: number[][];
        
        /** Known emotional patterns
         * For pattern reinforcement
         */
        emotional_patterns: Pattern[];
        
        /** Vector similarity threshold
         * For pattern matching
         */
        similarity_threshold?: number;
    };
}

interface MemorySystemOutput {
    /** Retrieved relevant memories */
    relevant_memories: Array<{
        /** Memory content */
        memory: Memory;
        /** Relevance score [0-1] */
        relevance: number;
        /** Retrieved for reason */
        retrieval_reason: string;
    }>;
    
    /** Vector state history */
    vector_history: Array<{
        /** Historical vector */
        vector: number[];
        /** When recorded */
        timestamp: DateTime;
        /** Associated context */
        context: string;
        /** Influence at time */
        influence: number;
    }>;
    
    /** Recognized patterns */
    patterns: {
        /** Emotional interaction patterns */
        emotional: Array<{
            /** Pattern type */
            pattern_type: string;
            /** Pattern frequency */
            frequency: number;
            /** Example memories */
            examples: string[];
            /** Pattern confidence [0-1] */
            confidence: number;
        }>;
        
        /** Behavioral patterns */
        behavioral: Array<{
            /** Behavior type */
            behavior: string;
            /** Occurrence count */
            occurrences: number;
            /** Trigger conditions */
            triggers: string[];
            /** Pattern strength [0-1] */
            strength: number;
        }>;
        
        /** Relationship development patterns */
        relationship: Array<{
            /** Pattern description */
            description: string;
            /** Development stage */
            stage: string;
            /** Key interactions */
            key_moments: string[];
            /** Pattern significance [0-1] */
            significance: number;
        }>;
    };
    
    /** Memory context summary */
    context_summary: {
        /** Most significant patterns */
        dominant_patterns: Pattern[];
        
        /** Relationship status overview */
        relationship_status: {
            /** Current stage */
            stage: string;
            /** Stage duration */
            duration: number;
            /** Stage stability [0-1] */
            stability: number;
            /** Development velocity [-1 to 1] */
            velocity: number;
        };
        
        /** Interaction metrics */
        interaction_metrics: {
            /** Total interaction count */
            total_interactions: number;
            /** Average interaction quality [0-1] */
            avg_quality: number;
            /** Response consistency [0-1] */
            consistency: number;
            /** Engagement level [0-1] */
            engagement: number;
        };
    };
}

/**
 * Memory Storage Interface
 * Handles actual storage and retrieval operations
 */
interface MemoryStore {
    /** Store new memory */
    store(
        memory: Memory,
        options?: StorageOptions
    ): Promise<string>;  // Returns memory ID
    
    /** Retrieve memories by query */
    retrieve(
        query: MemoryQuery,
        options?: RetrievalOptions
    ): Promise<Memory[]>;
    
    /** Update existing memory */
    update(
        id: string,
        updates: Partial<Memory>
    ): Promise<boolean>;
    
    /** Remove memory */
    delete(id: string): Promise<boolean>;
    
    /** Get memory by ID */
    get(id: string): Promise<Memory | null>;
}

/**
 * Pattern Recognition Interface
 * Handles pattern detection and analysis
 */
interface PatternRecognizer {
    /** Detect patterns in memories */
    detectPatterns(
        memories: Memory[],
        options?: PatternOptions
    ): Promise<Pattern[]>;
    
    /** Update existing patterns */
    updatePatterns(
        new_memory: Memory,
        existing_patterns: Pattern[]
    ): Promise<Pattern[]>;
    
    /** Validate pattern */
    validatePattern(
        pattern: Pattern,
        memories: Memory[]
    ): Promise<ValidationResult>;
}

/**
 * Supporting Types
 */
interface Memory {
    id: string;
    content: string;
    emotional_context: EmotionalState;
    vector_representation: number[];
    timestamp: DateTime;
    significance: number;
    metadata: Record<string, any>;
}

interface Pattern {
    id: string;
    type: string;
    frequency: number;
    confidence: number;
    supporting_evidence: string[];
    last_updated: DateTime;
}

interface StorageOptions {
    priority: "high" | "medium" | "low";
    retention: "short" | "medium" | "long";
    compression?: boolean;
    encryption?: boolean;
}

interface RetrievalOptions {
    limit?: number;
    min_relevance?: number;
    sort_by?: "time" | "relevance" | "significance";
    include_metadata?: boolean;
}

/**
 * Usage Example:
 * 
 * const memorySystem = new MemorySystem(config);
 * 
 * // Store new memory
 * const input: MemorySystemInput = {
 *     content: {
 *         message: "I'm feeling better now",
 *         response: "I'm glad to hear that...",
 *         emotional_state: { primary: "joy", ... }
 *     },
 *     control_vector: currentVector,
 *     context: {
 *         timestamp: new Date(),
 *         relationship_stage: "developing",
 *         interaction_type: "emotional_support",
 *         significance: 0.8
 *     }
 * };
 * 
 * await memorySystem.store(input);
 * 
 * // Retrieve relevant memories
 * const query = {
 *     emotion: "joy",
 *     timeframe: "recent",
 *     min_significance: 0.5
 * };
 * 
 * const memories = await memorySystem.retrieve(query);
 * 
 * // Analyze patterns
 * const patterns = await memorySystem.analyzePatterns(memories);
 */