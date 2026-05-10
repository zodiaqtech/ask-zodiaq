"""
Domain → Subdomain → Question House Configuration
Structured EXACTLY like the Excel spreadsheet for easy integration

Structure:
{
    "Domain (Main Topic)": {
        "Subdomain (Subcategory)": {
            "Specific Question": {
                "primary": {house numbers},
                "secondary": {house numbers}
            }
        }
    }
}
"""

from typing import Dict, Set, Optional,List

# ═══════════════════════════════════════════════════════════════════
# COMPLETE HOUSE CONFIGURATION (Excel Structure)
# ═══════════════════════════════════════════════════════════════════

DOMAIN_SUBDOMAIN_QUESTION_HOUSES = {
    
    # ══════════════════════════════════════════════════════════════
    # GENERAL GUIDANCE
    # ══════════════════════════════════════════════════════════════
    "General Guidance": {
        "General Kundali Analysis": {
            "How is my current astrological period (dasha) and are my planets strong or weak?": {
                "primary": {1, 9, 10},
                "secondary": {2, 5, 11}
            },
            "Are there any significant doshas or adverse influences right now and when do such periods occur (e.g., Sade Sati, Graha doshas)?": {
                "primary": {1, 6, 8, 12},
                "secondary": {7}
            },
            "What are the major favorable and unfavorable planetary transits affecting me at present?": {
                "primary": {1, 10, 11},
                "secondary": {7, 9}
            },
            "When can I expect major success or fortune phases (such as Raj, Dhana, or Sanyasa yogas) and what is their timing?": {
                "primary": {1, 9, 10, 11},
                "secondary": {2, 5}
            }
            
        },
        "Spiritual and Self Growth": {
            "What is my life's purpose and is my karma aligned to achieve it?": {
                "primary": {1, 9, 10},
                "secondary": {5, 12}
            },
            "Are there any karmic debts affecting my journey?": {
                "primary": {8, 9, 12},
                "secondary": {4, 5}
            },
            "How can I effectively handle emotions such as anxiety, fear, sadness, anger and cultivate forgiveness and empathy?": {
                "primary": {1, 4, 5},
                "secondary": {12}
            },
            "I find it difficult to take decisions. Why is it so and what should I do to correct this?": {
                "primary": {1, 3, 5},
                "secondary": {9}
            },
            "Will I find the right teacher, guru, or mentor to guide me?": {
                "primary": {9, 5},
                "secondary": {10, 4}
            }
           
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # LOST/MISSING
    # ══════════════════════════════════════════════════════════════
    "Lost/Missing": {
        "Lost Person or Belonging": {
            "How can I find a missing person or lost item and is there a way to recover something that was stolen?": {
                "primary": {1, 7, 12},
                "secondary": {2, 3, 6, 8}
            },
            "Any remedies that I must follow?": {
                "primary": {1, 2, 7},
                "secondary": {9}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # MARRIAGE
    # ══════════════════════════════════════════════════════════════
    "Marriage": {
        "Marriage Prospects": {

            "Is marriage promised in the chart? If yes, when is the likely period for marriage? What factors support or challenge it, and are there indications of delay?": {
            "primary": {2, 7, 11},
            "secondary": {5, 8}
            },

            "When is the likely period for my marriage according to astrology? Are there any possible delays or reasons for them, and what is the most auspicious muhurat for my marriage?": {
                "primary": {7, 1, 2},
                "secondary": {8, 11}
            },
            "What does astrology reveal about the nature of my marriage - arranged vs. love, intercaste or interfaith possibilities, and the prospects for remarriage if applicable?": {
                "primary": {7, 5, 1},
                "secondary": {9, 4}
            },
            "What guidance can astrology offer regarding the following aspects of my future spouse and marriage? - physical, intellectual, emotional, educational, family background, financial status": {
                "primary": {7, 1},
                "secondary": {2, 4, 5, 9, 10, 11}
            },
            "What will be the direction of the birth place of my prospective spouse?": {
                "primary": {7, 12},
                "secondary": {9, 3}
            }
        },
        "Kundali Matching and Timing": {
            "Result of full Guna Milan (Ashta Koota), including Manglik, Nadi, Bhakoot doshas and overall compatibility for marriage": {
                "primary": {7, 1, 8},
                "secondary": {2, 4, 12}
            },
            "Can this marriage be advised, or are remedies required? What are the reasons for any delay and when is the best period (muhurat) to marry?": {
                "primary": {7, 1, 2, 8},
                "secondary": {9, 11}
            },
            "What is the compatibility level (physical, intellectual, emotional, educational, family and financial backgrounds) and the prospects and success of marriage in this case?": {
                "primary": {7, 1, 4, 5},
                "secondary": {2, 8, 9}
            }
            
        },
        "Stability and Challenges": {
            "Are there chances of divorce, separation, ongoing conflicts, legal disputes, post-marital relocation and in-law problems?": {
                "primary": {7, 8, 6},
                "secondary": {12, 4}
            },
            "How can issues of physical intimacy and relationship harmony after marriage be addressed, including the role of rituals, puja and relevant planetary remedies?": {
                "primary": {7, 8, 12},
                "secondary": {1, 5}
            },
            "Are there any doshas? What specific remedies exist for Manglik, Shadashtak, Nadi and Pitra doshas affecting marital stability?": {
                "primary": {1, 4, 7, 8, 12},
                "secondary": {2, 9}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # LOVE RELATIONSHIP
    # ══════════════════════════════════════════════════════════════
    "Love Relationship": {
        "Attracting Love": {
            "Will I find love and when is it likely to happen?": {
                "primary": {5, 7},
                "secondary": {1, 11}
            },
            "How can I overcome or understand experiences of unrequited love?": {
                "primary": {5, 7, 8},
                "secondary": {12, 6}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {5, 7, 1},
                "secondary": {9}
            }
        },
        "Break-up": {
            "Should I stay in my current relationship or consider a breakup and what is the risk of separation?": {
                "primary": {5, 7, 8},
                "secondary": {6, 12}
            },
            "I have experienced a breakup - will my partner return to me?": {
                "primary": {5, 7, 8},
                "secondary": {11, 9}
            },
            "What can I do to avoid a breakup and strengthen my relationship?": {
                "primary": {5, 7, 1},
                "secondary": {4, 8}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {5, 7},
                "secondary": {1, 9}
            }
        },
        "Strength and Outcome": {
            "How can I understand and improve my partner's loyalty, trust issues and our emotional and physical compatibility?": {
                "primary": {5, 7, 1},
                "secondary": {4, 8}
            },
            "Will I get married to my current partner and what is the future course of our relationship?": {
                "primary": {5, 7},
                "secondary": {1, 2, 9, 11}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {5, 7},
                "secondary": {1, 9}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # PARENTING
    # ══════════════════════════════════════════════════════════════
    "Parenting": {
        "Family Planning and Parenting": {
            "When will I have a child? Are there any problems in my kundali?": {
                "primary": {5, 1},
                "secondary": {7, 9, 11}
            },
            "What is the best time to conceive and are there any risks of miscarriage I should be aware of?": {
                "primary": {5, 1, 7},
                "secondary": {8, 9}
            },
            "How compatible are our parenting styles and how will this affect our child's development and behavior?": {
                "primary": {5, 1, 7},
                "secondary": {4, 9}
            },
            "What insights does astrology provide about the health of our future child?": {
                "primary": {5, 6},
                "secondary": {1, 8}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {5, 1, 9},
                "secondary": {7}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # CHILD'S DEVELOPMENT AND EDUCATION
    # ══════════════════════════════════════════════════════════════
    "Child": {
        "Education Guidance": {
            "What does astrology reveal about the child's aptitude, talents and possible learning deficits/challenges?": {
                "primary": {5, 4},
                "secondary": {1, 9}
            },
            "What does astrology indicate about the child's ability to excel in exams, the best field or subject for me and my prospects for higher studies, research and scholarships?": {
                "primary": {5, 4, 9},
                "secondary": {2, 11}
            },
            "What are the prospects for school or college admission and receiving scholarships?": {
                "primary": {5, 4, 11},
                "secondary": {9}
            },
            "Are there prospects for the child to move abroad for studies and if so, which country and field of study would be most favorable?": {
                "primary": {5, 4, 9, 12},
                "secondary": {11}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {5, 4, 9},
                "secondary": {1}
            }
        },
        "Health Guidance": {
            "What guidance does astrology offer regarding physical and mental growth and health concerns?": {
                "primary": {5, 1, 6},
                "secondary": {4, 8}
            },
            "Relevant Planetary remedies, Harmony/compatibility puja": {
                "primary": {5, 1, 6},
                "secondary": {9}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # FAMILY AND FRIENDS
    # ══════════════════════════════════════════════════════════════
    "Family and Friends": {
        "Parents and Siblings": {
            "What does astrology reveal about harmony with my parents, the chances of disputes and responsibilities related to elder care?": {
                "primary": {4, 9},
                "secondary": {1, 6, 8, 10}
            },
            "What does astrology reveal about harmony with my siblings and the potential for disputes?": {
                "primary": {3},
                "secondary": {6, 11}
            },
            "Remedies": {
                "primary": {3, 4, 9},
                "secondary": {1}
            }
        },
        "Extended Family": {
            "What does astrology indicate about potential problems in joint or extended family, inheritance disputes and responsibilities related to ancestral property and duties?": {
                "primary": {2, 4, 8},
                "secondary": {6, 9}
            },
            "Any remedies that I must follow?": {
                "primary": {2, 4, 8, 9},
                "secondary": {1}
            }
        },
        "Strength of Friendships": {
            "What does astrology reveal about my friendship compatibility, the strength and longevity of my friendships and the chances of disputes, quarrels, or betrayal?": {
                "primary": {11},
                "secondary": {3, 6}
            },
            "Why might my friends be ignoring me and how can I improve these relationships?": {
                "primary": {11, 6},
                "secondary": {1, 3}
            },
            "Any remedies that I must follow?": {
                "primary": {11, 1},
                "secondary": {9}
            }
        },
        "Social Status and Reputation": {
            "Will I receive recognition or honours and what does astrology indicate about my reputation and social standing?": {
                "primary": {10, 11},
                "secondary": {1, 3}
            },
            "Are there risks to my reputation due to misinformation, scandal, blackmail, or personal problems and how can I protect myself?": {
                "primary": {6, 8, 10},
                "secondary": {12}
            },
            "Why might my social circle be ignoring me and how can I improve my relationships and standing?": {
                "primary": {11, 10, 1},
                "secondary": {3}
            },
            "Any remedies that I must follow?": {
                "primary": {10, 11, 1},
                "secondary": {9}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # CAREER AND PROFESSION
    # ══════════════════════════════════════════════════════════════
    "Career": {
        "Career Discovery and Employment": {
            "What career track, field, or roles-such as government, private, or non-traditional sectors-are best suited to my natural talents?": {
                "primary": {10, 1, 5},
                "secondary": {2, 6, 9}
            },
            "Should I pursue a job now or opt for further studies for better prospects?": {
                "primary": {10, 4, 5, 9},
                "secondary": {2, 11}
            },
            "When am I likely to secure a job and what obstacles might I face in my career journey?": {
                "primary": {10, 6, 11},
                "secondary": {2, 8, 9}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {10, 1, 9},
                "secondary": {6}
            }
        },
        "Growth and Security": {
            "What does astrology reveal about my prospects for promotions, raises, transfers, leadership roles and overall success in the corporate or political spheres?": {
                "primary": {10, 11},
                "secondary": {2, 5, 9}
            },
            "Are there risks of career stagnation, failing to get recognition, workplace politics, or instability and what obstacles might I face?": {
                "primary": {10, 6, 8},
                "secondary": {12, 3}
            },
            "How can I overcome challenges and achieve greater stability and success in my career?": {
                "primary": {10, 1, 6},
                "secondary": {11, 9}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {10, 6, 9},
                "secondary": {1}
            }
        },
        "Career Changes": {
            "What is the right career path for me and when would be the most favorable time to switch careers?": {
                "primary": {10, 8},
                "secondary": {6, 11, 12}
            },
            "Should I pursue further education or make other mid-life adaptations to enhance my professional growth?": {
                "primary": {10, 4, 9},
                "secondary": {5, 11}
            },
            "What obstacles might I face in this transition and how can I overcome them?": {
                "primary": {10, 6, 8},
                "secondary": {3, 12}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {10, 8, 9},
                "secondary": {1}
            }
        },
        "International Career": {
            "Is it advisable for me to go abroad and what are my prospects for working or settling there?": {
                "primary": {10, 12},
                "secondary": {9, 7, 11}
            },
            "What challenges might I face regarding immigration, employment visas, or other obstacles and how can I overcome them?": {
                "primary": {12, 6, 7},
                "secondary": {3, 9}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {12, 9, 10},
                "secondary": {1}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # BUSINESS AND ENTREPRENEURSHIP
    # ══════════════════════════════════════════════════════════════
    "Business": {
        "Starting New Business": {
            "Am I destined for business or entrepreneurship and which industries or locations are most favorable for me to start?": {
                "primary": {10, 7, 2},
                "secondary": {11, 3}
            },
            "What are the best timings and directions for launching a business and should I consider taking a loan?": {
                "primary": {10, 11, 9},
                "secondary": {6, 7}
            },
            "Is it better for me to pursue business alone or with partners and how can I choose the right partners or address family business issues?": {
                "primary": {7, 10},
                "secondary": {2, 11, 4}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {10, 7, 9},
                "secondary": {1, 2}
            }
        },
        "Growing Existing Business": {
            "Is this the right business for me and what guidance does astrology provide for growing my business, entering new markets, or diversifying?": {
                "primary": {10, 11},
                "secondary": {2, 3, 9}
            },
            "When are the most favorable times for business growth and expansion and should I consider taking a loan?": {
                "primary": {10, 11, 9},
                "secondary": {2, 6}
            },
            "What obstacles might I face in my business journey and how can I overcome them?": {
                "primary": {10, 6, 8},
                "secondary": {12, 7}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {10, 11, 9},
                "secondary": {1, 2}
            }
        },
        "Facing Challenges in Business": {
            "Why is my business facing challenges or stagnation or downturn? When will there be improvement?": {
                "primary": {10, 6, 8},
                "secondary": {2, 11, 12}
            },
            "Should I continue my business or consider shutting it down? Should I take loan? Will I be able to repay the loan?": {
                "primary": {10, 8, 6, 11},
                "secondary": {2, 12}
            },
            "What obstacles might I face and how can I overcome them to improve my business situation?": {
                "primary": {10, 6, 8},
                "secondary": {1, 9}
            },
            "Gemstones, Puja, rituals, Relevant planetary remedies": {
                "primary": {10, 6, 8, 9},
                "secondary": {1, 11}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # FINANCE AND PROPERTY
    # ══════════════════════════════════════════════════════════════
    "Finance": {
        "Prospects Of Investments": {
            "How can I increase my income? Can you suggest any new avenues for income growth?": {
                "primary": {2, 11},
                "secondary": {10, 9}
            },
            "What are the right investment avenues for me and should I invest or trade in equity, shares, or other assets?": {
                "primary": {2, 5, 11},
                "secondary": {8, 9}
            },
            "Will I be able to purchase a house, land, vehicle, jewellery, or afford travel for pleasure and when might these opportunities arise?": {
                "primary": {4, 2, 11},
                "secondary": {12, 9}
            },
            "What financial obstacles might I face and how can I overcome them?": {
                "primary": {2, 6, 8, 11},
                "secondary": {12}
            }
        },
        "Facing Financial Problems": {
            "According to astrology, what does my birth chart reveal about my financial situation, including income stability, wealth accumulation and my ability to manage loans and debts?": {
                "primary": {2, 11},
                "secondary": {6, 8, 12}
            },
            "Will I be able to repay my current loan and is there a risk of default?": {
                "primary": {6, 11},
                "secondary": {2, 8, 12}
            },
            "Are there any risks of financial disputes, court cases, or issues related to ancestral property, loss, or damage and how can I resolve these?": {
                "primary": {6, 8, 4},
                "secondary": {2, 12}
            }
        },
        "Buying Home or Land": {
            "Will I be able to purchase or build a house or land and when would be the most auspicious time for each?": {
                "primary": {4, 11},
                "secondary": {2, 9, 12}
            },
            "Are there any risks or challenges I should be aware of in these property endeavors?": {
                "primary": {4, 8, 6},
                "secondary": {12}
            },
            "What Vastu-based layout, direction, or guidance should I consider for my property?": {
                "primary": {4},
                "secondary": {1, 12}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # LEGAL MATTERS
    # ══════════════════════════════════════════════════════════════
    "Legal Matters": {
        "Fighting Court Case": {
            "What does astrology indicate about the outcome, duration, risks and potential penalties related to my legal challenges?": {
                "primary": {6, 7, 8},
                "secondary": {10, 12}
            },
            "What does astrology indicate about the outcome, duration, risks and potential penalties related to my criminal matter?": {
                "primary": {6, 8, 12},
                "secondary": {1, 3}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {6, 8, 9},
                "secondary": {1}
            }
        },
        "Family Legal Issue": {
            "What does astrology reveal about the outcome, duration, risks and potential penalties related to my family dispute?": {
                "primary": {4, 6, 8},
                "secondary": {2, 7}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {4, 6, 9},
                "secondary": {1}
            }
        },
        "Legal Issue in Business": {
            "What does astrology reveal about the outcome, duration, risks and potential penalties of my business or partnership legal issues?": {
                "primary": {7, 6, 10},
                "secondary": {8, 12}
            },
            "Mars/Saturn pacification, legal puja, yantra": {
                "primary": {6, 7, 10},
                "secondary": {9}
            }
        },
        "Property Case": {
            "What does astrology reveal about the outcome, duration, risks and potential penalties related to my land or property dispute?": {
                "primary": {4, 6, 8},
                "secondary": {9, 12}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {4, 6, 8, 9},
                "secondary": {1}
            }
        },
        "Marriage Court Case": {
            "What does astrology reveal about the outcome, duration, risks and potential penalties of my marriage-related legal issues, such as dowry, divorce, or alimony?": {
                "primary": {6, 7, 8},
                "secondary": {12}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {6, 7, 8, 9},
                "secondary": {1}
            }
        },
        "Other Legal Issue": {
            "What does astrology reveal about the outcome, duration, risks and potential penalties related to my other legal issues?": {
                "primary": {6, 8},
                "secondary": {3, 12}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {6, 8, 9},
                "secondary": {1}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # PHYSICAL AND MENTAL HEALTH
    # ══════════════════════════════════════════════════════════════
    "Health": {
        "Physical and Mental Health": {
            "According to astrology, what does my birth chart indicate about my physical health, tendency toward illness, and overall vitality, and are there any astrological remedies or lifestyle guidelines suggested for better well-being?": {
                "primary": {1, 6},
                "secondary": {8, 12}
            },
            "Are there risks to my life expectancy, chances of chronic disease, accidents, or the need for surgery? If I must undergo surgery, when is the most auspicious time for it?": {
                "primary": {1, 6, 8},
                "secondary": {12}
            },
            "What does astrology reveal about potential mental health issues, such as depression, anxiety, or addictions and should I consult a psychiatrist or psychologist?": {
                "primary": {1, 4, 5},
                "secondary": {6, 8, 12}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {1, 6, 9},
                "secondary": {8}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # TRAVEL
    # ══════════════════════════════════════════════════════════════
    "Travel": {
        "Travel": {
            "Will I be able to visit holy places for pilgrimage and when is the most auspicious muhurat for undertaking such journeys?": {
                "primary": {9, 12},
                "secondary": {3, 5}
            },
            "When is the most favorable time for other types of travel and will my travels be successful?": {
                "primary": {3, 9},
                "secondary": {12, 11}
            },
            "Are there any risks or obstacles I might face during my pilgrimage or travels and how can I overcome them?": {
                "primary": {3, 8, 12},
                "secondary": {6, 9}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {3, 9, 12},
                "secondary": {1}
            }
        }
    },
    
    # ══════════════════════════════════════════════════════════════
    # FOREIGN SETTLEMENT
    # ══════════════════════════════════════════════════════════════
    "Foreign": {
        "Foreign Settlement": {
            "Is there scope for me to settle abroad permanently?": {
                "primary": {12, 9},
                "secondary": {7, 10}
            },
            "Will I face any delays or obstacles in obtaining permits, passport, visa, or citizenship and how can I overcome them?": {
                "primary": {12, 9, 7},
                "secondary": {3, 6}
            },
            "What does astrology reveal about my prospects for income and adjustment in the new country and are there any challenges I should be prepared for?": {
                "primary": {10, 12, 11},
                "secondary": {2, 1, 9}
            },
            "Relevant yog activation; Relevant planetary remedies, Rituals and daan for wealth": {
                "primary": {12, 9},
                "secondary": {1, 7}
            }
        }
    }
}


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR EASY INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def get_houses_for_question(
    domain: str,
    subdomain: str,
    question: str
) -> Optional[Dict[str, Set[int]]]:
    """
    Get houses for a specific question.
    
    Args:
        domain: Main Topic (e.g., "Marriage")
        subdomain: Subcategory (e.g., "Marriage Prospects")
        question: Specific question text
    
    Returns:
        Dict with primary and secondary houses, or None if not found
    
    Example:
        >>> houses = get_houses_for_question(
        ...     "Marriage",
        ...     "Marriage Prospects",
        ...     "When is the likely period for my marriage..."
        ... )
        >>> print(houses)
        {'primary': {7, 1, 2}, 'secondary': {8, 11}}
    """
    if domain not in DOMAIN_SUBDOMAIN_QUESTION_HOUSES:
        return None
    
    if subdomain not in DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain]:
        return None
    
    # Try exact match first
    if question in DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain][subdomain]:
        config = DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain][subdomain][question]
        return {
            "primary": config["primary"],
            "secondary": config["secondary"],
            "source": "exact_match"
        }
    
    # Try partial match (for similar questions)
    subdomain_questions = DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain][subdomain]
    for q_key, q_config in subdomain_questions.items():
        # Simple similarity check - if first 30 chars match
        if question[:30].lower() in q_key.lower() or q_key[:30].lower() in question.lower():
            return {
                "primary": q_config["primary"],
                "secondary": q_config["secondary"],
                "source": "partial_match",
                "matched_question": q_key
            }
    
    return None


def get_all_questions_for_subdomain(domain: str, subdomain: str) -> List[str]:
    """
    Get all configured questions for a subdomain.
    
    Args:
        domain: Main Topic
        subdomain: Subcategory
    
    Returns:
        List of question strings
    """
    if domain not in DOMAIN_SUBDOMAIN_QUESTION_HOUSES:
        return []
    
    if subdomain not in DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain]:
        return []
    
    return list(DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain][subdomain].keys())


def get_all_subdomains_for_domain(domain: str) -> List[str]:
    """
    Get all subdomains for a domain.
    
    Args:
        domain: Main Topic
    
    Returns:
        List of subdomain names
    """
    if domain not in DOMAIN_SUBDOMAIN_QUESTION_HOUSES:
        return []
    
    return list(DOMAIN_SUBDOMAIN_QUESTION_HOUSES[domain].keys())


def get_all_domains() -> List[str]:
    """Get all configured domains."""
    return list(DOMAIN_SUBDOMAIN_QUESTION_HOUSES.keys())
