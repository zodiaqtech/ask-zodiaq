# ==============================================================================
# ADDITION TO astro_api.py - For Kundali Milan API
# ==============================================================================

# Add this method to a new class or create a separate API client

import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class KundaliMilanAPI:
    """Client for Kundali Milan API"""
    
    BASE_URL = "https://zodiaqbackendindia-addxcdexgkbhe6ea.centralindia-01.azurewebsites.net/api/v1"
    
    def fetch_kundali_milan(
        self,
        boy_name: str,
        boy_dob: str,  # Format: "YYYY-MM-DD"
        boy_tob: str,  # Format: "HH:MM"
        boy_lat: float,
        boy_lon: float,
        boy_pob: str,
        girl_name: str,
        girl_dob: str,  # Format: "YYYY-MM-DD"
        girl_tob: str,  # Format: "HH:MM"
        girl_lat: float,
        girl_lon: float,
        girl_pob: str,
        service_id: str = "6836b430d123edb99abb6b2d",
        boy_tz: float = 5.5,
        girl_tz: float = 5.5
    ) -> Dict:
        """
        Fetch Kundali Milan (matching) data for marriage compatibility
        
        Args:
            boy_name: Boy's name
            boy_dob: Boy's date of birth (YYYY-MM-DD)
            boy_tob: Boy's time of birth (HH:MM)
            boy_lat: Boy's birth latitude
            boy_lon: Boy's birth longitude
            boy_pob: Boy's place of birth
            girl_name: Girl's name
            girl_dob: Girl's date of birth (YYYY-MM-DD)
            girl_tob: Girl's time of birth (HH:MM)
            girl_lat: Girl's birth latitude
            girl_lon: Girl's birth longitude
            girl_pob: Girl's place of birth
            service_id: Service identifier
            
        Returns:
            Dict containing kundali milan data including:
            - ashtakoot scores
            - dosha analysis
            - divisional charts
            - compatibility assessment
        """
        url = f"{self.BASE_URL}/astrologers/kundali-milan"
        
        payload = {
            "boy": {
                "name": boy_name,
                "dob": boy_dob,
                "tob": boy_tob,
                "pob": boy_pob,
                "lon": str(boy_lon),
                "lat": str(boy_lat),
                "gender": "male",
                "tz": boy_tz
            },
            "girl": {
                "name": girl_name,
                "dob": girl_dob,
                "tob": girl_tob,
                "pob": girl_pob,
                "lon": str(girl_lon),
                "lat": str(girl_lat),
                "gender": "female",
                "tz": girl_tz
            },
            "serviceId": service_id
        }
        
        print(f"🌐 [KUNDALI_MILAN_API] Calling API: {url}")
        print(f"🌐 [KUNDALI_MILAN_API] Payload: Boy={boy_name} ({boy_dob}), Girl={girl_name} ({girl_dob})")
        logger.info(f"🌐 Calling Kundali Milan API: Boy={boy_name}, Girl={girl_name}")
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            print(f"🌐 [KUNDALI_MILAN_API] Response status: {response.status_code}")
            logger.info(f"🌐 Kundali Milan API response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            print(f"🌐 [KUNDALI_MILAN_API] Response success: {result.get('success')}")
            
            if result.get("success"):
                data = result.get("data", {})
                ashtakoot_score = data.get("match_details", {}).get("ashtakoot", {}).get("response", {}).get("score", "N/A")
                print(f"✅ [KUNDALI_MILAN_API] Success! Ashtakoot Score: {ashtakoot_score}/36")
                logger.info(f"✅ Kundali Milan API success! Ashtakoot Score: {ashtakoot_score}/36")
                return data
            else:
                error_msg = result.get("message", "Unknown error")
                print(f"❌ [KUNDALI_MILAN_API] API returned success=False: {error_msg}")
                logger.warning(f"❌ Kundali Milan API returned success=False: {error_msg}")
                return {}
        except requests.exceptions.Timeout:
            print(f"❌ [KUNDALI_MILAN_API] Request timed out after 60 seconds")
            logger.error(f"Kundali Milan API request timed out")
            return {}
        except requests.exceptions.HTTPError as e:
            print(f"❌ [KUNDALI_MILAN_API] HTTP Error: {e}")
            logger.error(f"Kundali Milan API HTTP error: {e}")
            return {}
        except Exception as e:
            print(f"❌ [KUNDALI_MILAN_API] Exception: {type(e).__name__}: {e}")
            logger.error(f"Failed to fetch kundali milan: {e}")
            return {}


# Create singleton instance
kundali_milan_api = KundaliMilanAPI()


# ==============================================================================
# NOTE: Test code moved to __main__ block to prevent execution at import time
# ==============================================================================
if __name__ == "__main__":
    # Only run when executing this file directly, not when importing
    print("Testing Kundali Milan API...")
    milan_data = kundali_milan_api.fetch_kundali_milan(
        boy_name="Xyz",
        boy_dob="2004-01-31",
        boy_tob="03:53",
        boy_lat=22.54111111,
        boy_lon=88.33777778,
        boy_pob="Kolkata",
        girl_name="ABC",
        girl_dob="2003-08-07",
        girl_tob="21:57",
        girl_lat=22.57688000,
        girl_lon=88.31857000,
        girl_pob="Howrah"
    )
    print(f"Result: {milan_data}")