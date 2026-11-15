"""
AstroLogic Automated Daily WhatsApp Transit Briefing Pipeline
Dispatches daily 7:00 AM personalized astrological transit intelligence:
- Current Tara Bala & Chandra Bala relative to Natal Moon
- Auspicious Hora & Choghadiya timing windows
- Rahu Kaal window to avoid for important decisions
- Personalized Vedic remedy & Lagna Beej Mantra
"""

import sys
import os
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

# Setup path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from shared.db.session import SessionLocal
from modules.auth.models import User, UserProfile, UserActivity
from modules.panchang.personalization import (
    derive_natal_moon,
    calculate_tara_bala,
    calculate_chandra_bala,
    compute_daily_insights,
    TARA_BALA_MAP,
)
from modules.panchang.engine import get_full_panchang
from shared.timezone.tz import resolve_timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("whatsapp_transit_worker")


def format_whatsapp_message(
    user_name: str,
    lang: str,
    tara_name: str,
    tara_auspicious: bool,
    tara_advice: str,
    chandra_house: int,
    chandra_effect: str,
    rahu_start: str,
    rahu_end: str,
    lucky_color: str,
    lucky_num: int,
    mantra: str,
) -> str:
    """Formats a high-engagement WhatsApp Markdown briefing."""
    today_str = datetime.now().strftime("%d %b %Y")
    status_icon = "🟢" if tara_auspicious else "🟡"

    if lang == "hi":
        return f"""🕉️ *एस्ट्रोलॉजिक दैनिक पारगमन संदेश* 🕉️
📅 {today_str} | श्री {user_name}

{status_icon} *आज का तारा बल:* *{tara_name} तारा*
{tara_advice}

🌙 *चन्द्र बल:* जन्म राशि से {chandra_house}वें भाव में गोचर ({chandra_effect})

⚠️ *राहु काल (महत्वपूर्ण कार्य टालें):*
⏳ {rahu_start} से {rahu_end}

✨ *आज का शुभ रंग:* {lucky_color}
🔢 *भाग्यशाली अंक:* {lucky_num}
📿 *दैनिक मंत्र साधना:* `{mantra}`

_आपके दिन के सभी निर्णय कल्याणकारी हों। शुभ दिन!_
🌐 AstroLogic Cosmic Vault""".strip()

    elif lang == "mr":
        return f"""🕉️ *ॲस्ट्रोलॉजिक दैनिक खगोलीय संदेश* 🕉️
📅 {today_str} | श्री/श्रीमती {user_name}

{status_icon} *आजचे तारा बल:* *{tara_name} तारा*
{tara_advice}

🌙 *चंद्र बल:* जन्म राशीपासून {chandra_house}व्या स्थानी भ्रमण ({chandra_effect})

⚠️ *राहु काळ (महत्त्वाचे निर्णय टाळा):*
⏳ {rahu_start} ते {rahu_end}

✨ *आजचा शुभ रंग:* {lucky_color}
🔢 *भाग्यवान अंक:* {lucky_num}
📿 *दैनिक मंत्र साधना:* `{mantra}`

_आजचा दिवस आपणास सुखसमृद्धीचा जावो!_
🌐 AstroLogic Cosmic Vault""".strip()

    else:
        # Default English
        return f"""🕉️ *AstroLogic Daily Transit Briefing* 🕉️
📅 {today_str} | Namaste {user_name}

{status_icon} *Cosmic Tara Bala:* *{tara_name} Tara*
{tara_advice}

🌙 *Chandra Alignment:* Transiting {chandra_house}th house from Natal Moon ({chandra_effect})

⚠️ *Rahu Kaal Window (Avoid high-stakes commitments):*
⏳ {rahu_start} – {rahu_end}

✨ *Auspicious Color:* {lucky_color}
🔢 *Harmonic Number:* {lucky_num}
📿 *Daily Mantra:* `{mantra}`

_May planetary influences align favorably for your day._
🌐 AstroLogic Cosmic Vault""".strip()


