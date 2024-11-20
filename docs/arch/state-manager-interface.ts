/**
 * STATE MANAGER INTERFACES
 * Manages overall system state including emotional, psychological, and relationship aspects.
 * Ensures coherent state transitions and maintains system stability.
 * 
 * Primary Responsibilities:
 * - Maintain system state
 * - Handle state transitions
 * - Ensure state coherence
 * - Track state history
 * - Predict state evolution
 */

interface StateManagerInput {
    /** Current complete system state */
    current_state: SystemState;
    
    /** Control vector for state modification
     * @dimension 768
     * @normalized true
     */
    control_vector: number[];
    
    /** Requested state updates */
    updates: {
        /** Emotional state changes */
        emotional: {
            /** New emotional state */
            state: EmotionalState;
            /** Confidence in update [0-1] */
            confidence: number;
            /** Transition speed [0-1] */
            speed: number;
        };
        
        /** Psychological state changes */
        psychological: {
            /** Updated traits */
            traits: PersonalityTraits;
            /** Theory compliance scores */
            theory_alignment: Record<string, number>;
            /** Change magnitude [0-1] */
            magnitude: number;
        };
        
        /** Relationship state changes */
        relationship: {
            /** New stage if changed */
            stage?: string;
            /** Trust level change */
            trust_delta: number;
            /** Interaction quality [0-1] */
            quality: number;
        };
    };
    
    /** Update context */
    context: {
        /** When update occurs */
        timestamp: DateTime;
        
        /** Type of interaction causing update */
        interaction_type: string;
        
        /** Update significance [0-1] */
        significance: number;
        
        /** Required stability [0-1]
         * Higher values mean slower changes
         */
        stability_requirement: number;
    };
}

interface StateManagerOutput {
    /** New system state after updates */
    new_state: SystemState;
    
    /** State transition details */
    transitions: {
        /** Emotional state changes */
        emotional_changes: Array<{
            /** What changed */
            type: string;
            /** From value */
            from: any;
            /** To value */
            to: any;
            /** Change magnitude */
            magnitude: number;
        }>;
        
        /** Psychological state changes */
        psychological_changes: Array<{
            /** Trait modified */
            trait: string;
            /** Change amount */
            delta: number;
            /** Reason for change */
            reason: string;
        }>;
        
        /** Relationship state changes */
        relationship_changes: Array<{
            /** Aspect changed */
            aspect: string;
            /** Change details */
            details: string;
            /** Impact [0-1] */
            impact: number;
        }>;
    };
    
    /** State quality metrics */
    metrics: {
        /** State stability [0-1]
         * How well state maintains consistency
         */
        stability: number;
        
        /** State coherence [0-1]
         * How well components align
         */
        coherence: number;
        
        /** Transition quality [0-1]
         * How smooth the change was
         */
        transition_quality: number;
    };
    
    /** Future state guidance */
    recommendations: {
        /** Suggested state adjustments */
        adjustments: Array<{
            /** What to adjust */
            target: string;
            /** How to adjust */
            action: string;
            /** Why needed */
            reason: string;
            /** Priority [0-1] */
            priority: number;
        }>;
        
        /** Predicted future states */
        future_predictions: Array<{
            /** Predicted state */
            state: SystemState;
            /** Time offset */
            time_offset: number;
            /** Confidence [0-1] */
            confidence: number;
        }>;
    };
}

/**
 * Supporting Types
 */
interface SystemState {
    /** Emotional component */
    emotional: {
        /** Primary emotion */
        primary: EmotionalState;
        /** Secondary emotions */
        secondary: EmotionalState[];
        /** Overall intensity [0-1] */
        intensity: number;
    };
    
    /** Psychological component */
    psychological: {
        /** Personality traits */
        traits: PersonalityTraits;
        /** Active adaptations */
        adaptations: string[];
        /** Theory alignment */
        theory_alignment: Record<string, number>;
    };
    
    /** Relationship component */
    relationship: {
        /** Current stage */
        stage: string;
        /** Trust level [0-1] */
        trust_level: number;
        /** Connection depth [0-1] */
        connection_depth: number;
    };
    
    /** Meta information */
    meta: {
        /** Last update time */
        last_updated: DateTime;
        /** State version */
        version: number;
        /** Stability metric [0-1] */
        stability: number;
    };
}

/**
 * Usage Example:
 * 
 * const stateManager = new StateManager(config);
 * 
 * const input: StateManagerInput = {
 *     current_state: currentSystemState,
 *     control_vector: latestVector,
 *     updates: {
 *         emotional: {
 *             state: newEmotionalState,
 *             confidence: 0.8,
 *             speed: 0.5
 *         },
 *         psychological: {
 *             traits: updatedTraits,
 *             theory_alignment: { "attachment": 0.9 },
 *             magnitude: 0.3
 *         },
 *         relationship: {
 *             trust_delta: 0.1,
 *             quality: 0.7
 *         }
 *     },
 *     context: {
 *         timestamp: new Date(),
 *         interaction_type: "emotional_support",
 *         significance: 0.8,
 *         stability_requirement: 0.7
 *     }
 * };
 * 
 * const result = await stateManager.updateState(input);
 * // result.new_state contains updated system state
 * // result.transitions shows what changed
 * // result.metrics indicates state quality
 * // result.recommendations guides future updates
 */