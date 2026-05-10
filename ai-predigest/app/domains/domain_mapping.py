"""
Domain Mapping Configuration for MyZodiaq UI Integration

Maps UI display names to backend folder names for proper routing.

Usage:
    from app.domains.domain_mapping import (
        resolve_domain_subdomain,
        validate_domain,
        validate_subdomain,
        get_all_domains_for_api
    )
    
    # In your API endpoint:
    backend_domain, backend_subdomain = resolve_domain_subdomain(
        request.domain, 
        request.subtopic
    )
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


# ========================
# Data Classes
# ========================

@dataclass
class SubdomainConfig:
    """Configuration for a single subdomain"""
    ui_name: str                    # Display name for UI
    backend_name: str               # Folder name in backend (snake_case)
    description: str = ""
    aliases: List[str] = field(default_factory=list)
    requires_person2: bool = False
    is_implemented: bool = True


@dataclass
class DomainConfig:
    """Configuration for a domain and its subdomains"""
    ui_name: str                    # Display name for UI
    backend_name: str               # Folder name in backend (snake_case)
    description: str = ""
    subdomains: List[SubdomainConfig] = field(default_factory=list)
    order: int = 0


# ========================
# Domain Configuration
# ========================

DOMAIN_CONFIG: List[DomainConfig] = [
    # 1. General Guidance
    DomainConfig(
        ui_name="General Guidance",
        backend_name="general_guidance",
        description="General kundali analysis and spiritual guidance",
        order=1,
        subdomains=[
            SubdomainConfig(
                ui_name="General Kundali Analysis",
                backend_name="general_kundali_analysis",
                description="Comprehensive kundali reading covering all aspects of life",
                aliases=["kundali", "horoscope", "birth chart", "janam kundali"]
            ),
            SubdomainConfig(
                ui_name="Spiritual and Self Growth",
                backend_name="spiritual_self_growth",
                description="Spiritual path, meditation, and self-development guidance",
                aliases=["spirituality", "moksha", "self growth", "meditation"]
            ),
        ]
    ),
    
    # 2. Lost / Missing
    DomainConfig(
        ui_name="Lost / Missing",
        backend_name="lost_missing",
        description="Predictions about lost or missing persons and belongings",
        order=2,
        subdomains=[
            SubdomainConfig(
                ui_name="Lost Person or Belonging",
                backend_name="lost_person_or_belonging",
                description="Finding lost persons, pets, or valuable belongings",
                aliases=["missing person", "lost item", "lost property"],
                is_implemented=False
            ),
        ]
    ),
    
    # 3. Marriage
    DomainConfig(
        ui_name="Marriage",
        backend_name="marriage",
        description="Marriage predictions including timing, compatibility, and marital life",
        order=3,
        subdomains=[
            SubdomainConfig(
                ui_name="Kundali Matching and Timing",
                backend_name="kundali_matching_timing",
                description="Match-making analysis and auspicious timing for marriage",
                aliases=["kundali milan", "gun milan", "match making", "marriage timing"],
                requires_person2=True
            ),
            SubdomainConfig(
                ui_name="Marriage Prospects",
                backend_name="marriage_prospects",
                description="Analysis of marriage likelihood, timing, and favorable periods",
                aliases=["when will i marry", "marriage prediction", "vivah yog"]
            ),
            SubdomainConfig(
                ui_name="Stability and Challenges",
                backend_name="marital_stability",
                description="Assessment of marriage stability, challenges, and remedies",
                aliases=["marital stability", "marriage problems", "divorce yoga", "separation"]
            ),
        ]
    ),
    
    # 4. Love Relationship
    DomainConfig(
        ui_name="Love Relationship",
        backend_name="love_relationship",
        description="Love and romantic relationship predictions",
        order=4,
        subdomains=[
            SubdomainConfig(
                ui_name="Attracting Love",
                backend_name="attracting_love",
                description="Finding love and attracting romantic partners",
                aliases=["finding love", "love life", "romance"]
            ),
            SubdomainConfig(
                ui_name="Break-up",
                backend_name="breakup",
                description="Analysis of relationship challenges and potential breakups",
                aliases=["breakup", "separation", "relationship end"]
            ),
            SubdomainConfig(
                ui_name="Strength and Outcome",
                backend_name="strength_and_outcome",
                description="Relationship strength assessment and future outcome",
                aliases=["relationship strength", "love outcome"]
            ),
        ]
    ),
    
    # 5. Parenting
    DomainConfig(
        ui_name="Parenting",
        backend_name="parenting",
        description="Family planning and parenting guidance",
        order=5,
        subdomains=[
            SubdomainConfig(
                ui_name="Family Planning and Parenting",
                backend_name="family_planning_and_parenting",
                description="Childbirth timing, fertility, and parenting guidance",
                aliases=["children", "childbirth", "pregnancy", "fertility", "santan yog"]
            ),
        ]
    ),
    
    # 6. Child's Development and Education
    DomainConfig(
        ui_name="Child's Development and Education",
        backend_name="child",
        description="Child's education, health, and overall development",
        order=6,
        subdomains=[
            SubdomainConfig(
                ui_name="Education Guidance",
                backend_name="education_guidance",
                description="Academic path, field of study, and educational success",
                aliases=["child education", "studies", "school", "academics"]
            ),
            SubdomainConfig(
                ui_name="Health Guidance",
                backend_name="health_guidance",
                description="Child's health, wellness, and developmental milestones",
                aliases=["child health", "development", "growth"]
            ),
        ]
    ),
    
    # 7. Family and Friends
    DomainConfig(
        ui_name="Family and Friends",
        backend_name="family_friends",
        description="Relationships with family members and social connections",
        order=7,
        subdomains=[
            SubdomainConfig(
                ui_name="Parents and Siblings",
                backend_name="parents_siblings",
                description="Relationship with parents and siblings",
                aliases=["parents", "siblings", "mother", "father", "brother", "sister"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Extended Family",
                backend_name="extended_family",
                description="Relations with extended family members",
                aliases=["relatives", "in-laws", "joint family"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Strength of Friendships",
                backend_name="friendships",
                description="Quality and longevity of friendships",
                aliases=["friends", "friendship", "social circle"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Social Status and Reputation",
                backend_name="social_status",
                description="Social standing, reputation, and public image",
                aliases=["reputation", "status", "fame", "recognition"],
                is_implemented=False
            ),
        ]
    ),
    
    # 8. Career and Profession
    DomainConfig(
        ui_name="Career and Profession",
        backend_name="career",
        description="Career path, job prospects, and professional growth",
        order=8,
        subdomains=[
            SubdomainConfig(
                ui_name="Career Discovery and Employment",
                backend_name="career_discovery_and_employment",
                description="Finding the right career and job opportunities",
                aliases=["job", "employment", "career path", "profession"]
            ),
            SubdomainConfig(
                ui_name="Growth and Security",
                backend_name="growth_and_security",
                description="Career growth prospects and job stability",
                aliases=["promotion", "job security", "career growth"]
            ),
            SubdomainConfig(
                ui_name="Career Changes",
                backend_name="career_changes",
                description="Job transitions and career pivots",
                aliases=["job change", "career switch", "new job"]
            ),
            SubdomainConfig(
                ui_name="International Career",
                backend_name="international_career",
                description="Overseas job opportunities and international careers",
                aliases=["foreign job", "overseas career", "abroad work"]
            ),
        ]
    ),
    
    # 9. Business and Entrepreneurship
    DomainConfig(
        ui_name="Business and Entrepreneurship",
        backend_name="business",
        description="Business ventures, entrepreneurship, and commercial success",
        order=9,
        subdomains=[
            SubdomainConfig(
                ui_name="Starting New Business",
                backend_name="starting_new_business",
                description="Auspicious timing and prospects for new ventures",
                aliases=["new business", "startup", "entrepreneurship"]
            ),
            SubdomainConfig(
                ui_name="Growing Existing Business",
                backend_name="growing_existing_business",
                description="Business expansion and growth opportunities",
                aliases=["business growth", "expansion", "scaling"]
            ),
            SubdomainConfig(
                ui_name="Facing Challenges in Business",
                backend_name="facing_challenges_in_business",
                description="Overcoming business obstacles and challenges",
                aliases=["business problems", "challenges", "obstacles"]
            ),
        ]
    ),
    
    # 10. Finance and Property
    DomainConfig(
        ui_name="Finance and Property",
        backend_name="finance",
        description="Financial prospects, investments, and property matters",
        order=10,
        subdomains=[
            SubdomainConfig(
                ui_name="Prospects of Investments",
                backend_name="prospects_of_investments",
                description="Investment opportunities and returns analysis",
                aliases=["investments", "stocks", "mutual funds", "wealth"]
            ),
            SubdomainConfig(
                ui_name="Facing Financial Problems",
                backend_name="facing_financial_problems",
                description="Financial difficulties and debt management",
                aliases=["financial problems", "debt", "loans", "money problems"]
            ),
            SubdomainConfig(
                ui_name="Buying Home or Land",
                backend_name="buying_home_or_land",
                description="Property acquisition and real estate matters",
                aliases=["property", "house", "land", "real estate"]
            ),
        ]
    ),
    
    # 11. Legal Matters
    DomainConfig(
        ui_name="Legal Matters",
        backend_name="legal",
        description="Legal issues, court cases, and litigation outcomes",
        order=11,
        subdomains=[
            SubdomainConfig(
                ui_name="Fighting Court Case",
                backend_name="court_case",
                description="General litigation and court case outcomes",
                aliases=["court case", "lawsuit", "litigation"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Family Legal Issue",
                backend_name="family_legal",
                description="Family-related legal matters and disputes",
                aliases=["family dispute", "inheritance", "will"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Legal Issue in Business",
                backend_name="business_legal",
                description="Business-related legal matters",
                aliases=["business dispute", "commercial litigation"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Property Case",
                backend_name="property_case",
                description="Property-related legal disputes",
                aliases=["property dispute", "land dispute"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Marriage Court Case",
                backend_name="marriage_legal",
                description="Divorce, alimony, and marriage-related legal matters",
                aliases=["divorce case", "alimony", "maintenance"],
                is_implemented=False
            ),
            SubdomainConfig(
                ui_name="Other Legal Issue",
                backend_name="other_legal",
                description="Other legal matters not covered above",
                aliases=["legal issue", "other legal"],
                is_implemented=False
            ),
        ]
    ),
    
    # 12. Physical and Mental Health
    DomainConfig(
        ui_name="Physical and Mental Health",
        backend_name="health",
        description="Health predictions and wellness guidance",
        order=12,
        subdomains=[
            SubdomainConfig(
                ui_name="Physical and Mental Health",
                backend_name="physical_and_mental_health",
                description="Overall health outlook, ailments, and recovery",
                aliases=["health", "wellness", "disease", "recovery", "mental health"]
            ),
        ]
    ),
    
    # 13. Travel
    DomainConfig(
        ui_name="Travel",
        backend_name="travel",
        description="Travel predictions and journey outcomes",
        order=13,
        subdomains=[
            SubdomainConfig(
                ui_name="Travel",
                backend_name="travel",
                description="Travel prospects, journey success, and auspicious timing",
                aliases=["travel", "journey", "trip", "vacation"],
                is_implemented=False
            ),
        ]
    ),
    
    # 14. Foreign Settlement
    DomainConfig(
        ui_name="Foreign Settlement",
        backend_name="foreign",
        description="Overseas settlement and immigration prospects",
        order=14,
        subdomains=[
            SubdomainConfig(
                ui_name="Foreign Settlement",
                backend_name="foreign_settlement",
                description="Immigration, visa, and settling abroad",
                aliases=["abroad", "immigration", "visa", "settle abroad"]
            ),
        ]
    ),
]


# ========================
# Domain Mapper Class
# ========================

class DomainMapper:
    """Singleton class for domain/subdomain resolution"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._ui_to_backend_domain: Dict[str, str] = {}
        self._backend_to_ui_domain: Dict[str, str] = {}
        self._ui_to_backend_subdomain: Dict[str, Dict[str, str]] = {}
        self._backend_to_ui_subdomain: Dict[str, Dict[str, str]] = {}
        self._alias_to_subdomain: Dict[str, Dict[str, str]] = {}
        self._domain_configs: Dict[str, DomainConfig] = {}
        self._subdomain_configs: Dict[str, Dict[str, SubdomainConfig]] = {}
        
        self._build_lookups()
        self._initialized = True
    
    def _build_lookups(self):
        """Build all lookup dictionaries"""
        for domain in DOMAIN_CONFIG:
            self._ui_to_backend_domain[domain.ui_name.lower()] = domain.backend_name
            self._backend_to_ui_domain[domain.backend_name] = domain.ui_name
            self._domain_configs[domain.backend_name] = domain
            
            self._ui_to_backend_subdomain[domain.backend_name] = {}
            self._backend_to_ui_subdomain[domain.backend_name] = {}
            self._alias_to_subdomain[domain.backend_name] = {}
            self._subdomain_configs[domain.backend_name] = {}
            
            for sub in domain.subdomains:
                self._ui_to_backend_subdomain[domain.backend_name][sub.ui_name.lower()] = sub.backend_name
                self._backend_to_ui_subdomain[domain.backend_name][sub.backend_name] = sub.ui_name
                self._subdomain_configs[domain.backend_name][sub.backend_name] = sub
                
                for alias in sub.aliases:
                    self._alias_to_subdomain[domain.backend_name][alias.lower()] = sub.backend_name
    
    def get_backend_domain(self, ui_domain: str) -> Optional[str]:
        """Convert UI domain name to backend folder name"""
        result = self._ui_to_backend_domain.get(ui_domain.lower())
        if result:
            return result
        if ui_domain in self._backend_to_ui_domain:
            return ui_domain
        return None
    
    def get_ui_domain(self, backend_domain: str) -> Optional[str]:
        """Convert backend folder name to UI domain name"""
        return self._backend_to_ui_domain.get(backend_domain)
    
    def get_backend_subdomain(self, domain: str, ui_subdomain: str) -> Optional[str]:
        """Convert UI subdomain name to backend folder name"""
        backend_domain = self.get_backend_domain(domain)
        if not backend_domain:
            return None
        
        subdomains = self._ui_to_backend_subdomain.get(backend_domain, {})
        result = subdomains.get(ui_subdomain.lower())
        if result:
            return result
        
        aliases = self._alias_to_subdomain.get(backend_domain, {})
        result = aliases.get(ui_subdomain.lower())
        if result:
            return result
        
        if ui_subdomain in self._backend_to_ui_subdomain.get(backend_domain, {}):
            return ui_subdomain
        
        return None
    
    def resolve(self, domain: str, subdomain: str) -> Tuple[Optional[str], Optional[str]]:
        """Resolve UI domain and subdomain to backend names"""
        backend_domain = self.get_backend_domain(domain)
        if not backend_domain:
            return None, None
        backend_subdomain = self.get_backend_subdomain(backend_domain, subdomain)
        return backend_domain, backend_subdomain
    
    def is_implemented(self, domain: str, subdomain: str) -> bool:
        """Check if subdomain has backend implementation"""
        backend_domain = self.get_backend_domain(domain)
        if not backend_domain:
            return False
        backend_subdomain = self.get_backend_subdomain(backend_domain, subdomain)
        if not backend_subdomain:
            return False
        config = self._subdomain_configs.get(backend_domain, {}).get(backend_subdomain)
        return config.is_implemented if config else False
    
    def requires_person2(self, domain: str, subdomain: str) -> bool:
        """Check if subdomain requires two-person analysis"""
        backend_domain = self.get_backend_domain(domain)
        if not backend_domain:
            return False
        backend_subdomain = self.get_backend_subdomain(backend_domain, subdomain)
        if not backend_subdomain:
            return False
        config = self._subdomain_configs.get(backend_domain, {}).get(backend_subdomain)
        return config.requires_person2 if config else False
    
    def validate_domain(self, domain: str) -> Tuple[bool, str]:
        """Validate domain name"""
        backend = self.get_backend_domain(domain)
        if backend:
            return True, backend
        available = [d.ui_name for d in DOMAIN_CONFIG]
        return False, f"Invalid domain '{domain}'. Available: {available}"
    
    def validate_subdomain(self, domain: str, subdomain: str) -> Tuple[bool, str]:
        """Validate subdomain name"""
        valid, result = self.validate_domain(domain)
        if not valid:
            return False, result
        
        backend_domain = result
        backend_subdomain = self.get_backend_subdomain(backend_domain, subdomain)
        
        if backend_subdomain:
            return True, backend_subdomain
        
        domain_config = self._domain_configs.get(backend_domain)
        if domain_config:
            available = [s.ui_name for s in domain_config.subdomains]
            return False, f"Invalid subdomain '{subdomain}'. Available: {available}"
        return False, "Domain not found"
    
    def get_all_domains(self) -> List[Dict[str, Any]]:
        """Get all domains for API response"""
        result = []
        for domain in sorted(DOMAIN_CONFIG, key=lambda x: x.order):
            result.append({
                "id": domain.backend_name,
                "name": domain.ui_name,
                "description": domain.description,
                "order": domain.order,
                "subdomains": [
                    {
                        "id": sub.backend_name,
                        "name": sub.ui_name,
                        "description": sub.description,
                        "requires_person2": sub.requires_person2,
                        "is_available": sub.is_implemented
                    }
                    for sub in domain.subdomains
                ]
            })
        return result
    
    def get_implemented_subdomains(self, domain: str) -> List[str]:
        """Get implemented subdomain backend names"""
        backend_domain = self.get_backend_domain(domain)
        if not backend_domain:
            return []
        domain_config = self._domain_configs.get(backend_domain)
        if not domain_config:
            return []
        return [s.backend_name for s in domain_config.subdomains if s.is_implemented]