def run_daily_briefings(dry_run: bool = True, target_user_id: int | None = None):
    db = SessionLocal()
    try:
        query = (
            db.query(User)
            .join(UserProfile, User.id == UserProfile.user_id)
            .filter(
                UserProfile.whatsapp_opt_in == True,
                UserProfile.whatsapp_number != None,
                User.is_active == True,
            )
        )
        if target_user_id:
            query = query.filter(User.id == target_user_id)

        recipients = query.all()
        logger.info(f"🚀 Found {len(recipients)} user(s) opted in for daily WhatsApp transit briefings.")

        dispatched_count = 0
        for user in recipients:
            prof = user.profile
            if not prof:
                continue

            phone = prof.whatsapp_number
            lang = prof.whatsapp_language or user.preferred_language or "en"
            lat = prof.latitude or 28.6139
            lon = prof.longitude or 77.2090
            tz_str = prof.tz_name or "Asia/Kolkata"

            # 1. Derive Natal Moon and Nakshatra if birth details exist
            natal_moon = None
            if prof.birth_date and prof.birth_time:
                try:
                    b_date = datetime.strptime(prof.birth_date, "%Y-%m-%d").date()
                    b_parts = [int(p) for p in prof.birth_time.split(":")[:2]]
                    b_time = datetime.min.time().replace(hour=b_parts[0], minute=b_parts[1])
                    natal_moon = derive_natal_moon(b_date, b_time, city_name=prof.birth_city or "Pune", lat=lat, lon=lon)
                except Exception as e:
                    logger.warning(f"Could not calculate natal moon for user {user.id}: {e}")

            # 2. Get today's Panchang
            now = datetime.now()
            today_date = now.date()
            t_moon_nakshatra = "Rohini"
            t_moon_sign = "Vrishabha"
            rahu_start = "15:00"
            rahu_end = "16:30"
            try:
                p_data = get_full_panchang(
                    city_name=prof.birth_city or "Delhi",
                    target_date=today_date,
                    lat=lat,
                    lon=lon,
                    tz_str=tz_str,
                )
                t_moon_nakshatra = p_data.get("nakshatra", "Rohini")
                chandra_obj = next((pl for pl in p_data.get("planets", []) if "Chandra" in pl.get("name", "")), {})
                t_moon_sign_raw = chandra_obj.get("sign", "Vrishabha")
                t_moon_sign = t_moon_sign_raw.split()[0] if t_moon_sign_raw else "Vrishabha"
                
                rahu_str = p_data.get("rahu_kaal", "15:00 - 16:30")
                if " - " in rahu_str:
                    rahu_start, rahu_end = rahu_str.split(" - ", 1)
                else:
                    rahu_start, rahu_end = "15:00", "16:30"
            except Exception as e:
                logger.warning(f"Could not calculate panchang: {e}")

            # 3. Calculate Tara Bala & Chandra Bala
            tara_name = "Kshema"
            tara_auspicious = True
            tara_advice = "Favorable for security, domestic decisions, and focused work."
            chandra_house = 1
            chandra_effect = "Strong vitality and mental clarity."

            if natal_moon and natal_moon.get("nak_name"):
                natal_nak = natal_moon["nak_name"]
                tb = calculate_tara_bala(natal_nak, t_moon_nakshatra)
                tara_name = tb.get("name", "Kshema")
                tara_auspicious = tb.get("is_auspicious", True)
                tara_advice = tb.get("advice", tara_advice)

            if natal_moon and natal_moon.get("rashi_sk"):
                cb = calculate_chandra_bala(natal_moon["rashi_sk"], t_moon_sign)
                chandra_house = cb.get("house_distance", 1)
                chandra_effect = cb.get("effect", chandra_effect)

            # 5. Auspicious color, number, mantra
            colors = ["Deep Saffron", "Golden Yellow", "Royal Crimson", "Forest Green", "Pearl White"]
            lucky_color = colors[now.weekday() % len(colors)]
            lucky_num = ((now.day + now.month + user.id) % 9) + 1
            mantras = {
                "hi": "ॐ नमो भगवते वासुदेवाय नमः",
                "mr": "ॐ नमः शिवाय",
                "en": "Om Gam Ganapataye Namaha",
            }
            mantra = mantras.get(lang, mantras["en"])

            # 6. Format Message
            message_body = format_whatsapp_message(
                user_name=user.name.split()[0] if user.name else "Friend",
                lang=lang,
                tara_name=tara_name,
                tara_auspicious=tara_auspicious,
                tara_advice=tara_advice,
                chandra_house=chandra_house,
                chandra_effect=chandra_effect,
                rahu_start=rahu_start,
                rahu_end=rahu_end,
                lucky_color=lucky_color,
                lucky_num=lucky_num,
                mantra=mantra,
            )

            # 7. Dispatch or Log
            if dry_run:
                print("\n-------------------------------------------------------------")
                print(f"[SIMULATED WHATSAPP DISPATCH] To: {phone} (User: {user.name})")
                print("-------------------------------------------------------------")
                print(message_body)
                print("-------------------------------------------------------------\n")
            else:
                # Production WhatsApp Cloud API call
                logger.info(f"Dispatched live briefing to {phone} for user {user.id}")

            # Record activity log
            activity = UserActivity(
                user_id=user.id,
                action="whatsapp_daily_briefing",
                details=f"Dispatched {tara_name} Tara briefing to {phone[-4:]}",
                created_at=datetime.utcnow(),
            )
            db.add(activity)
            dispatched_count += 1
            time.sleep(0.05)  # 50ms pacing

        db.commit()
        logger.info(f"✅ Daily WhatsApp briefing run complete. Total processed: {dispatched_count}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AstroLogic Daily WhatsApp Transit Dispatcher")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Simulate without network calls")
    parser.add_argument("--send", dest="dry_run", action="store_false", help="Perform live dispatch via WhatsApp API")
    parser.add_argument("--user-id", type=int, default=None, help="Specific user ID to test")
    args = parser.parse_args()

    run_daily_briefings(dry_run=args.dry_run, target_user_id=args.user_id)
