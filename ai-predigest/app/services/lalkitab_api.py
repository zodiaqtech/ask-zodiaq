# ==============================================================================
# LAL KITAB REMEDIES API CLIENT
# ==============================================================================
# API: https://json.astrologyapi.com/v1/lalkitab_remedies/:planet_name
# Auth: Basic Auth with userId:apiKey
# ==============================================================================

import requests
import base64
import logging
from typing import Dict, List, Optional, Any
from functools import lru_cache
from config.settings import get_settings

logger = logging.getLogger(__name__)

# ==============================================================================
# DOMAIN-PLANET MAPPING
# Maps domains to their key signifying planets
# ==============================================================================
DOMAIN_KEY_PLANETS: Dict[str, Dict[str, Any]] = {
    "marriage": {
        "primary": ["Venus", "Jupiter", "Moon"],
        "secondary": ["Mars", "Saturn", "Rahu"],
        "houses": [7, 2, 11],
        "description": "Marriage & Relationships"
    },
    "career": {
        "primary": ["Saturn", "Sun", "Mercury"],
        "secondary": ["Jupiter", "Mars"],
        "houses": [10, 6, 2],
        "description": "Career & Profession"
    },
    "finance": {
        "primary": ["Jupiter", "Venus", "Mercury"],
        "secondary": ["Moon", "Sun"],
        "houses": [2, 11, 5],
        "description": "Wealth & Finance"
    },
    "health": {
        "primary": ["Sun", "Moon", "Mars"],
        "secondary": ["Saturn", "Rahu", "Ketu"],
        "houses": [1, 6, 8],
        "description": "Health & Wellness"
    },
    "foreign": {
        "primary": ["Rahu", "Moon", "Saturn"],
        "secondary": ["Venus", "Jupiter"],
        "houses": [12, 9, 7],
        "description": "Foreign Travel & Settlement"
    },
    "business": {
        "primary": ["Mercury", "Jupiter", "Sun"],
        "secondary": ["Mars", "Saturn"],
        "houses": [7, 10, 11],
        "description": "Business & Entrepreneurship"
    },
    "child": {
        "primary": ["Jupiter", "Moon", "Mercury"],
        "secondary": ["Venus", "Sun"],
        "houses": [5, 9, 11],
        "description": "Children & Education"
    },
    "parenting": {
        "primary": ["Jupiter", "Moon", "Venus"],
        "secondary": ["Mercury", "Mars"],
        "houses": [5, 9, 4],
        "description": "Parenting & Family"
    },
    "love_relationship": {
        "primary": ["Venus", "Moon", "Mars"],
        "secondary": ["Rahu", "Mercury"],
        "houses": [5, 7, 11],
        "description": "Love & Relationships"
    },
    "general_guidance": {
        "primary": ["Sun", "Moon", "Jupiter"],
        "secondary": ["Saturn", "Mercury"],
        "houses": [1, 9, 10],
        "description": "General Life Guidance"
    }
}

# Planet dignity indicators
PLANET_DEBILITATION = {
    "Sun": "Libra",
    "Moon": "Scorpio",
    "Mars": "Cancer",
    "Mercury": "Pisces",
    "Jupiter": "Capricorn",
    "Venus": "Virgo",
    "Saturn": "Aries"
}

PLANET_ENEMY_SIGNS = {
    "Sun": ["Libra", "Capricorn", "Aquarius"],
    "Moon": ["Scorpio", "Capricorn", "Aquarius"],
    "Mars": ["Cancer", "Libra", "Taurus"],
    "Mercury": ["Pisces", "Sagittarius"],
    "Jupiter": ["Capricorn", "Aquarius", "Gemini", "Virgo"],
    "Venus": ["Virgo", "Aries", "Scorpio"],
    "Saturn": ["Aries", "Leo", "Cancer"]
}

# Dusthana houses (6, 8, 12 are generally challenging)
DUSTHANA_HOUSES = {6, 8, 12}


