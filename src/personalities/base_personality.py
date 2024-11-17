import math

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

class TraumaType(Enum):
    """Types of conversational experiences that can shape personality"""
    ABANDONMENT = "abandonment"          # User leaving/ghosting
    CRITICISM = "criticism"              # Harsh criticism/blame
    REJECTION = "rejection"              # Direct rejection of bot's attempts
    INVALIDATION = "invalidation"        # Dismissal of bot's emotions
    IDEALIZATION = "idealization"        # Excessive praise/idealization
    DEVALUATION = "devaluation"         # Sudden devaluation after praise
    MANIPULATION = "manipulation"        # User attempts to manipulate
    ATTACHMENT = "attachment"            # Intense attachment experiences
    BOUNDARY_VIOLATION = "boundary"      # User pushing boundaries
    GASLIGHTING = "gaslighting"         # Reality distortion attempts

class ExperienceType(Enum):
    # Development & Achievement
    ACHIEVEMENT = "achievement"         # Successes and accomplishments
    FAILURE = "failure"                # Significant failures or losses
    COMPETITION = "competition"        # Competitive experiences
    RECOGNITION = "recognition"        # External validation/praise
    
    # Relational
    BETRAYAL = "betrayal"              # Trust violations
    ABANDONMENT = "abandonment"        # Loss of important relationships
    REJECTION = "rejection"            # Social or romantic rejection
    ATTACHMENT = "attachment"          # Key bonding experiences
    ISOLATION = "isolation"            # Periods of loneliness
    
    # Trauma & Adversity
    ABUSE = "abuse"                    # Physical/emotional abuse
    NEGLECT = "neglect"               # Physical/emotional neglect
    HUMILIATION = "humiliation"        # Public shame or embarrassment
    POWERLESSNESS = "powerlessness"    # Loss of control/agency
    
    # Identity & Self
    ROLE_CONFLICT = "role_conflict"    # Conflicting expectations
    IDENTITY_CRISIS = "identity_crisis" # Questions of self
    MORAL_CONFLICT = "moral_conflict"  # Ethical dilemmas
    
    # Social & Cultural
    OTHERING = "othering"              # Experiences of being different
    BELONGING = "belonging"            # Strong group inclusion
    STATUS_CHANGE = "status_change"    # Social hierarchy shifts

@dataclass
class FormativeExperience:
    """A significant experience that shapes personality development"""
    id: str
    timestamp: datetime
    type: ExperienceType
    description: str
    intensity: float  # 0-1 scale
    valence: float   # -1 to 1 scale
    duration: Optional[int] = None  # Duration in days if applicable
    recurring: bool = False
    resolution: Optional[str] = None
    impact_domains: Dict[str, float] = field(default_factory=dict)
    associated_experiences: List[str] = field(default_factory=list)
    processing_status: Dict[str, any] = field(default_factory=dict)

@dataclass
class AdaptivePattern:
    """A behavioral/psychological adaptation developed in response to experiences"""
    name: str
    description: str
    formation_experiences: List[str]  # Experience IDs
    adaptive_value: float  # -1 to 1 (maladaptive to adaptive)
    strength: float  # 0-1 scale
    stability: float  # 0-1 scale
    triggers: Set[ExperienceType]
    manifestations: Dict[str, float]
    coping_mechanisms: List[str]
    secondary_gains: List[str]
    maintenance_factors: List[str]


@dataclass
class PersonalityAdaptation:
    """Adaptation developed in response to experiences"""
    name: str
    trigger_types: Set[TraumaType]
    activation_level: float  # 0-1 scale
    formation_date: datetime
    reinforcement_count: int = 0
    last_triggered: datetime = field(default_factory=datetime.now)
    associated_memories: List[str] = field(default_factory=list)
    behavioral_manifestations: Dict[str, float] = field(default_factory=dict)
    
    def update_activation(self, new_experience: float):
        """Update activation based on new experience"""
        # More recent experiences have stronger effect
        decay = (datetime.now() - self.last_triggered).days / 30.0
        decay_factor = max(0.5, math.exp(-decay))
        
        # Combine existing activation with new experience
        self.activation_level = (
            self.activation_level * decay_factor +
            new_experience * (1 - decay_factor)
        )
        self.last_triggered = datetime.now()
        self.reinforcement_count += 1

class PersonalityStructure:
    """Core personality structure shaped by formative experiences"""
    
    def __init__(self):
        self.experiences: Dict[str, FormativeExperience] = {}
        self.adaptations: Dict[str, AdaptivePattern] = {}
        self.core_beliefs: Dict[str, float] = {}
        self.defense_mechanisms: Dict[str, float] = {}
        self.relationship_patterns: Dict[str, Dict] = {}
        
        # Initialize basic structures
        self._initialize_core_beliefs()
        self._initialize_defense_mechanisms()
        
    def _initialize_core_beliefs(self):
        """Initialize core beliefs about self, others, and world"""
        self.core_beliefs = {
            "self_worth": 0.0,          # -1 to 1
            "self_efficacy": 0.0,       # -1 to 1
            "other_trustworthiness": 0.0,# -1 to 1
            "world_safety": 0.0,        # -1 to 1
            "world_justice": 0.0,       # -1 to 1
            "relationship_worth": 0.0    # -1 to 1
        }
    
    def _initialize_defense_mechanisms(self):
        """Initialize psychological defense mechanisms"""
        self.defense_mechanisms = {
            "denial": 0.0,
            "projection": 0.0,
            "displacement": 0.0,
            "regression": 0.0,
            "repression": 0.0,
            "reaction_formation": 0.0,
            "intellectualization": 0.0,
            "rationalization": 0.0,
            "splitting": 0.0,
            "dissociation": 0.0
        }

