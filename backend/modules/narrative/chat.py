"""Vedic Astrology Smart Chat Service answering user queries from Natal Chart data with i18n support."""

import re
from shared.veda.zodiac import SIGNS as SIGNS_SK, SIGN_LORDS
from shared.i18n.translation import get_translation, translate_astrology_term
from modules.narrative.llm_client import ask_llm
from modules.narrative.prompt_builder import build_chat_prompt

DASHA_YRS = dict(Ketu=7, Venus=20, Sun=6, Moon=10, Mars=7, Rahu=18, Jupiter=16, Saturn=19, Mercury=17)
DASHA_SEQ = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]


class ChatService:
    @staticmethod
    def answer_general_chat(message: str, chart: dict | None, lang: str = "en") -> str:
        """Answer chat questions utilizing chart context if available in user's requested language."""
        if not chart:
            return get_translation(
                "kundali.form.title",
                lang,
                default="Please generate your birth chart or Kundali first so I can analyze your planetary positions.",
            )

        prompt = build_chat_prompt(chart, message, lang=lang)
        return ask_llm(prompt)

    @staticmethod
    def answer_kundali_chat(message: str, chart: dict, lang: str = "en") -> dict:
        """Smart rules + context aware Kundali chat engine answering life domain questions."""
        if not chart:
            return {
                "reply": get_translation(
                    "common.error",
                    lang,
                    default="Please generate your Kundali first before asking questions.",
                ),
                "topic": "error",
            }

        msg = message.strip().lower()
        topic = ChatService._detect_topic(msg)

        planets_list = chart.get("planets", []) if isinstance(chart, dict) else []
        pm = {p["name"]: p for p in planets_list if "name" in p}
        lagna = chart.get("lagna", "Aries") if isinstance(chart, dict) else "Aries"
        md = chart.get("mahadasha", "Jupiter") if isinstance(chart, dict) else "Jupiter"
        ad = chart.get("antardasha", "Jupiter") if isinstance(chart, dict) else "Jupiter"
        bal = chart.get("dasha_balance", "5.0 years") if isinstance(chart, dict) else "5.0 years"
        yogas = [y.get("name", "") for y in chart.get("yogas", []) if y.get("present")] if isinstance(chart, dict) else []
        doshas = [d.get("name", "") for d in chart.get("doshas", []) if d.get("present")] if isinstance(chart, dict) else []

        if topic == "career":
            core = ChatService._answer_career(pm, lagna, md, ad, bal)
        elif topic == "marriage":
            core = ChatService._answer_marriage(pm, lagna, md, ad, bal)
        elif topic == "wealth":
            core = ChatService._answer_wealth(pm, lagna, md, ad, bal)
        elif topic == "health":
            core = ChatService._answer_health(pm, lagna)
        elif topic == "foreign":
            core = ChatService._answer_foreign(pm, lagna, md)
        elif topic == "timing":
            core = (
                f"**Current Dasha Period**: **{md}/{ad}** (Balance remaining: {bal}).\n\n"
                f"Planetary energies are primarily directed by {md}, activating associated house themes in your chart.\n\n"
                f"*(Note: Astrological timing reflects traditional Parāśari period frameworks and symbolic Gochara alignment, not fixed event guarantees or predictive probabilities.)*"
            )
        elif topic == "dosha":
            core = f"**Active Doshas Detected**: {', '.join(doshas) if doshas else 'No severe doshas detected.'}\n\n**Key Yogas**: {', '.join(yogas[:3]) if yogas else 'Standard planetary configurations.'}"
        elif topic == "remedy":
            core = ChatService._answer_remedy(pm, md)
        else:
            ai_reply = ask_llm(build_chat_prompt(chart, message, lang=lang))
            core = ai_reply if ai_reply else (
                f"**Chart Summary**: Lagna: **{translate_astrology_term(lagna, lang)}** | Mahadasha: **{md}/{ad}**.\n"
                f"Active Yogas: {', '.join(yogas[:3]) if yogas else 'None'}. "
                f"Please ask about career, marriage, wealth, health, or remedies for specific guidance."
            )

        return {
            "reply": core,
            "topic": topic,
            "chart_context": {
                "lagna": translate_astrology_term(lagna, lang),
                "mahadasha": md,
                "antardasha": ad,
                "dasha_balance": bal,
                "active_yogas": yogas[:4],
                "active_doshas": doshas[:3],
            },
        }

    @staticmethod
    def _detect_topic(msg: str) -> str:
        if any(w in msg for w in ["job", "career", "work", "business", "promotion", "profession"]):
            return "career"
        if any(w in msg for w in ["marr", "husband", "wife", "spouse", "partner", "love", "wedding"]):
            return "marriage"
        if any(w in msg for w in ["wealth", "money", "rich", "income", "finance", "earn"]):
            return "wealth"
        if any(w in msg for w in ["health", "sick", "disease", "illness", "body", "surgery"]):
            return "health"
        if any(w in msg for w in ["foreign", "abroad", "visa", "settle", "overseas", "travel"]):
            return "foreign"
        if any(w in msg for w in ["dasha", "timing", "period", "when", "year"]):
            return "timing"
        if any(w in msg for w in ["dosha", "mangal", "sade", "kaal sarp", "pitru"]):
            return "dosha"
        if any(w in msg for w in ["remedy", "gemstone", "mantra", "puja", "fast", "ring", "stone"]):
            return "remedy"
        return "general"

    @staticmethod
    def _house_of(pm: dict, name: str) -> int:
        p = pm.get(name, {})
        h = p.get("house", 1)
        if isinstance(h, int):
            return h
        try:
            return int(str(h).split("/")[0])
        except (ValueError, TypeError):
            return 1

    @staticmethod
    def _answer_career(pm: dict, lagna: str, md: str, ad: str, bal: str) -> str:
        lagna_idx = SIGNS_SK.index(lagna) if lagna in SIGNS_SK else 0
        lord_10 = SIGN_LORDS.get(SIGNS_SK[(lagna_idx + 9) % 12], "Mars")
        sign_10 = SIGNS_SK[(lagna_idx + 9) % 12]
        l10_h = ChatService._house_of(pm, lord_10)
        l10_str = pm.get(lord_10, {}).get("strength", "Neutral")

        return (
            f"**10th House (Career & Status)** is in **{sign_10}**, ruled by **{lord_10}**.\n"
            f"• **{lord_10}** is placed in house {l10_h} with **{l10_str}** dignity.\n"
            f"• Current operating Dasha: **{md}/{ad}**.\n"
            f"• Career growth accelerates when taking initiative in strategic domains aligned with {lord_10}'s qualities."
        )

    @staticmethod
    def _answer_marriage(pm: dict, lagna: str, md: str, ad: str, bal: str) -> str:
        lagna_idx = SIGNS_SK.index(lagna) if lagna in SIGNS_SK else 0
        lord_7 = SIGN_LORDS.get(SIGNS_SK[(lagna_idx + 6) % 12], "Venus")
        sign_7 = SIGNS_SK[(lagna_idx + 6) % 12]
        l7_h = ChatService._house_of(pm, lord_7)
        l7_str = pm.get(lord_7, {}).get("strength", "Neutral")
        venus = pm.get("Venus", {})
        mars_h = ChatService._house_of(pm, "Mars")
        mangal = mars_h in (1, 2, 4, 7, 8, 12)

        return (
            f"**7th House (Marriage & Partnership)** is in **{sign_7}**, ruled by **{lord_7}**.\n"
            f"• **{lord_7}** is situated in house {l7_h} ({l7_str}).\n"
            f"• **Venus (Kalatra Karaka)** is placed in {venus.get('sign', '')} in house {ChatService._house_of(pm, 'Venus')}.\n"
            f"• {'⚠️ **Mangal Dosha** present (Mars in house ' + str(mars_h) + ') — matched compatibility advised.' if mangal else '✅ No severe Mangal Dosha afflictions to the 7th house.'}\n"
            f"• Current Dasha: **{md}/{ad}** supports constructive relational alignment."
        )

    @staticmethod
    def _answer_wealth(pm: dict, lagna: str, md: str, ad: str, bal: str) -> str:
        lagna_idx = SIGNS_SK.index(lagna) if lagna in SIGNS_SK else 0
        lord_2 = SIGN_LORDS.get(SIGNS_SK[(lagna_idx + 1) % 12], "Venus")
        lord_11 = SIGN_LORDS.get(SIGNS_SK[(lagna_idx + 10) % 12], "Jupiter")
        jup_h = ChatService._house_of(pm, "Jupiter")
        jup_str = pm.get("Jupiter", {}).get("strength", "Neutral")

        return (
            f"**Financial Indicators (2nd & 11th Houses)**:\n"
            f"• 2nd Lord (Accumulated Wealth): **{lord_2}** in house {ChatService._house_of(pm, lord_2)}.\n"
            f"• 11th Lord (Gains & Income): **{lord_11}** in house {ChatService._house_of(pm, lord_11)}.\n"
            f"• **Jupiter (Dhana Karaka)** is placed in house {jup_h} ({jup_str}).\n"
            f"• Steady accumulation through disciplined value-oriented investments is favored."
        )

    @staticmethod
    def _answer_health(pm: dict, lagna: str) -> str:
        lagna_idx = SIGNS_SK.index(lagna) if lagna in SIGNS_SK else 0
        lord_1 = SIGN_LORDS.get(SIGNS_SK[lagna_idx], "Mars")
        l1_h = ChatService._house_of(pm, lord_1)
        l1_str = pm.get(lord_1, {}).get("strength", "Neutral")
        sun_str = pm.get("Sun", {}).get("strength", "Neutral")

        return (
            f"**Vitality & Health (1st & 6th Houses)**:\n"
            f"• Lagna Lord **{lord_1}** is in house {l1_h} ({l1_str}) governing physical stamina.\n"
            f"• Sun (Vitality indicator) is in house {ChatService._house_of(pm, 'Sun')} ({sun_str}).\n"
            f"• Maintain balanced Ayurvedic lifestyle and regular physical activity to optimize planetary energies.\n"
            f"*(Note: Astrological interpretations are non-diagnostic cultural reflections. Consult licensed medical providers for health advice.)*"
        )

    @staticmethod
    def _answer_foreign(pm: dict, lagna: str, md: str) -> str:
        rahu_h = ChatService._house_of(pm, "Rahu")
        foreign_strong = rahu_h in (1, 7, 9, 12)
        return (
            f"**Foreign Travel & Relocation (9th & 12th Houses)**:\n"
            f"• Rahu is placed in house {rahu_h} — {'Strong indicator for foreign opportunities and overseas travel.' if foreign_strong else 'Travel indicated for specific educational or professional assignments.'}\n"
            f"• Favorable periods activate during Rahu, 9th lord, or 12th lord sub-dashas."
        )

    @staticmethod
    def _answer_remedy(pm: dict, md: str) -> str:
        gems = {
            "Sun": "Ruby", "Moon": "Pearl", "Mars": "Red Coral", "Mercury": "Emerald",
            "Jupiter": "Yellow Sapphire", "Venus": "Diamond / White Topaz", "Saturn": "Blue Sapphire",
            "Rahu": "Hessonite", "Ketu": "Cat's Eye"
        }
        return (
            f"**Astrological Remedies & Strengthening**:\n"
            f"• Current Mahadasha Lord is **{md}**.\n"
            f"• Primary Gemstone recommendation for {md}: **{gems.get(md, 'Consult Astrologer')}** (wear after proper Energization).\n"
            f"• Daily Mantra: Recite the planetary mantra for {md} 108 times at sunrise for mental clarity and protection."
        )


chat_service = ChatService()