# Singleton instance
_mapper = DomainMapper()


# ========================
# Public API Functions
# ========================

def resolve_domain_subdomain(domain: str, subdomain: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolve UI domain/subdomain names to backend folder names.
    
    Example:
        >>> resolve_domain_subdomain("Marriage", "Marriage Prospects")
        ('marriage', 'marriage_prospects')
        
        >>> resolve_domain_subdomain("Career and Profession", "job")
        ('career', 'career_discovery_and_employment')
    """
    return _mapper.resolve(domain, subdomain)


def get_backend_domain(ui_domain: str) -> Optional[str]:
    """Convert UI domain name to backend folder name"""
    return _mapper.get_backend_domain(ui_domain)


def get_backend_subdomain(domain: str, ui_subdomain: str) -> Optional[str]:
    """Convert UI subdomain name to backend folder name"""
    return _mapper.get_backend_subdomain(domain, ui_subdomain)


def get_ui_domain(backend_domain: str) -> Optional[str]:
    """Convert backend folder name to UI domain name"""
    return _mapper.get_ui_domain(backend_domain)


def validate_domain(domain: str) -> Tuple[bool, str]:
    """Validate a domain name"""
    return _mapper.validate_domain(domain)


def validate_subdomain(domain: str, subdomain: str) -> Tuple[bool, str]:
    """Validate a subdomain name"""
    return _mapper.validate_subdomain(domain, subdomain)


def is_subdomain_implemented(domain: str, subdomain: str) -> bool:
    """Check if a subdomain has backend implementation"""
    return _mapper.is_implemented(domain, subdomain)


def requires_person2(domain: str, subdomain: str) -> bool:
    """Check if subdomain requires two-person analysis"""
    return _mapper.requires_person2(domain, subdomain)


def get_all_domains_for_api() -> List[Dict[str, Any]]:
    """Get all domains for API response"""
    return _mapper.get_all_domains()


def get_implemented_subdomains(domain: str) -> List[str]:
    """Get implemented subdomain backend names"""
    return _mapper.get_implemented_subdomains(domain)


__all__ = [
    "SubdomainConfig",
    "DomainConfig", 
    "DOMAIN_CONFIG",
    "resolve_domain_subdomain",
    "get_backend_domain",
    "get_backend_subdomain",
    "get_ui_domain",
    "validate_domain",
    "validate_subdomain",
    "is_subdomain_implemented",
    "requires_person2",
    "get_all_domains_for_api",
    "get_implemented_subdomains",
]