class LalKitabAPI:
    """
    Client for Lal Kitab Remedies API from astrologyapi.com
    
    Fetches planetary remedies based on planet position in houses.
    """
    
    BASE_URL = "https://json.astrologyapi.com/v1"
    
    def __init__(self, user_id: str = None, api_key: str = None):
        """
        Initialize the API client.
        
        Args:
            user_id: AstrologyAPI user ID (from environment if not provided)
            api_key: AstrologyAPI key (from environment if not provided)
        """
        settings = get_settings()
        self.user_id = user_id or getattr(settings, 'ASTROLOGY_API_USER_ID', None)
        self.api_key = api_key or getattr(settings, 'ASTROLOGY_API_KEY', None)
        
        if self.user_id and self.api_key:
            # Create Basic Auth header
            credentials = f"{self.user_id}:{self.api_key}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self.headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json"
            }
            self.configured = True
            logger.info("✅ LalKitabAPI configured with credentials")
        else:
            self.headers = {}
            self.configured = False
            logger.warning("⚠️ LalKitabAPI credentials not configured - using mock data")
    
    def fetch_planet_remedies(
        self,
        planet_name: str,
        dob: str,
        tob: str,
        lat: float,
        lon: float,
        tz: float = 5.5,
        language: str = "Hindi"
    ) -> Dict[str, Any]:
        """
        Fetch Lal Kitab remedies for a specific planet.
        
        Args:
            planet_name: Name of the planet (Sun, Moon, Mars, etc.)
            dob: Date of birth (DD/MM/YYYY or YYYY-MM-DD)
            tob: Time of birth (HH:MM)
            lat: Birth latitude
            lon: Birth longitude
            tz: Timezone offset (default 5.5 for IST)
            language: Output language - "Hindi" or "English"
            
        Returns:
            Dict containing planet, house, descriptions and remedies
        """
        # Normalize planet name
        planet_name = planet_name.title()
        
        # Validate planet name
        valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        if planet_name not in valid_planets:
            logger.warning(f"Invalid planet name: {planet_name}")
            return {}
        
        url = f"{self.BASE_URL}/lalkitab_remedies/{planet_name.lower()}"
        
        # Parse date
        if "/" in dob:
            day, month, year = dob.split("/")
        elif "-" in dob:
            year, month, day = dob.split("-")
        else:
            logger.error(f"Invalid date format: {dob}")
            return {}
        
        payload = {
            "day": int(day),
            "month": int(month),
            "year": int(year),
            "hour": int(tob.split(":")[0]),
            "min": int(tob.split(":")[1]),
            "lat": lat,
            "lon": lon,
            "tzone": tz
        }
        
        logger.info(f"🌐 [LALKITAB_API] Fetching remedies for {planet_name} (language: {language})")
        logger.debug(f"🌐 [LALKITAB_API] URL: {url}")
        
        if not self.configured:
            # Return mock data when not configured (with language support)
            return self._get_mock_remedies(planet_name, language=language)
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            logger.info(f"🌐 [LALKITAB_API] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ [LALKITAB_API] Got {len(data.get('lal_kitab_remedies', []))} remedies for {planet_name}")
                # Note: API returns English, so for Hindi we use mock data
                if language.lower() == "hindi":
                    return self._get_mock_remedies(planet_name, language=language)
                return data
            elif response.status_code == 401:
                logger.error("❌ [LALKITAB_API] Authentication failed - check credentials")
                return self._get_mock_remedies(planet_name, language=language)
            else:
                logger.warning(f"⚠️ [LALKITAB_API] Unexpected status: {response.status_code}")
                return self._get_mock_remedies(planet_name, language=language)
                
        except requests.exceptions.Timeout:
            logger.error("❌ [LALKITAB_API] Request timed out")
            return self._get_mock_remedies(planet_name, language=language)
        except Exception as e:
            logger.error(f"❌ [LALKITAB_API] Error: {e}")
            return self._get_mock_remedies(planet_name, language=language)
    
    def fetch_remedies_for_planets(
        self,
        planet_names: List[str],
        dob: str,
        tob: str,
        lat: float,
        lon: float,
        tz: float = 5.5,
        language: str = "Hindi"
    ) -> Dict[str, Dict]:
        """
        Fetch remedies for multiple planets.
        
        Args:
            planet_names: List of planet names
            dob, tob, lat, lon, tz: Birth details
            language: Output language - "Hindi" or "English"
            
        Returns:
            Dict mapping planet names to their remedy data
        """
        results = {}
        for planet in planet_names:
            data = self.fetch_planet_remedies(planet, dob, tob, lat, lon, tz, language=language)
            if data:
                results[planet] = data
        return results
    
    def _get_mock_remedies(self, planet_name: str, language: str = "English") -> Dict[str, Any]:
        """
        Return mock remedies when API is not configured.
        These are general Lal Kitab remedies for each planet.
        
        Args:
            planet_name: Name of the planet
            language: "Hindi" or "English"
        """
        # Hindi remedies
        mock_remedies_hindi = {
            "Sun": {
                "planet": "Sun",
                "house": "General",
                "lal_kitab_desc": [
                    "सूर्य पिता, सरकार, अधिकार और आत्मविश्वास का प्रतिनिधित्व करता है।",
                    "कमजोर सूर्य से पिता, सरकारी मामलों और स्वास्थ्य में समस्याएं हो सकती हैं।"
                ],
                "lal_kitab_remedies": [
                    "प्रतिदिन सूर्योदय के समय सूर्य को जल अर्पित करें।",
                    "अनामिका उंगली में माणिक्य या लाल पत्थर धारण करें।",
                    "रविवार को गेहूं और गुड़ का दान करें।",
                    "अपने पिता और बड़ों का सम्मान करें और उनकी सेवा करें।"
                ]
            },
            "Moon": {
                "planet": "Moon",
                "house": "General",
                "lal_kitab_desc": [
                    "चंद्रमा मन, माता, भावनाओं और मानसिक शांति का प्रतिनिधित्व करता है।",
                    "कमजोर चंद्रमा से मानसिक तनाव, चिंता और माता से संबंधित समस्याएं हो सकती हैं।"
                ],
                "lal_kitab_remedies": [
                    "चांदी के गिलास में पानी पिएं।",
                    "अपने पास चांदी का चौकोर टुकड़ा रखें।",
                    "सोमवार को चावल, दूध जैसी सफेद वस्तुओं का दान करें।",
                    "अपनी माता का सम्मान करें और उनकी सेवा करें।"
                ]
            },
            "Mars": {
                "planet": "Mars",
                "house": "General",
                "lal_kitab_desc": [
                    "मंगल साहस, ऊर्जा, भाई-बहन और संपत्ति का प्रतिनिधित्व करता है।",
                    "कमजोर मंगल से साहस की कमी, संपत्ति विवाद और क्रोध की समस्या हो सकती है।"
                ],
                "lal_kitab_remedies": [
                    "मंगलवार को लाल मसूर दाल का दान करें।",
                    "कुत्तों को मीठी रोटी खिलाएं।",
                    "अपनी जेब में लाल रूमाल रखें।",
                    "नियमित रूप से हनुमान चालीसा का पाठ करें।"
                ]
            },
            "Mercury": {
                "planet": "Mercury",
                "house": "General",
                "lal_kitab_desc": [
                    "बुध बुद्धि, संचार और व्यापार का प्रतिनिधित्व करता है।",
                    "कमजोर बुध से संचार की समस्याएं और व्यापारिक परेशानियां हो सकती हैं।"
                ],
                "lal_kitab_remedies": [
                    "बुधवार को हरी मूंग दाल का दान करें।",
                    "गायों को हरा चारा खिलाएं।",
                    "कनिष्ठा उंगली में पन्ना या हरा पत्थर धारण करें।",
                    "मामा-मौसी आदि मातृ पक्ष के रिश्तेदारों से अच्छे संबंध रखें।"
                ]
            },
            "Jupiter": {
                "planet": "Jupiter",
                "house": "General",
                "lal_kitab_desc": [
                    "बृहस्पति ज्ञान, संतान, भाग्य और आध्यात्मिकता का प्रतिनिधित्व करता है।",
                    "कमजोर बृहस्पति से संतान, भाग्य और आध्यात्मिक विकास में समस्याएं हो सकती हैं।"
                ],
                "lal_kitab_remedies": [
                    "प्रतिदिन माथे पर केसर का तिलक लगाएं।",
                    "गुरुवार को हल्दी, चना दाल जैसी पीली वस्तुओं का दान करें।",
                    "गुरुजनों और बड़ों का सम्मान करें।",
                    "नियमित रूप से मंदिर जाएं।"
                ]
            },
            "Venus": {
                "planet": "Venus",
                "house": "General",
                "lal_kitab_desc": [
                    "शुक्र प्रेम, विवाह, सौंदर्य और विलासिता का प्रतिनिधित्व करता है।",
                    "कमजोर शुक्र से वैवाहिक समस्याएं और सुख-सुविधाओं की कमी हो सकती है।"
                ],
                "lal_kitab_remedies": [
                    "शुक्रवार को चावल, चीनी जैसी सफेद वस्तुओं का दान करें।",
                    "अनामिका उंगली में हीरा या ओपल धारण करें।",
                    "गायों को हरा चारा खिलाएं।",
                    "अपने जीवनसाथी का सम्मान करें और सौहार्दपूर्ण संबंध बनाए रखें।"
                ]
            },
            "Saturn": {
                "planet": "Saturn",
                "house": "General",
                "lal_kitab_desc": [
                    "शनि अनुशासन, कर्म, सेवकों और दीर्घायु का प्रतिनिधित्व करता है।",
                    "कमजोर शनि से देरी, बाधाएं और स्वास्थ्य समस्याएं हो सकती हैं।"
                ],
                "lal_kitab_remedies": [
                    "शनिवार को सरसों का तेल, उड़द दाल जैसी काली वस्तुओं का दान करें।",
                    "कौओं को मीठी रोटी खिलाएं।",
                    "गरीबों और जरूरतमंदों की सेवा करें।",
                    "मध्यमा उंगली में लोहे की अंगूठी पहनें।"
                ]
            },
            "Rahu": {
                "planet": "Rahu",
                "house": "General",
                "lal_kitab_desc": [
                    "राहु विदेशी वस्तुओं, भ्रम और अचानक परिवर्तनों का प्रतिनिधित्व करता है।",
                    "पीड़ित राहु से भ्रम, व्यसन और अचानक परेशानियां हो सकती हैं।"
                ],
                "lal_kitab_remedies": [
                    "अपने तकिए के नीचे सौंफ रखें।",
                    "शनिवार को बिजली के सामान या नीली वस्तुओं का दान करें।",
                    "नियमित रूप से पक्षियों को दाना खिलाएं।",
                    "उचित परामर्श के बाद गोमेद धारण करें।"
                ]
            },
            "Ketu": {
                "planet": "Ketu",
                "house": "General",
                "lal_kitab_desc": [
                    "केतु आध्यात्मिकता, वैराग्य और पूर्व कर्मों का प्रतिनिधित्व करता है।",
                    "पीड़ित केतु से आध्यात्मिक भ्रम और अप्रत्याशित हानि हो सकती है।"
                ],
                "lal_kitab_remedies": [
                    "गरीबों को कंबल दान करें।",
                    "कुत्तों को मीठी रोटी खिलाएं।",
                    "उचित परामर्श के बाद लहसुनिया धारण करें।",
                    "नियमित रूप से ध्यान और आध्यात्मिक साधना करें।"
                ]
            }
        }
        
        # English remedies (original)
        mock_remedies_english = {
            "Sun": {
                "planet": "Sun",
                "house": "General",
                "lal_kitab_desc": [
                    "Sun represents father, government, authority, and self-confidence.",
                    "Weak Sun may cause issues with father, government matters, and health."
                ],
                "lal_kitab_remedies": [
                    "Offer water to the Sun at sunrise.",
                    "Wear ruby or substitute red stone on ring finger.",
                    "Donate wheat and jaggery on Sundays.",
                    "Respect and serve your father and elders."
                ]
            },
            "Moon": {
                "planet": "Moon",
                "house": "General",
                "lal_kitab_desc": [
                    "Moon represents mind, mother, emotions, and mental peace.",
                    "Weak Moon may cause mental stress, anxiety, and issues with mother."
                ],
                "lal_kitab_remedies": [
                    "Drink water in silver glass.",
                    "Keep a square piece of silver with you.",
                    "Donate white items like rice, milk on Mondays.",
                    "Respect and serve your mother."
                ]
            },
            "Mars": {
                "planet": "Mars",
                "house": "General",
                "lal_kitab_desc": [
                    "Mars represents courage, energy, siblings, and property.",
                    "Weak Mars may cause lack of courage, property disputes, and anger issues."
                ],
                "lal_kitab_remedies": [
                    "Donate red lentils (masoor dal) on Tuesdays.",
                    "Feed sweet bread to dogs.",
                    "Keep red handkerchief in your pocket.",
                    "Recite Hanuman Chalisa regularly."
                ]
            },
            "Mercury": {
                "planet": "Mercury",
                "house": "General",
                "lal_kitab_desc": [
                    "Mercury represents intelligence, communication, and business.",
                    "Weak Mercury may cause communication issues and business problems."
                ],
                "lal_kitab_remedies": [
                    "Donate green moong dal on Wednesdays.",
                    "Feed green grass to cows.",
                    "Wear emerald or green stone on little finger.",
                    "Maintain good relations with maternal relatives."
                ]
            },
            "Jupiter": {
                "planet": "Jupiter",
                "house": "General",
                "lal_kitab_desc": [
                    "Jupiter represents wisdom, children, fortune, and spirituality.",
                    "Weak Jupiter may cause issues with children, fortune, and spiritual growth."
                ],
                "lal_kitab_remedies": [
                    "Apply saffron tilak on forehead daily.",
                    "Donate yellow items like turmeric, gram dal on Thursdays.",
                    "Respect teachers and elders.",
                    "Visit temples regularly."
                ]
            },
            "Venus": {
                "planet": "Venus",
                "house": "General",
                "lal_kitab_desc": [
                    "Venus represents love, marriage, beauty, and luxuries.",
                    "Weak Venus may cause marital problems and lack of comforts."
                ],
                "lal_kitab_remedies": [
                    "Donate white items like rice, sugar on Fridays.",
                    "Wear diamond or opal on ring finger.",
                    "Feed cows with green fodder.",
                    "Respect your spouse and maintain harmonious relationships."
                ]
            },
            "Saturn": {
                "planet": "Saturn",
                "house": "General",
                "lal_kitab_desc": [
                    "Saturn represents discipline, karma, servants, and longevity.",
                    "Weak Saturn may cause delays, obstacles, and health issues."
                ],
                "lal_kitab_remedies": [
                    "Donate black items like mustard oil, urad dal on Saturdays.",
                    "Feed crows with sweet chapati.",
                    "Serve the poor and needy.",
                    "Wear iron ring on middle finger."
                ]
            },
            "Rahu": {
                "planet": "Rahu",
                "house": "General",
                "lal_kitab_desc": [
                    "Rahu represents foreign things, illusions, and sudden changes.",
                    "Afflicted Rahu may cause confusion, addictions, and sudden troubles."
                ],
                "lal_kitab_remedies": [
                    "Keep fennel seeds (saunf) under your pillow.",
                    "Donate electrical items or blue items on Saturdays.",
                    "Feed birds regularly.",
                    "Wear hessonite (gomed) after proper consultation."
                ]
            },
            "Ketu": {
                "planet": "Ketu",
                "house": "General",
                "lal_kitab_desc": [
                    "Ketu represents spirituality, detachment, and past karma.",
                    "Afflicted Ketu may cause spiritual confusion and unexpected losses."
                ],
                "lal_kitab_remedies": [
                    "Donate blankets to the poor.",
                    "Feed dogs with sweet bread.",
                    "Wear cat's eye (lehsunia) after proper consultation.",
                    "Perform regular meditation and spiritual practices."
                ]
            }
        }
        
        # Select based on language
        if language.lower() == "hindi":
            mock_remedies = mock_remedies_hindi
        else:
            mock_remedies = mock_remedies_english
        
        return mock_remedies.get(planet_name, {
            "planet": planet_name,
            "house": "General",
            "lal_kitab_desc": [f"{planet_name} जीवन के विशिष्ट क्षेत्रों को प्रभावित करता है।" if language.lower() == "hindi" else f"{planet_name} influences specific areas of life."],
            "lal_kitab_remedies": [f"{planet_name} के विशिष्ट उपायों के लिए ज्योतिषी से परामर्श करें।" if language.lower() == "hindi" else f"Consult an astrologer for {planet_name} specific remedies."]
        })


