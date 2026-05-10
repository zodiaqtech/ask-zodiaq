"""
Domain Configuration for MyZodiaq Predigest API
Defines all available prediction domains and their subtopics.
"""

# ========================
# Domain Definitions
# ========================

DOMAINS = {
    "Marriage": {
        "display_name": "Marriage",
        "description": "Marriage and relationship predictions including timing, compatibility, and marital life",
        "subtopics": {
            "Marriage Prospects": {
                "display_name": "Marriage Prospects",
                "description": "Analysis of marriage timing, likelihood, and favorable periods",
                "requires_person2": False,
                "aliases": ["marriage prospects", "marriage timing", "when will i marry"]
            },
            "Marital Stability": {
                "display_name": "Marital Stability",
                "description": "Assessment of marriage stability and longevity",
                "requires_person2": False,
                "aliases": ["marital stability", "marriage stability", "married life"]
            },
            "Marriage Compatibility": {
                "display_name": "Marriage Compatibility",
                "description": "Compatibility analysis between two individuals",
                "requires_person2": True,
                "aliases": ["compatibility", "kundli matching", "match making", "gun milan"]
            },
            "Divorce and Separation": {
                "display_name": "Divorce and Separation",
                "description": "Analysis of separation possibilities and remedies",
                "requires_person2": False,
                "aliases": ["divorce", "separation", "marriage problems"]
            },
            "Second Marriage": {
                "display_name": "Second Marriage",
                "description": "Prospects and timing for second marriage",
                "requires_person2": False,
                "aliases": ["second marriage", "remarriage"]
            }
        }
    },
    "Career": {
        "display_name": "Career",
        "description": "Career and professional life predictions",
        "subtopics": {
            "Career Discovery and Employment": {
                "display_name": "Career Discovery and Employment",
                "description": "Finding the right career path and job opportunities",
                "requires_person2": False,
                "aliases": ["career discovery", "job", "employment", "career path"]
            },
            "Growth and Security": {
                "display_name": "Growth and Security",
                "description": "Career growth prospects and job stability",
                "requires_person2": False,
                "aliases": ["career growth", "promotion", "job security"]
            },
            "Career Changes": {
                "display_name": "Career Changes",
                "description": "Analysis of career transitions and job changes",
                "requires_person2": False,
                "aliases": ["job change", "career change", "career transition"]
            },
            "Foreign Settlement": {
                "display_name": "Foreign Settlement",
                "description": "Prospects of working or settling abroad",
                "requires_person2": False,
                "aliases": ["foreign", "abroad", "overseas job", "immigration"]
            }
        }
    },
    "Finance": {
        "display_name": "Finance",
        "description": "Financial prospects and wealth predictions",
        "subtopics": {
            "Financial Management and Savings": {
                "display_name": "Financial Management and Savings",
                "description": "Wealth accumulation and savings potential",
                "requires_person2": False,
                "aliases": ["finance", "savings", "wealth", "money"]
            },
            "Investments": {
                "display_name": "Investments",
                "description": "Investment opportunities and returns",
                "requires_person2": False,
                "aliases": ["investment", "stocks", "mutual funds", "returns"]
            },
            "Property and Assets": {
                "display_name": "Property and Assets",
                "description": "Property acquisition and asset accumulation",
                "requires_person2": False,
                "aliases": ["property", "real estate", "house", "land", "assets"]
            },
            "Debt and Loans": {
                "display_name": "Debt and Loans",
                "description": "Debt management and loan prospects",
                "requires_person2": False,
                "aliases": ["debt", "loan", "borrowing", "financial problems"]
            }
        }
    },
    "Health": {
        "display_name": "Health",
        "description": "Health and wellness predictions",
        "subtopics": {
            "General Health": {
                "display_name": "General Health",
                "description": "Overall health outlook and vitality",
                "requires_person2": False,
                "aliases": ["health", "wellness", "vitality"]
            },
            "Mental Health": {
                "display_name": "Mental Health",
                "description": "Mental and emotional well-being",
                "requires_person2": False,
                "aliases": ["mental health", "stress", "anxiety", "depression"]
            },
            "Chronic Conditions": {
                "display_name": "Chronic Conditions",
                "description": "Long-term health conditions and management",
                "requires_person2": False,
                "aliases": ["chronic illness", "long term health", "disease"]
            },
            "Recovery and Healing": {
                "display_name": "Recovery and Healing",
                "description": "Recovery prospects from illness",
                "requires_person2": False,
                "aliases": ["recovery", "healing", "cure"]
            }
        }
    },
    "Business": {
        "display_name": "Business",
        "description": "Business and entrepreneurship predictions",
        "subtopics": {
            "Business Success": {
                "display_name": "Business Success",
                "description": "Business prospects and success potential",
                "requires_person2": False,
                "aliases": ["business", "entrepreneurship", "startup"]
            },
            "Partnership": {
                "display_name": "Partnership",
                "description": "Business partnership compatibility and success",
                "requires_person2": True,
                "aliases": ["business partner", "partnership", "collaboration"]
            },
            "Business Expansion": {
                "display_name": "Business Expansion",
                "description": "Growth and expansion opportunities",
                "requires_person2": False,
                "aliases": ["expansion", "growth", "scaling"]
            }
        }
    },
    "Education": {
        "display_name": "Education",
        "description": "Education and learning predictions",
        "subtopics": {
            "Academic Success": {
                "display_name": "Academic Success",
                "description": "Academic performance and success",
                "requires_person2": False,
                "aliases": ["education", "studies", "academics", "exams"]
            },
            "Higher Education": {
                "display_name": "Higher Education",
                "description": "Prospects for higher studies and research",
                "requires_person2": False,
                "aliases": ["higher education", "masters", "phd", "research"]
            },
            "Competitive Exams": {
                "display_name": "Competitive Exams",
                "description": "Success in competitive examinations",
                "requires_person2": False,
                "aliases": ["competitive exams", "entrance exam", "upsc", "gate"]
            },
            "Foreign Education": {
                "display_name": "Foreign Education",
                "description": "Prospects for studying abroad",
                "requires_person2": False,
                "aliases": ["study abroad", "foreign education", "overseas studies"]
            }
        }
    },
    "Children": {
        "display_name": "Children",
        "description": "Children and progeny predictions",
        "subtopics": {
            "Childbirth": {
                "display_name": "Childbirth",
                "description": "Prospects and timing of childbirth",
                "requires_person2": False,
                "aliases": ["children", "childbirth", "pregnancy", "baby"]
            },
            "Child Health": {
                "display_name": "Child Health",
                "description": "Health prospects of children",
                "requires_person2": False,
                "aliases": ["child health", "children health"]
            },
            "Child Education": {
                "display_name": "Child Education",
                "description": "Educational prospects for children",
                "requires_person2": False,
                "aliases": ["child education", "children studies"]
            }
        }
    },
    "Legal": {
        "display_name": "Legal",
        "description": "Legal matters and litigation predictions",
        "subtopics": {
            "Court Cases": {
                "display_name": "Court Cases",
                "description": "Outcome of legal proceedings",
                "requires_person2": False,
                "aliases": ["court case", "litigation", "lawsuit", "legal case"]
            },
            "Property Disputes": {
                "display_name": "Property Disputes",
                "description": "Property related legal matters",
                "requires_person2": False,
                "aliases": ["property dispute", "land dispute"]
            }
        }
    }
}


