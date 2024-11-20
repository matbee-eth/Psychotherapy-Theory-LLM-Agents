/**
 * MONITORING AND FEEDBACK SYSTEM INTERFACES
 * Tracks system performance, collects metrics, and provides feedback
 * for system improvement and debugging.
 * 
 * Primary Responsibilities:
 * - Track system performance
 * - Collect interaction metrics
 * - Monitor emotional coherence
 * - Detect anomalies
 * - Provide debugging info
 */

interface MonitoringSystemInput {
    /** Interaction data */
    interaction: {
        /** Interaction ID */
        id: string;
        
        /** Original message */
        message: string;
        
        /** Generated response */
        response: string;
        
        /** Processing time (ms) */
        processing_time: number;
        
        /** Interaction timestamp */
        timestamp: DateTime;
    };
    
    /** System state */
    system_state: {
        /** Emotional state */
        emotional_state: EmotionalState;
        
        /** Control vector */
        control_vector: number[];
        
        /** Memory usage */
        memory_usage: MemoryMetrics;
        
        /** Theory compliance */
        theory_compliance: Record<string, number>;
    };
    
    /** Performance metrics */
    metrics: {
        /** Response generation metrics */
        generation: {
            /** Token count */
            tokens: number;
            
            /** Generation time (ms) */
            generation_time: number;
            
            /** Cache hits/misses */
            cache_metrics: CacheMetrics;
            
            /** LLM calls */
            llm_metrics: LLMMetrics;
        };
        
        /** Quality metrics */
        quality: {
            /** Response coherence [0-1] */
            coherence: number;
            
            /** Emotional alignment [0-1] */
            emotional_alignment: number;
            
            /** Theory compliance [0-1] */
            theory_compliance: number;
            
            /** Memory relevance [0-1] */
            memory_relevance: number;
        };
        
        /** Resource usage */
        resources: {
            /** CPU usage % */
            cpu_usage: number;
            
            /** Memory usage MB */
            memory_usage: number;
            
            /** Storage usage MB */
            storage_usage: number;
        };
    };
    
    /** Debug information */
    debug?: {
        /** Error traces */
        errors: ErrorTrace[];
        
        /** Warning messages */
        warnings: Warning[];
        
        /** System logs */
        logs: LogEntry[];
    };
}

interface MonitoringSystemOutput {
    /** System health assessment */
    health_assessment: {
        /** Overall status */
        status: "healthy" | "degraded" | "critical";
        
        /** Health score [0-1] */
        health_score: number;
        
        /** Active issues */
        issues: Issue[];
        
        /** Improvement suggestions */
        suggestions: Suggestion[];
    };
    
    /** Performance analysis */
    performance: {
        /** Current performance metrics */
        current_metrics: MetricSet;
        
        /** Historical trends */
        trends: Trend[];
        
        /** Anomalies detected */
        anomalies: Anomaly[];
        
        /** Performance insights */
        insights: Insight[];
    };
    
    /** Quality assessment */
    quality: {
        /** Quality scores */
        scores: Record<string, number>;
        
        /** Quality trends */
        trends: QualityTrend[];
        
        /** Areas for improvement */
        improvement_areas: ImprovementArea[];
    };
    
    /** System recommendations */
    recommendations: {
        /** Configuration updates */
        config_updates: ConfigUpdate[];
        
        /** Resource adjustments */
        resource_adjustments: ResourceAdjustment[];
        
        /** Maintenance tasks */
        maintenance_tasks: MaintenanceTask[];
    };
    
    /** Alert notifications */
    alerts?: {
        /** Critical alerts */
        critical: Alert[];
        
        /** Warnings */
        warnings: Alert[];
        
        /** Information notices */
        info: Alert[];
    };
}

/**
 * Monitoring Registry Interface
 * Manages monitoring configurations and callbacks
 */
interface MonitoringRegistry {
    /** Register metric */
    registerMetric(
        metric: Metric
    ): Promise<void>;
    
    /** Register alert handler */
    registerAlertHandler(
        handler: AlertHandler
    ): Promise<void>;
    
    /** Update monitoring config */
    updateConfig(
        updates: Partial<MonitoringConfig>
    ): Promise<void>;
}

/**
 * Supporting Types
 */
interface Metric {
    /** Metric name */
    name: string;
    
    /** Collection function */
    collect: () => Promise<number>;
    
    /** Thresholds */
    thresholds: {
        warning: number;
        critical: number;
    };
    
    /** Collection interval (ms) */
    interval: number;
}

interface Alert {
    /** Alert level */
    level: "info" | "warning" | "critical";
    
    /** Alert message */
    message: string;
    
    /** Triggering metric */
    metric: string;
    
    /** Current value */
    value: number;
    
    /** Threshold crossed */
    threshold: number;
    
    /** Timestamp */
    timestamp: DateTime;
}

/**
 * Usage Example:
 * 
 * const monitor = new MonitoringSystem(config);
 * 
 * // Register metrics
 * await monitor.registerMetric({
 *     name: "response_time",
 *     collect: async () => {
 *         // Collect response time metric
 *         return responseTime;
 *     },
 *     thresholds: {
 *         warning: 1000,  // 1 second
 *         critical: 2000  // 2 seconds
 *     },
 *     interval: 60000  // Check every minute
 * });
 * 
 * // Monitor interaction
 * const input: MonitoringSystemInput = {
 *     interaction: {
 *         id: "interaction-123",
 *         message: "Hello",
 *         response: "Hi there!",
 *         processing_time: 500,
 *         timestamp: new Date()
 *     },
 *     system_state: {
 *         emotional_state: currentState,
 *         control_vector: currentVector,
 *         memory_usage: memoryMetrics,
 *         theory_compliance: complianceScores
 *     },
 *     metrics: {
 *         generation: { ... },
 *         quality: { ... },
 *         resources: { ... }
 *     }
 * };
 * 
 * const assessment = await monitor.processInteraction(input);
 * 
 * // Handle any alerts
 * if (assessment.alerts?.critical.length > 0) {
 *     await monitor.handleCriticalAlerts(assessment.alerts.critical);
 * }
 * 
 * // Apply recommendations
 * if (assessment.recommendations.config_updates.length > 0) {
 *     await monitor.applyConfigUpdates(
 *         assessment.recommendations.config_updates
 *     );
 * }
 */