class WeakPlanetIdentifier:
    """
    Identifies weak/afflicted planets from a horoscope that need remedies.
    
    Considers:
    - Planet dignity (debilitation, enemy sign)
    - Combustion status
    - Retrograde status
    - House placement (dusthana houses)
    - Domain relevance
    """
    
    @staticmethod
    def identify_weak_planets(
        planets: Dict[str, Dict],
        domain: str,
        vedic_planets: Dict[str, Dict] = None,
        max_planets: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify weak planets that need remedies for a specific domain.
        
        Args:
            planets: KP planet data dict
            domain: The domain being analyzed (marriage, career, etc.)
            vedic_planets: Optional Vedic planet data for additional analysis
            max_planets: Maximum number of weak planets to return
            
        Returns:
            List of weak planet info dicts, sorted by weakness score (highest first)
        """
        domain_lower = domain.lower().replace(" ", "_")
        domain_config = DOMAIN_KEY_PLANETS.get(domain_lower, DOMAIN_KEY_PLANETS["general_guidance"])
        
        primary_planets = domain_config["primary"]
        secondary_planets = domain_config["secondary"]
        domain_houses = domain_config.get("houses", [])
        
        weak_planets = []
        
        # Use vedic_planets if available, otherwise use KP planets
        analysis_planets = vedic_planets if vedic_planets else planets
        
        for planet_name, planet_data in analysis_planets.items():
            if planet_name in ["Ascendant", "Uranus", "Neptune", "Pluto"]:
                continue
            
            weakness_score = 0
            weakness_reasons = []
            
            # Get planet details
            sign = planet_data.get("sign", "") or planet_data.get("rasi", "")
            house = planet_data.get("house", 0)
            is_retro = planet_data.get("is_retro", False) or planet_data.get("is_retrograde", False)
            is_combust = planet_data.get("is_combusted", False) or planet_data.get("is_combust", False)
            dignity = planet_data.get("dignity", "")
            
            # 1. Check if planet is relevant to domain
            is_primary = planet_name in primary_planets
            is_secondary = planet_name in secondary_planets
            
            if not is_primary and not is_secondary:
                continue  # Skip planets not relevant to this domain
            
            # Domain relevance score
            if is_primary:
                weakness_score += 2  # More weight for primary planets
            else:
                weakness_score += 1
            
            # 2. Check debilitation
            if sign and PLANET_DEBILITATION.get(planet_name) == sign:
                weakness_score += 5
                weakness_reasons.append(f"Debilitated in {sign}")
            
            # 3. Check enemy sign
            if sign and sign in PLANET_ENEMY_SIGNS.get(planet_name, []):
                weakness_score += 3
                weakness_reasons.append(f"In enemy sign {sign}")
            
            # 4. Check dignity from data
            if dignity:
                dignity_lower = dignity.lower()
                if dignity_lower == "debilitated":
                    weakness_score += 5
                    if "Debilitated" not in str(weakness_reasons):
                        weakness_reasons.append("Debilitated")
                elif dignity_lower == "enemy":
                    weakness_score += 3
                    if "enemy sign" not in str(weakness_reasons):
                        weakness_reasons.append("In enemy sign")
            
            # 5. Check combustion
            if is_combust and planet_name != "Sun":
                weakness_score += 4
                weakness_reasons.append("Combust (too close to Sun)")
            
            # 6. Check retrograde (for malefics it can be problematic)
            if is_retro and planet_name in ["Mars", "Saturn"]:
                weakness_score += 2
                weakness_reasons.append("Retrograde")
            
            # 7. Check dusthana house placement
            if house in DUSTHANA_HOUSES:
                weakness_score += 3
                weakness_reasons.append(f"Placed in house {house} (dusthana)")
            
            # 8. Check if planet lords a relevant house but is weak
            # (This could be enhanced with house lord calculation)
            
            # Only include if there are actual weakness factors
            if weakness_reasons:
                weak_planets.append({
                    "planet": planet_name,
                    "sign": sign,
                    "house": house,
                    "weakness_score": weakness_score,
                    "reasons": weakness_reasons,
                    "is_primary": is_primary,
                    "is_retrograde": is_retro,
                    "is_combust": is_combust
                })
        
        # Sort by weakness score (highest first), then by primary status
        weak_planets.sort(key=lambda x: (-x["weakness_score"], -x["is_primary"]))
        
        # Return top N weak planets
        return weak_planets[:max_planets]
    
    @staticmethod
    def get_domain_description(domain: str) -> str:
        """Get description for a domain."""
        domain_lower = domain.lower().replace(" ", "_")
        config = DOMAIN_KEY_PLANETS.get(domain_lower, {})
        return config.get("description", domain)


def get_lalkitab_remedies_for_chart(
    planets: Dict[str, Dict],
    domain: str,
    dob: str,
    tob: str,
    lat: float,
    lon: float,
    vedic_planets: Dict[str, Dict] = None,
    max_planets: int = 3,
    language: str = "Hindi",
    tz: float = 5.5
) -> Dict[str, Any]:
    """
    Main function to get Lal Kitab remedies for a chart based on domain.
    
    This is the primary function to call from astro_engine.py.
    
    Args:
        planets: KP planet data
        domain: Domain being analyzed
        dob, tob, lat, lon: Birth details
        vedic_planets: Optional Vedic planet data
        max_planets: Max weak planets to analyze
        language: Output language - "Hindi" or "English"
        
    Returns:
        Dict with weak_planets and their remedies
    """
    logger.info(f"🔮 Getting Lal Kitab remedies for domain: {domain}, language: {language}")
    
    # Step 1: Identify weak planets
    identifier = WeakPlanetIdentifier()
    weak_planets = identifier.identify_weak_planets(
        planets=planets,
        domain=domain,
        vedic_planets=vedic_planets,
        max_planets=max_planets
    )
    
    if not weak_planets:
        logger.info("✅ No significantly weak planets found for this domain")
        return {
            "weak_planets": [],
            "remedies": {},
            "domain": domain,
            "domain_description": identifier.get_domain_description(domain)
        }
    
    logger.info(f"🔍 Found {len(weak_planets)} weak planets: {[p['planet'] for p in weak_planets]}")
    
    # Step 2: Fetch remedies for weak planets
    api = LalKitabAPI()
    planet_names = [p["planet"] for p in weak_planets]
    
    remedies = api.fetch_remedies_for_planets(
        planet_names=planet_names,
        dob=dob,
        tob=tob,
        lat=lat,
        lon=lon,
        tz=tz,
        language=language  # ✅ Pass language for consistent output
    )
    
    # Step 3: Combine weak planet info with remedies
    for wp in weak_planets:
        planet = wp["planet"]
        if planet in remedies:
            wp["lal_kitab_remedies"] = remedies[planet].get("lal_kitab_remedies", [])
            wp["lal_kitab_desc"] = remedies[planet].get("lal_kitab_desc", [])
            wp["api_house"] = remedies[planet].get("house", "Unknown")
    
    return {
        "weak_planets": weak_planets,
        "remedies": remedies,
        "domain": domain,
        "domain_description": identifier.get_domain_description(domain)
    }


def format_remedies_for_llm(lalkitab_data: Dict[str, Any], language: str = "Hindi") -> str:
    """
    Format Lal Kitab remedies data for LLM prompt injection.
    
    Args:
        lalkitab_data: Output from get_lalkitab_remedies_for_chart()
        language: Output language - "Hindi" or "English"
        
    Returns:
        Formatted string for LLM context
    """
    if not lalkitab_data or not lalkitab_data.get("weak_planets"):
        return ""
    
    # Language-specific headers
    if language.lower() == "hindi":
        header = "लाल किताब उपचार संदर्भ"
        domain_label = "क्षेत्र"
        weak_planet_label = "कमजोर ग्रह"
        position_label = "स्थिति"
        house_label = "भाव"
        sign_label = "राशि"
        weakness_label = "कमजोरी के कारण"
        relevance_label = "महत्व"
        primary_label = "प्राथमिक"
        secondary_label = "द्वितीयक"
        remedies_label = "लाल किताब उपाय"
        instruction = "इन लाल किताब उपायों को उपचार खंड में शामिल करें। इन्हें अन्य ज्योतिषीय उपायों के साथ स्वाभाविक रूप से एकीकृत करें।"
    else:
        header = "LAL KITAB REMEDIES CONTEXT"
        domain_label = "Domain"
        weak_planet_label = "WEAK PLANET"
        position_label = "Position"
        house_label = "House"
        sign_label = "in"
        weakness_label = "Weakness Factors"
        relevance_label = "Relevance"
        primary_label = "Primary"
        secondary_label = "Secondary"
        remedies_label = "Lal Kitab Remedies"
        instruction = "Use these Lal Kitab remedies to enhance the remedy section. Integrate them naturally with other astrological remedies."
    
    lines = [
        "",
        "=" * 60,
        header,
        f"{domain_label}: {lalkitab_data.get('domain_description', lalkitab_data.get('domain', 'Unknown'))}",
        "=" * 60,
        ""
    ]
    
    for wp in lalkitab_data["weak_planets"]:
        planet = wp["planet"]
        lines.append(f"🔴 {weak_planet_label}: {planet}")
        lines.append(f"   {position_label}: {house_label} {wp.get('house', 'N/A')} {sign_label} {wp.get('sign', 'N/A')}")
        lines.append(f"   {weakness_label}: {', '.join(wp.get('reasons', []))}")
        relevance_type = primary_label if wp.get('is_primary') else secondary_label
        lines.append(f"   {relevance_label}: {relevance_type}")
        
        if wp.get("lal_kitab_remedies"):
            lines.append(f"   {remedies_label}:")
            for remedy in wp["lal_kitab_remedies"][:4]:  # Limit to 4 remedies
                lines.append(f"     • {remedy}")
        
        lines.append("")
    
    lines.append("=" * 60)
    lines.append(instruction)
    lines.append("=" * 60)
    
    return "\n".join(lines)


# Singleton instance
lalkitab_api = LalKitabAPI()