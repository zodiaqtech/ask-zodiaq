"""
Two-Person Timing Overlap Calculator for Kundali Matching

Finds common favorable marriage timing windows by analyzing
both partners' dasha periods and finding overlapping favorable periods.
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import math

logger = logging.getLogger(__name__)


@dataclass
class OverlapWindow:
    """Represents an overlapping favorable period for both partners"""
    start: str
    end: str
    person1_dasha: str
    person2_dasha: str
    person1_score: float
    person2_score: float
    combined_score: float
    overlap_days: int
    quality: str  # "Excellent", "Good", "Moderate"
    

def find_overlapping_timing_windows(
    person1_windows: List[Dict],
    person2_windows: List[Dict],
    min_overlap_days: int = 30,
    max_results: int = 10
) -> List[OverlapWindow]:
    """
    Find overlapping favorable timing windows between two people's charts.
    
    Algorithm:
    1. Sort both lists by start date
    2. For each person1 window, find all person2 windows that overlap
    3. Calculate overlap period and combined score
    4. Filter by minimum overlap duration
    5. Sort by combined score and return top results
    
    Args:
        person1_windows: Timing windows for person 1 (boy)
        person2_windows: Timing windows for person 2 (girl)
        min_overlap_days: Minimum overlap duration to consider (default 30 days)
        max_results: Maximum number of results to return
        
    Returns:
        List of OverlapWindow objects sorted by combined score
    """
    if not person1_windows or not person2_windows:
        logger.warning("One or both timing window lists are empty")
        return []
    
    overlaps = []
    
    # Convert string dates to datetime for comparison
    def parse_date(date_val) -> Optional[datetime]:
        if isinstance(date_val, datetime):
            return date_val
        if isinstance(date_val, str):
            try:
                return datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.fromisoformat(date_val[:10])
                except:
                    return None
        return None
    
    # Process each combination
    for w1 in person1_windows:
        w1_start = parse_date(w1.get("start"))
        w1_end = parse_date(w1.get("end"))
        
        if not w1_start or not w1_end:
            continue
            
        w1_score = w1.get("final_score") or w1.get("score") or 0
        w1_dasha = w1.get("dasha", "")
        
        for w2 in person2_windows:
            w2_start = parse_date(w2.get("start"))
            w2_end = parse_date(w2.get("end"))
            
            if not w2_start or not w2_end:
                continue
            
            w2_score = w2.get("final_score") or w2.get("score") or 0
            w2_dasha = w2.get("dasha", "")
            
            # Calculate overlap
            overlap_start = max(w1_start, w2_start)
            overlap_end = min(w1_end, w2_end)
            
            if overlap_start < overlap_end:
                overlap_days = (overlap_end - overlap_start).days
                
                if overlap_days >= min_overlap_days:
                    # Calculate combined score using geometric mean for balance
                    # This prevents one very high score from dominating
                    if w1_score > 0 and w2_score > 0:
                        combined_score = math.sqrt(w1_score * w2_score)
                    else:
                        combined_score = (w1_score + w2_score) / 2
                    
                    # Add bonus for longer overlaps
                    overlap_bonus = min(overlap_days / 30, 3) * 5  # Max 15 points bonus
                    combined_score += overlap_bonus
                    
                    # Determine quality
                    if combined_score >= 100:
                        quality = "Excellent"
                    elif combined_score >= 80:
                        quality = "Good"
                    else:
                        quality = "Moderate"
                    
                    overlaps.append(OverlapWindow(
                        start=overlap_start.strftime("%Y-%m-%d"),
                        end=overlap_end.strftime("%Y-%m-%d"),
                        person1_dasha=w1_dasha,
                        person2_dasha=w2_dasha,
                        person1_score=round(w1_score, 1),
                        person2_score=round(w2_score, 1),
                        combined_score=round(combined_score, 1),
                        overlap_days=overlap_days,
                        quality=quality
                    ))
    
    # Sort by combined score descending
    overlaps.sort(key=lambda x: x.combined_score, reverse=True)
    
    # Remove duplicates (same overlap period)
    seen_periods = set()
    unique_overlaps = []
    for o in overlaps:
        period_key = (o.start, o.end)
        if period_key not in seen_periods:
            seen_periods.add(period_key)
            unique_overlaps.append(o)
    
    logger.info(f"Found {len(unique_overlaps)} unique overlapping periods from "
                f"{len(person1_windows)} x {len(person2_windows)} combinations")
    
    return unique_overlaps[:max_results]


def format_overlapping_windows_for_llm(overlaps: List[OverlapWindow]) -> str:
    """
    Format overlapping windows into a string for LLM prompt.
    """
    if not overlaps:
        return "No overlapping favorable periods found between both charts."
    
    text = "OVERLAPPING FAVORABLE MARRIAGE PERIODS (Both Charts):\n"
    text += "=" * 70 + "\n\n"
    
    for i, o in enumerate(overlaps, 1):
        text += f"{i}. **{o.start} to {o.end}** ({o.overlap_days} days)\n"
        text += f"   Quality: {o.quality} (Combined Score: {o.combined_score})\n"
        text += f"   Boy's Dasha: {o.person1_dasha} (Score: {o.person1_score})\n"
        text += f"   Girl's Dasha: {o.person2_dasha} (Score: {o.person2_score})\n\n"
    
    return text


def convert_overlaps_to_timing_windows(overlaps: List[OverlapWindow]) -> List[Dict]:
    """
    Convert OverlapWindow objects to standard timing window dict format.
    """
    return [
        {
            "start": o.start,
            "end": o.end,
            "dasha": f"{o.person1_dasha} / {o.person2_dasha}",
            "score": o.combined_score,
            "final_score": o.combined_score,
            "person1_dasha": o.person1_dasha,
            "person2_dasha": o.person2_dasha,
            "person1_score": o.person1_score,
            "person2_score": o.person2_score,
            "overlap_days": o.overlap_days,
            "quality": o.quality,
            "is_two_person_overlap": True
        }
        for o in overlaps
    ]
