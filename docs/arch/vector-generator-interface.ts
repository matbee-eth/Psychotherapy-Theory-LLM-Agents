/**
 * CONTROL VECTOR GENERATOR INTERFACES
 * Core system for generating and managing control vectors that modify model behavior.
 * Transforms emotional and psychological states into vectors that can directly
 * influence the model's response generation.
 * 
 * Primary Responsibilities:
 * - Generate control vectors from emotional states
 * - Combine multiple influence vectors
 * - Manage vector transitions
 * - Ensure vector stability and coherence
 */

interface VectorGeneratorInput {
    /** Responses from emotional agents with their vectors
     * Used to determine emotional influences
     */
    emotional_responses: Array<{
        /** The emotional response content and metadata */
        response: EmotionalResponse;
        /** The agent's current control vector */
        vector: number[];
        /** Agent's influence level [0-1] */
        influence: number;
    }>;
    
    /** Theory-based validations and constraints
     * Used to ensure psychological coherence
     */
    theory_validations: Array<{
        /** Theory providing the validation */
        theory_name: string;
        /** How well current state aligns with theory [0-1] */
        alignment_score: number;
        /** Theory-specific vector modifications */
        vector_adjustment: number[];
    }>;
    
    /** Current context for vector generation */
    context: {
        /** Stage of relationship development
         * Influences vector strength and complexity
         */
        relationship_stage: string;
        
        /** Number of total interactions
         * Used for experience-based adjustments
         */
        interaction_count: number;
        
        /** Time since last interaction (seconds)
         * For temporal decay calculations
         */
        time_elapsed: number;
        
        /** Current emotional intensity [0-1]
         * Affects vector magnitude
         */
        emotional_intensity: number;
    };
    
    /** Optional previous control vector
     * For smooth transitions
     * @dimension 768
     * @normalized true
     */
    current_vector?: number[];
}

interface VectorGeneratorOutput {
    /** Generated control vector
     * @dimension 768 - Matches model embedding space
     * @normalized true - Unit length for stability
     * Final vector to modify model behavior
     */
    control_vector: number[];
    
    /** Component vectors for analysis and debugging */
    vector_components: {
        /** Emotional influence vector
         * From emotional agent responses
         */
        emotional: number[];
        
        /** Psychological influence vector
         * From theory validations
         */
        psychological: number[];
        
        /** Temporal dynamics vector
         * Time-based modifications
         */
        temporal: number[];
    };
    
    /** Component weights used in combination */
    weights: {
        /** Weight of emotional component [0-1]
         * Higher for emotionally intense situations
         */
        emotional: number;
        
        /** Weight of psychological component [0-1]
         * Higher for complex interactions
         */
        psychological: number;
        
        /** Weight of temporal component [0-1]
         * Higher for maintaining continuity
         */
        temporal: number;
    };
    
    /** Metadata about vector generation */
    metadata: {
        /** Confidence in vector quality [0-1] */
        confidence: number;
        
        /** Vector stability metric [0-1] */
        stability: number;
        
        /** Expected influence strength [0-1] */
        expected_influence: number;
        
        /** Vector generation approach used */
        generation_method: string;
    };
}

/**
 * Supporting Types
 */
interface VectorModification {
    /** Type of modification applied */
    type: "add" | "subtract" | "scale" | "rotate";
    
    /** Magnitude of modification */
    magnitude: number;
    
    /** Component affected 
     * Which aspect of vector is modified
     */
    component: "emotional" | "psychological" | "temporal";
    
    /** Reason for modification */
    reason: string;
}

interface VectorConstraints {
    /** Minimum vector magnitude */
    min_magnitude: number;
    
    /** Maximum vector magnitude */
    max_magnitude: number;
    
    /** Allowed rate of change */
    max_delta: number;
    
    /** Required similarity to previous [0-1] */
    min_similarity: number;
}

/**
 * Usage Example:
 * 
 * const vectorGen = new ControlVectorGenerator(config);
 * 
 * const input: VectorGeneratorInput = {
 *     emotional_responses: [
 *         {
 *             response: joyResponse,
 *             vector: joyVector,
 *             influence: 0.8
 *         },
 *         // ... other emotional responses
 *     ],
 *     theory_validations: [
 *         {
 *             theory_name: "attachment",
 *             alignment_score: 0.9,
 *             vector_adjustment: attachmentVector
 *         }
 *     ],
 *     context: {
 *         relationship_stage: "established",
 *         interaction_count: 100,
 *         time_elapsed: 3600,
 *         emotional_intensity: 0.7
 *     },
 *     current_vector: previousVector
 * };
 * 
 * const result = await vectorGen.generateVector(input);
 * // result.control_vector can be used to modify model behavior
 * // result.vector_components shows how vector was constructed
 * // result.weights shows relative importance of components
 * 
 * // Apply vector constraints
 * const constraints: VectorConstraints = {
 *     min_magnitude: 0.1,
 *     max_magnitude: 1.0,
 *     max_delta: 0.2,
 *     min_similarity: 0.7
 * };
 * 
 * const constrained_vector = vectorGen.applyConstraints(
 *     result.control_vector, 
 *     constraints
 * );
 */