# ========================
# Domain Functions
# ========================

def get_all_domains_info() -> dict:
    """
    Get information about all available domains.
    
    Returns:
        dict: Dictionary containing all domain configurations
    """
    return DOMAINS.copy()


def list_domain_names() -> list:
    """
    Get list of all available domain names.
    
    Returns:
        list: List of domain name strings
    """
    return list(DOMAINS.keys())


def get_domain(domain_name: str) -> dict | None:
    """
    Get a specific domain by name (case-insensitive).
    
    Args:
        domain_name: Name of the domain to retrieve
        
    Returns:
        dict: Domain configuration or None if not found
    """
    # Try exact match first
    if domain_name in DOMAINS:
        return DOMAINS[domain_name]
    
    # Try case-insensitive match
    for name, domain in DOMAINS.items():
        if name.lower() == domain_name.lower():
            return domain
    
    return None


def get_domain_info(domain_name: str) -> dict:
    """
    Get detailed information about a specific domain.
    
    Args:
        domain_name: Name of the domain
        
    Returns:
        dict: Domain information including subtopics
    """
    domain = get_domain(domain_name)
    if domain:
        return domain
    return {}


def get_subtopic_info(domain_name: str, subtopic_name: str) -> dict | None:
    """
    Get information about a specific subtopic.
    
    Args:
        domain_name: Name of the domain
        subtopic_name: Name of the subtopic
        
    Returns:
        dict: Subtopic configuration or None if not found
    """
    domain = get_domain(domain_name)
    if not domain:
        return None
    
    subtopics = domain.get("subtopics", {})
    
    # Try exact match
    if subtopic_name in subtopics:
        return subtopics[subtopic_name]
    
    # Try case-insensitive match
    for name, info in subtopics.items():
        if name.lower() == subtopic_name.lower():
            return info
        # Check aliases
        aliases = [a.lower() for a in info.get("aliases", [])]
        if subtopic_name.lower() in aliases:
            return info
    
    return None


def resolve_subtopic_alias(domain_name: str, alias: str) -> str | None:
    """
    Resolve a subtopic alias to its canonical name.
    
    Args:
        domain_name: Name of the domain
        alias: Alias to resolve
        
    Returns:
        str: Canonical subtopic name or None if not found
    """
    domain = get_domain(domain_name)
    if not domain:
        return None
    
    subtopics = domain.get("subtopics", {})
    
    # Check if it's already a canonical name
    if alias in subtopics:
        return alias
    
    # Search through aliases
    for name, info in subtopics.items():
        if alias.lower() == name.lower():
            return name
        aliases = [a.lower() for a in info.get("aliases", [])]
        if alias.lower() in aliases:
            return name
    
    return None


def validate_domain_subtopic(domain_name: str, subtopics: list) -> tuple[bool, str]:
    """
    Validate that a domain and its subtopics exist.
    
    Args:
        domain_name: Name of the domain
        subtopics: List of subtopic names to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    domain = get_domain(domain_name)
    if not domain:
        available = list_domain_names()
        return False, f"Domain '{domain_name}' not found. Available: {available}"
    
    domain_subtopics = domain.get("subtopics", {})
    
    for subtopic in subtopics:
        resolved = resolve_subtopic_alias(domain_name, subtopic)
        if not resolved:
            available = list(domain_subtopics.keys())
            return False, f"Subtopic '{subtopic}' not found in {domain_name}. Available: {available}"
    
    return True, ""


# ========================
# Exports
# ========================

__all__ = [
    "DOMAINS",
    "get_all_domains_info",
    "list_domain_names",
    "get_domain",
    "get_domain_info",
    "get_subtopic_info",
    "resolve_subtopic_alias",
    "validate_domain_subtopic"
]