/**
 * THEORY VALIDATOR INTERFACES
 * Ensures responses and state transitions align with psychological theories.
 * Acts as a psychological coherence check for the system's behavior.
 * 
 * Primary Responsibilities:
 * - Validate responses against psychological theories
 * - Guide emotional development
 * - Ensure relationship progression
 * - Maintain psychological consistency
 * - Provide theory-based modifications
 */

interface TheoryValidatorInput {
    /** Message and response for validation */
    interaction: {
        /** Original message */
        message: string;
        
        /** Proposed response */
        proposed_response: string;
        
        /** Current emotional state */
        emotional_state: EmotionalState;
        
        /** Response confidence [0-1] */
        confidence: number;
    };
    
    /** Relationship context */
    context: {
        /** Current relationship stage */
        relationship_stage: string;
        
        /** Recent interactions */
        interaction_history: Interaction[];
        
        /** Trust level [0-1] */
        trust_level: number;
        
        /** Emotional depth [0-1] */
        emotional_depth: number;
        
        /** Self-disclosure level [0-1] */
        self_disclosure_level: number;
    };
    
    /** Current control vector
     * @dimension 768
     * @normalized true
     */
    control_vector: number[];
    
    /** Active theories to check
     * If empty, checks all theories
     */
    theories_to_check?: string[];
    
    /** Validation requirements */
    requirements?: {
        /** Minimum alignment score [0-1] */
        min_alignment_score?: number;
        
        /** Required theories to pass */
        required_theories?: string[];
        
        /** Maximum suggested modifications */
        max_modifications?: number;
    };
}

interface TheoryValidatorOutput {
    /** Individual theory validations */
    validations: Array<{
        /** Theory name */
        theory_name: string;
        
        /** Alignment score [0-1] */
        alignment_score: number;
        
        /** Specific concerns */
        concerns: Array<{
            /** Concern type */
            type: string;
            /** Description */
            description: string;
            /** Severity [0-1] */
            severity: number;
            /** Suggested fix */
            suggestion: string;
        }>;
        
        /** Improvement suggestions */
        suggestions: Array<{
            /** What to modify */
            target: string;
            /** How to modify */
            modification: string;
            /** Expected improvement */
            expected_impact: number;
            /** Implementation priority */
            priority: number;
        }>;
    }>;
    
    /** Vector modifications */
    modifications: {
        /** Control vector adjustments */
        vector_adjustments: Array<{
            /** Adjustment type */
            type: "add" | "subtract" | "scale";
            /** Vector to apply */
            vector: number[];
            /** Adjustment magnitude */
            magnitude: number;
            /** Theory requiring change */
            theory: string;
        }>;
        
        /** Response content adjustments */
        response_adjustments: Array<{
            /** Original content */
            original: string;
            /** Suggested modification */
            suggestion: string;
            /** Reason for change */
            reason: string;
            /** Theory alignment improvement */
            improvement: number;
        }>;
    };
    
    /** Theory-based guidance */
    guidance: {
        /** Overall interaction approach */
        recommended_approach: string;
        
        /** Theory-specific recommendations */
        theory_specific_advice: Record<string, {
            /** Key points to consider */
            considerations: string[];
            /** Specific techniques */
            techniques: string[];
            /** Development goals */
            goals: string[];
        }>;
        
        /** Development trajectory */
        development_path: {
            /** Current stage */
            current_stage: string;
            /** Next stage */
            next_stage: string;
            /** Requirements for progression */
            progression_requirements: string[];
            /** Estimated interactions to next stage */
            estimated_progression: number;
        };
    };
    
    /** Validation metrics */
    metrics: {
        /** Overall validation score [0-1] */
        overall_score: number;
        
        /** Theory compliance scores */
        theory_scores: Record<string, number>;
        
        /** Validation confidence [0-1] */
        confidence: number;
        
        /** Areas needing improvement */
        improvement_areas: Array<{
            /** Area name */
            area: string;
            /** Current score [0-1] */
            current_score: number;
            /** Target score [0-1] */
            target_score: number;
            /** Priority */
            priority: number;
        }>;
    };
}

/**
 * Theory Registry Interface
 * Manages available psychological theories
 */
interface TheoryRegistry {
    /** Register new theory */
    registerTheory(
        theory: Theory
    ): Promise<void>;
    
    /** Get theory by name */
    getTheory(
        name: string
    ): Promise<Theory | null>;
    
    /** Update theory configuration */
    updateTheory(
        name: string,
        updates: Partial<Theory>
    ): Promise<void>;
    
    /** Get all active theories */
    getActiveTheories(): Promise<Theory[]>;
}

/**
 * Supporting Types
 */
interface Theory {
    /** Theory name */
    name: string;
    
    /** Core principles */
    principles: string[];
    
    /** Implementation guidelines */
    guidelines: string[];
    
    /** Validation rules */
    validation_rules: ValidationRule[];
    
    /** Development stages */
    development_stages: DevelopmentStage[];
    
    /** Theory weight [0-1] */
    weight: number;
}

interface ValidationRule {
    /** Rule identifier */
    id: string;
    
    /** What to check */
    check: string;
    
    /** Validation function */
    validate: (input: any) => ValidationResult;
    
    /** Rule priority */
    priority: number;
}

interface DevelopmentStage {
    /** Stage name */
    name: string;
    
    /** Entry requirements */
    requirements: Requirement[];
    
    /** Stage characteristics */
    characteristics: string[];
    
    /** Progression metrics */
    progression_metrics: Record<string, number>;
}

/**
 * Usage Example:
 * 
 * const validator = new TheoryValidator(config);
 * 
 * const input: TheoryValidatorInput = {
 *     interaction: {
 *         message: "I trust you with this...",
 *         proposed_response: "Thank you for sharing...",
 *         emotional_state: { primary: "empathy", ... },
 *         confidence: 0.85
 *     },
 *     context: {
 *         relationship_stage: "developing",
 *         trust_level: 0.7,
 *         emotional_depth: 0.6,
 *         self_disclosure_level: 0.5
 *     },
 *     control_vector: currentVector,
 *     theories_to_check: ["attachment", "social_penetration"]
 * };
 * 
 * const validation = await validator.validate(input);
 * 
 * if (validation.metrics.overall_score >= 0.8) {
 *     // Use response as is
 * } else {
 *     // Apply suggested modifications
 *     const modifiedResponse = await validator.applyModifications(
 *         input.interaction.proposed_response,
 *         validation.modifications
 *     );
 * }
 */