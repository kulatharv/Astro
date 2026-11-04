"""Seed initial rich Vedic astrology blog posts into database."""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from shared.db.session import SessionLocal, init_db
from modules.blog.repository import BlogRepository
from modules.blog.schemas import BlogPostCreate

init_db()
db = SessionLocal()
repo = BlogRepository(db)

seeds = [
    {
        "title": "Understanding the 9 Planets (Navagrahas) in Vedic Astrology",
        "slug": "understanding-the-9-planets-in-vedic-astrology",
        "summary": "The nine celestial bodies govern every domain of human existence, shaping destiny, personality, and karmic lessons.",
        "content": """In classical Vedic Jyotish, the nine cosmic bodies — Surya (Sun), Chandra (Moon), Mangala (Mars), Budha (Mercury), Guru (Jupiter), Shukra (Venus), Shani (Saturn), Rahu (North Node), and Ketu (South Node) — are not merely distant balls of gas or rock; they are living archetypes of cosmic consciousness that channel specific karmic energies into our lives.

### Surya (The Sun) — Atmakaraka & Soul Force
The Sun represents the immortal soul (Atman), willpower, authority, father, and vital vitality. When strong in Aries or Leo, it gives nobility and leadership. When stressed, it indicates ego struggles or lack of confidence.

### Chandra (The Moon) — Manas & Emotional Consciousness
The Moon governs the mind, feelings, mother, intuition, and mental peace. Because the Moon moves fastest through the 27 Nakshatras, its placement at birth defines our core emotional baseline and initial Vimshottari Mahadasha balance.

### Mangala (Mars) — Courage & Proactive Energy
Mars symbolizes drive, passion, physical energy, brothers, and real estate. It provides the courage to overcome obstacles. A balanced Mars gives courageous initiative; an unguided Mars manifests as impulsiveness.

### Budha (Mercury) — Intellect & Discernment
Mercury governs speech, discrimination (Buddhi), commercial acumen, humor, and learning. As the prince of planets, it easily adapts to the qualities of whatever planets it associates with.

### Guru (Jupiter) — Wisdom & Divine Grace
Jupiter is the great benefic, bestowing dharma, wisdom, children, wealth, and spiritual growth. Its expansive transit and aspect bring benevolence wherever they fall.

### Shukra (Venus) — Harmony, Art & Devotion
Venus rules love, aesthetics, vehicles, luxuries, and refined creative expression. In its highest expression, Venus is divine devotion (Bhakti).

### Shani (Saturn) — Discipline & Karma
Saturn is the karmic taskmaster, teaching endurance, humility, truth, and longevity. Far from being purely difficult, Saturn builds enduring foundations and spiritual liberation.

### Rahu & Ketu — The Karmic Axis
Rahu represents our soul's obsessive worldly desires and uncharted ambitions, while Ketu signifies detachment, spiritual insight, and past-life mastery. Together, they guide the soul's evolutionary trajectory across incarnations.""",
        "language": "en",
        "tags": ["Planets", "Navagrahas", "Philosophy"],
        "author": "Acharya Shastri",
    },
    {
        "title": "What is Vimshottari Dasha and Why It Governs Life Timing",
        "slug": "vimshottari-dasha-complete-guide",
        "summary": "The 120-year Vimshottari cycle is the crown jewel of predictive Jyotish, explaining why events unfold precisely when they do.",
        "content": """Have you ever wondered why life moves in distinct chapters — periods of boundless expansion followed by periods of introspection, intense hard work, or unexpected romantic partnerships? The answer lies in the ancient Vimshottari Dasha system.

### The 120-Year Cosmic Blueprint
Vimshottari (literally meaning '120') assigns specific durations of time to the nine planetary rulers based on the moon's birth nakshatra degree:
- Sun: 6 Years
- Moon: 10 Years
- Mars: 7 Years
- Rahu: 18 Years
- Jupiter: 16 Years
- Saturn: 19 Years
- Mercury: 17 Years
- Ketu: 7 Years
- Venus: 20 Years

### How Dasha Transitions Feel
When shifting from a 19-year Saturn Mahadasha into a 16-year Mercury Mahadasha, the native often experiences a dramatic lightness: strict burdens and slow perseverance yield to learning, networking, commercial growth, and intellectual curiosity.

Similarly, entering a Jupiter period often brings spiritual mentorship, auspicious family milestones, and expansion of horizons.

### The Sub-Period Hierarchy
Timing precision is achieved through layered sub-periods:
1. **Mahadasha**: The overarching climate (years).
2. **Antardasha (Bhukti)**: The specific seasonal weather within that climate (months).
3. **Pratyantardasha**: Day-to-day energetic triggers.

Understanding your active Dasha empowers conscious alignment with cosmic timing rather than resisting natural tides.""",
        "language": "en",
        "tags": ["Dasha", "Timing", "Vedic Wisdom"],
        "author": "Dr. Ramananda",
    },
    {
        "title": "Raj Yoga: The Celestial Combinations for Power and Success",
        "slug": "raj-yoga-power-authority-success",
        "summary": "How kendra and trikona house lord unions elevate individuals to extraordinary leadership, respect, and influence.",
        "content": """In classical Jyotish, the term 'Raj Yoga' denotes planetary combinations that bestow power, royal stature, high administrative authority, and widespread respect.

### Kendra and Trikona: Vishnu and Lakshmi
The classical foundation rests on two auspicious pillars:
- **Kendra Houses (1, 4, 7, 10)**: Known as the pillars of Lord Vishnu, representing action, dynamic effort, and worldly manifestation.
- **Trikona Houses (1, 5, 9)**: Known as the realms of Goddess Lakshmi, representing divine grace, past-life merit (Purva Punya), and effortless fortune.

When the lord of a Kendra combines with the lord of a Trikona — either through conjunction, mutual aspect, or sign exchange (Parivartana) — a potent Raj Yoga is formed.

### The 5 MahaPurusha Yogas
Special Raj Yogas are formed when Mars, Mercury, Jupiter, Venus, or Saturn occupy a Kendra in their exaltation or own sign:
1. **Ruchaka Yoga (Mars)**: Fearless leadership, martial excellence, and physical stamina.
2. **Bhadra Yoga (Mercury)**: Brilliant oratory, encyclopedic intellect, and commercial mastery.
3. **Hamsa Yoga (Jupiter)**: Spiritual nobility, ethical jurisprudence, and profound wisdom.
4. **Malavya Yoga (Venus)**: Sensual refinement, artistic genius, and magnetic charisma.
5. **Sasa Yoga (Saturn)**: Enduring authority over organizations, masses, and long-range infrastructure.

Realizing the fruits of Raj Yoga requires favorable Dasha activation and uncontaminated planetary dignity.""",
        "language": "en",
        "tags": ["Yogas", "Kundali", "Success"],
        "author": "Pt. Devadatta",
    },
    {
        "title": "Saturn Sade Sati: Dispelling Myths & Embracing Karmic Growth",
        "slug": "saturn-sade-sati-guide",
        "summary": "Why the 7.5-year transit of Saturn over your natal Moon is an alchemical forge for character, resilience, and genuine accomplishment.",
        "content": """Few concepts in Indian astrology evoke as much unwarranted anxiety as 'Sade Sati' — the seven-and-a-half-year period during which Shani (Saturn) transits the sign preceding the natal Moon, the natal Moon sign itself, and the sign immediately following it.

### The Three Phases of Sade Sati
1. **Rising Phase (12th from Moon)**: Saturn tests psychological comfort, finances, expenditures, and subconscious attachments.
2. **Peak Phase (Over Natal Moon)**: The most transformative stretch. Direct pressure on the mind, emotions, identity, and personal responsibilities.
3. **Setting Phase (2nd from Moon)**: Focus turns toward family harmony, domestic values, and long-term financial realignment.

### Why Sade Sati is Not a Curse
Saturn is the divine auditor. It never takes away anything that is intrinsically pure and aligned with truth. It merely clears delusions, superficial relations, and fragile ambitions, leaving in their place unshakeable competence, integrity, and self-reliance.

Many of history's greatest achievements, promotions to peak responsibility, and profound spiritual awakenings occur precisely during Sade Sati.

### Recommended Vedic Remedies
- Regular chanting of the *Hanuman Chalisa* or *Shani Gayatri*.
- Charitable service to elderly, disabled, or labor-class individuals without pride.
- Eating simple, sattvic food and practicing punctuality and honesty in speech.""",
        "language": "en",
        "tags": ["Planets", "Remedies", "Shani"],
        "author": "Acharya Shastri",
    },
    {
        "title": "वैदिक ज्योतिष में नौ ग्रहों (नवग्रह) का प्रभाव और महत्व",
        "slug": "navagraha-parichay-vedic-jyotish",
        "summary": "नवग्रह मानव जीवन के प्रत्येक अंग को प्रभावित करते हैं — जानिए उनके शास्त्रीय गुणधर्म और जीवन पर पड़ने वाले प्रभाव।",
        "content": """वैदिक ज्योतिष में नवग्रह केवल खगोलीय पिंड नहीं, बल्कि ईश्वरीय चेतना के संवाहक हैं। सूर्य आत्मा, चंद्र मन, मंगल पराक्रम, बुध बुद्धि, गुरु ज्ञान, शुक्र सौंदर्य व ऐश्वर्य, शनि न्याय व कर्म, और राहु-केतु पूर्वजन्म के कर्मबंधनों का प्रतिनिधित्व करते हैं।

कुंडली में इन ग्रहों की शुभ स्थिति मनुष्य को जीवन में उन्नति, शांति और संतोष प्रदान करती है, जबकि प्रतिकूल स्थिति संयम और आत्म-मंथन का संदेश देती है। नियमित वैदिक आराधना और सदाचार से प्रत्येक ग्रह के शुभ फल प्राप्त किए जा सकते हैं।""",
        "language": "hi",
        "tags": ["ग्रह", "नवग्रह", "वैदिक ज्ञान"],
        "author": "पं. देवदत्त",
    },
    {
        "title": "शनि की साढ़ेसाती: भय नहीं, आत्म-विकास और शास्त्रीय उपाय",
        "slug": "sade-sati-vastavikta-aur-upay",
        "summary": "साढ़ेसाती से डरने की नहीं, बल्कि जीवन में अनुशासन और सत्यनिष्ठा लाने की आवश्यकता है।",
        "content": """शनिदेव को कर्मफलदाता कहा गया है। जब शनि जन्म चंद्र से १२वें, पहले और दूसरे भाव में गोचर करते हैं, तो साढ़े सात वर्ष की साढ़ेसाती होती है।

यह काल व्यक्ति को अहंकार से मुक्त कर वास्तविक सामर्थ्य प्रदान करता है। हनुमान चालीसा का पाठ, वृद्धजनों की सेवा और अहंकाररहित कर्म शनिदेव की कृपा पाने के अचूक मार्ग हैं।""",
        "language": "hi",
        "tags": ["शनि", "उपाय", "साढ़ेसाती"],
        "author": "आचार्य शास्त्री",
    },
    {
        "title": "वैदिक ज्योतिषशास्त्रातील नवग्रह आणि त्यांचे मानवी जीवनावरील प्रभाव",
        "slug": "vedic-jyotishatil-navagraha-mahatva",
        "summary": "सूर्य, चंद्र, मंगळ ते राहू-केतू या नवग्रहांची वैशिष्ट्ये आणि मानवी जीवनातील त्यांची भूमिका समजून घ्या.",
        "content": """भारतीय संस्कृतीत आणि वैदिक ज्योतिषशास्त्रात नवग्रहांना अत्यंत पूज्य स्थान आहे. सूर्य हा आत्म्याचा कारक, चंद्र मनाचा स्वामी, मंगळ शौर्याचे प्रतीक, बुध बुद्धीचा दाता, गुरु ज्ञानाचा सागर, शुक्र कला आणि प्रेमाचा प्रतिनिधी, तर शनी हा न्यायाचा कर्ता मानला गेला आहे.

राहू आणि केतू हे छायाग्रह असून आत्म्याच्या अध्यात्मिक प्रवासाची दिशा निश्चित करतात. या नवग्रहांच्या गती आणि युतीमुळे आपल्या जीवनातील विविध घटना घडत असतात.""",
        "language": "mr",
        "tags": ["ग्रह", "नवग्रह", "ज्योतिष"],
        "author": "पंडित देवदत्त",
    },
    {
        "title": "शनीची साडेसाती: भीती नव्हे, कर्मशुद्धी आणि प्रभावी वैदिक उपाय",
        "slug": "shani-sadesati-vastav-ani-upay",
        "summary": "साडेसाती हा कालावधी व्यक्तीला परिपक्व आणि स्वावलंबी बनवणारा ठरतो — शास्त्रीय दृष्टिकोन व उपाय.",
        "content": """शनीची साडेसाती म्हणजे चंद्र राशीच्या आधीच्या, त्याच आणि पुढच्या राशीतील साडेसात वर्षांचा प्रवास. हा काळ संकटाचा नसून आत्मपरीक्षणाचा आणि कर्माची शुद्धी करण्याचा असतो.

या काळात नम्रता, संयम, सचोटी आणि गरजूंना केलेली मदत शनीदेवांचा कृपाशीर्वाद मिळवून देते. हनुमान उपासना आणि शनी स्तोत्राचे पठण मन शांत ठेवण्यास अत्यंत लाभदायक ठरते.""",
        "language": "mr",
        "tags": ["शनी", "उपाय", "साडेसाती"],
        "author": "आचार्य शास्त्री",
    },
]

for s in seeds:
    existing = repo.get_by_slug(s["slug"])
    if not existing:
        dto = BlogPostCreate(**s)
        repo.create_post(dto)
        print(f"Created: {s['slug']} ({s['language']})")
    else:
        print(f"Already exists: {s['slug']}")

db.close()
print("Seeding completed successfully.")

