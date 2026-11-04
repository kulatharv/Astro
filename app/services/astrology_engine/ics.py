"""
RFC 5545 Compliant iCalendar (.ics) Generator for Vedic Panchang Events.
Exports Ekadashi, Purnima, Amavasya, Pradosh, and Major Hindu Festivals.
Compatible with Google Calendar, Apple Calendar, Microsoft Outlook.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from app.services.astrology_engine.festival import get_upcoming_festivals


def generate_panchang_ics(
    city: str = "Pune",
    limit: int = 45,
    tz_name: str = "Asia/Kolkata"
) -> str:
    """
    Generate an RFC 5545 compliant .ics calendar string.
    """
    festivals_data = get_upcoming_festivals(limit=limit)
    if isinstance(festivals_data, dict):
        festivals: List[Dict[str, Any]] = festivals_data.get("festivals", [])
    elif isinstance(festivals_data, list):
        festivals: List[Dict[str, Any]] = festivals_data
    else:
        festivals = []
    
    now_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//AstroLogic Vedic Platform//Panchang Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Vedic Panchang Calendar - {city}",
        f"X-WR-TIMEZONE:{tz_name}",
        "X-WR-CALDESC:Daily Vedic Panchang festivals, Ekadashis, and auspicious Muhurtas"
    ]
    
    for idx, f in enumerate(festivals):
        f_name = f.get("name", "Vedic Event")
        f_date_str = f.get("date", "")
        f_desc = f.get("desc") or f.get("description", "Auspicious Vedic festival celebration")
        f_remedy = f.get("remedies", "")
        f_tithi = f.get("tithi", "")
        f_paksha = f.get("paksha", "")
        f_nakshatra = f.get("nakshatra", "")
        f_tag = f.get("tag", "festival").upper()
        
        if not f_date_str:
            continue
            
        event_date = None
        for fmt in ("%Y-%m-%d", "%d %b %Y", "%b %d, %Y", "%d-%m-%Y"):
            try:
                event_date = datetime.strptime(f_date_str, fmt).date()
                break
            except ValueError:
                pass
                
        if not event_date:
            continue
            
        dtstart_str = event_date.strftime("%Y%m%d")
        dtend_str = (event_date + timedelta(days=1)).strftime("%Y%m%d")
        
        uid = f"panchang-{f_tag.lower()}-{dtstart_str}-{idx}-{city.lower().replace(' ', '')}@astrologic.local"
        
        full_desc = f"{f_desc}"
        if f_tithi:
            full_desc += f"\\n\\nTithi: {f_tithi} ({f_paksha} Paksha)"
        if f_nakshatra:
            full_desc += f"\\nMoon in: {f_nakshatra}"
        if f_remedy:
            full_desc += f"\\nRituals/Remedies: {f_remedy}"
            
        clean_summary = f_name.replace(",", "\\,").replace(";", "\\;")
        clean_desc = full_desc.replace(",", "\\,").replace(";", "\\;")
        
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{dtstart_str}",
            f"DTEND;VALUE=DATE:{dtend_str}",
            f"SUMMARY:{clean_summary}",
            f"DESCRIPTION:{clean_desc}",
            f"CATEGORIES:VEDIC PANCHANG,HINDU FESTIVALS,{f_tag}",
            "STATUS:CONFIRMED",
            "TRANSP:TRANSPARENT",
            "END:VEVENT"
        ])
        
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
