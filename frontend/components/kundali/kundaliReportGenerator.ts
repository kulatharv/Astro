/**
 * High-fidelity Printable Kundali Report Generator
 * Multi-language support (English, हिन्दी, मराठी)
 * Faithfully matches and modernizes the complete report template from app/templates/kundali.html
 */

import { HOUSE_NAMES_DATA, RASHI_NAMES_MAP, PLANET_NAMES_MAP } from './kundaliLocalization';

export type ReportLanguage = 'en' | 'hi' | 'mr';

export interface ReportInput {
  name: string;
  dob: string;
  tob: string;
  city: string;
  chartData: any;
  chartStyle?: 'north' | 'south';
  reportLanguage?: ReportLanguage;
}

const RASHI_FULL = [
  "Mesha", "Vrishabha", "Mithuna", "Karka",
  "Simha", "Kanya", "Tula", "Vrischika",
  "Dhanu", "Makara", "Kumbha", "Meena"
];

const STRENGTH_MAP: Record<string, { exalt: string; debil: string; own: string[] }> = {
  Sun: { exalt: "Mesha", debil: "Tula", own: ["Simha"] },
  Moon: { exalt: "Vrishabha", debil: "Vrischika", own: ["Karka"] },
  Mars: { exalt: "Makara", debil: "Karka", own: ["Mesha", "Vrischika"] },
  Mercury: { exalt: "Kanya", debil: "Meena", own: ["Mithuna", "Kanya"] },
  Jupiter: { exalt: "Karka", debil: "Makara", own: ["Dhanu", "Meena"] },
  Venus: { exalt: "Meena", debil: "Kanya", own: ["Vrishabha", "Tula"] },
  Saturn: { exalt: "Tula", debil: "Mesha", own: ["Makara", "Kumbha"] },
  Rahu: { exalt: "Mithuna", debil: "Dhanu", own: [] },
  Ketu: { exalt: "Dhanu", debil: "Mithuna", own: [] },
};

function getStrength(name: string, sign: string, lang: ReportLanguage = 'en') {
  const s = STRENGTH_MAP[name];
  if (!s) {
    return lang === 'en' ? "Neutral" : "सम";
  }
  if (s.exalt === sign) {
    return lang === 'en' ? "⬆ Exalted" : "⬆ उच्च";
  }
  if (s.debil === sign) {
    return lang === 'en' ? "⬇ Debilitated" : "⬇ नीच";
  }
  if (s.own.includes(sign)) {
    return lang === 'en' ? "★ Own Sign" : "★ स्वक्षेत्री";
  }
  return lang === 'en' ? "Neutral" : "सम";
}

function getRashiIndex(lagnaSign: string, h: number) {
  const i = RASHI_FULL.indexOf(lagnaSign);
  if (i === -1) return (h - 1) % 12;
  return (i + h - 1) % 12;
}

function getRashiDisplayName(sign: string, lang: ReportLanguage): string {
  const r = RASHI_NAMES_MAP[sign];
  if (!r) return sign || "—";
  if (lang === 'mr') return r.mr;
  if (lang === 'hi') return r.hi;
  return `${sign} (${r.en})`;
}

function getPlanetDisplayName(name: string, lang: ReportLanguage): string {
  const p = PLANET_NAMES_MAP[name];
  if (!p) return name || "—";
  if (lang === 'mr') return p.mr;
  if (lang === 'hi') return p.hi;
  return p.en;
}

const DEVA_PLANET_SHORT: Record<string, string> = {
  Sun: "सू",
  Moon: "चं",
  Mars: "मं",
  Mercury: "बु",
  Jupiter: "गु",
  Venus: "शु",
  Saturn: "श",
  Rahu: "रा",
  Ketu: "के",
  Lagna: "लग्न",
};

// Generate North Indian SVG string for the report with language sensitivity
function generateNorthIndianSvg(
  housesData: Record<string | number, string[]>,
  lagnaSign: string,
  lang: ReportLanguage = 'en'
): string {
  const lagnaRashiNum = RASHI_NAMES_MAP[lagnaSign]?.num || 1;
  const POSITION_MAP: Record<number, number> = { 1: 1, 2: 12, 3: 11, 4: 2, 5: 10, 6: 3, 7: 9, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8 };
  const HOUSE_COORDS: Record<number, { nx: number; ny: number; px: number; py: number }> = {
    1: { nx: 300, ny: 155, px: 300, py: 105 },
    2: { nx: 200, ny: 55,  px: 235, py: 75 },
    3: { nx: 70,  ny: 95,  px: 75,  py: 115 },
    4: { nx: 400, ny: 55,  px: 365, py: 75 },
    5: { nx: 530, ny: 95,  px: 525, py: 115 },
    6: { nx: 70,  ny: 320, px: 75,  py: 295 },
    7: { nx: 200, ny: 360, px: 235, py: 335 },
    8: { nx: 155, ny: 215, px: 220, py: 210 },
    9: { nx: 445, ny: 215, px: 380, py: 210 },
    10: { nx: 530, ny: 320, px: 525, py: 295 },
    11: { nx: 400, ny: 360, px: 365, py: 335 },
    12: { nx: 300, ny: 260, px: 300, py: 310 },
  };

  const lagnaLabel = lang === 'en' ? 'LAGNA' : 'लग्न';

  let svg = `<svg viewBox="0 0 600 420" style="width:100%;max-width:440px;display:block;margin:0 auto;background:#fff;border:1px solid #d4a017;border-radius:6px">`;
  svg += `<rect x="8" y="8" width="584" height="404" fill="#faf7f2" stroke="#8b1a1a" stroke-width="2"/>`;
  svg += `<line x1="8" y1="8" x2="592" y2="412" stroke="#d4a017" stroke-width="1.2"/>`;
  svg += `<line x1="592" y1="8" x2="8" y2="412" stroke="#d4a017" stroke-width="1.2"/>`;
  svg += `<polygon points="300,8 592,210 300,412 8,210" fill="none" stroke="#8b1a1a" stroke-width="1.5"/>`;

  for (let pos = 1; pos <= 12; pos++) {
    const houseNum = POSITION_MAP[pos];
    const coords = HOUSE_COORDS[pos];
    const rashiNum = ((lagnaRashiNum + houseNum - 2) % 12) + 1;
    const isLagna = houseNum === 1;

    svg += `<text x="${coords.nx}" y="${coords.ny}" text-anchor="middle" font-size="11" font-weight="bold" fill="${isLagna ? '#8b1a1a' : '#888'}" font-family="monospace">${rashiNum}</text>`;

    if (isLagna) {
      svg += `<text x="${coords.px}" y="${coords.py - 18}" text-anchor="middle" font-size="11" font-weight="bold" fill="#8b1a1a" font-family="'Noto Serif Devanagari', 'Segoe UI', sans-serif">${lagnaLabel}</text>`;
    }

    const rawPlanets = housesData[houseNum] || [];
    const planetsInHouse = rawPlanets.filter((p) => p !== "Lagna");
    if (planetsInHouse.length > 0) {
      const lh = 15;
      const totalH = (planetsInHouse.length - 1) * lh;
      const startY = coords.py - totalH / 2 + (isLagna ? 8 : 0);
      planetsInHouse.forEach((p, idx) => {
        const pInfo = PLANET_NAMES_MAP[p];
        const label = lang === 'en' ? (pInfo?.short || p.slice(0, 2)) : (DEVA_PLANET_SHORT[p] || pInfo?.short || p.slice(0, 2));
        const isSp = ["Sun", "Moon", "Jupiter"].includes(p);
        svg += `<text x="${coords.px}" y="${startY + idx * lh}" text-anchor="middle" font-size="11.5" font-weight="bold" fill="${isSp ? '#8b1a1a' : '#421a10'}" font-family="'Noto Serif Devanagari', sans-serif">${label}</text>`;
      });
    }
  }

  svg += `</svg>`;
  return svg;
}

// Multilingual report dictionaries
const REPORT_TEXTS: Record<ReportLanguage, {
  siteTitle: string;
  reportSubtitle: string;
  metaDetails: string;
  printBtn: string;
  secBirth: string;
  nativeName: string;
  dob: string;
  tob: string;
  pob: string;
  lagna: string;
  lagnaNakshatra: string;
  moonSign: string;
  birthNakshatra: string;
  tithi: string;
  yoga: string;
  karana: string;
  ayanamsa: string;
  activeDasha: string;
  dashaBalance: string;
  pada: string;
  secD1: string;
  secD9: string;
  secStrength: string;
  scores: Record<string, string>;
  secNavagraha: string;
  thPlanet: string;
  thSign: string;
  thDegree: string;
  thHouse: string;
  thNakshatra: string;
  thPada: string;
  thNavamsa: string;
  thDignity: string;
  thMotion: string;
  secHouses: string;
  thHouseNum: string;
  thHouseSign: string;
  thHouseSignifications: string;
  thHouseOccupants: string;
  secYogas: string;
  secDoshas: string;
  noYogas: string;
  neutralDoshasTitle: string;
  neutralDoshasDesc: string;
  secDasha: string;
  activeMahadasha: string;
  activeAntardasha: string;
  balanceRemaining: string;
  antardashaSeq: string;
  years: string;
  direct: string;
  retrograde: string;
  footer: (name: string) => string;
}> = {
  en: {
    siteTitle: "✦ AstroLogic AI ✦",
    reportSubtitle: "Vedic Birth Kundali — Authoritative Natal Report",
    metaDetails: "Lahiri Ayanamsa · Swiss Ephemeris Accuracy · Vimshottari Dasha",
    printBtn: "🖨️ Print / Save as PDF",
    secBirth: "Birth Details & Panchang",
    nativeName: "Native Name:",
    dob: "Date of Birth:",
    tob: "Time of Birth:",
    pob: "Place of Birth:",
    lagna: "Lagna (Ascendant):",
    lagnaNakshatra: "Lagna Nakshatra:",
    moonSign: "Moon Sign (Chandra Rashi):",
    birthNakshatra: "Birth Nakshatra:",
    tithi: "Janma Tithi:",
    yoga: "Birth Yoga:",
    karana: "Karana:",
    ayanamsa: "Ayanamsa:",
    activeDasha: "Active Mahadasha:",
    dashaBalance: "Dasha Balance:",
    pada: "Pada",
    secD1: "D1 — Rashi Chart (Natal)",
    secD9: "D9 — Navamsha Chart (Spouse & Dharma)",
    secStrength: "Chart Strength Analysis",
    scores: {
      overall: "Overall Strength",
      career: "Career & Karma",
      finance: "Finance & Wealth",
      marriage: "Marriage & Partnership",
      health: "Physical Longevity",
      mental: "Mental Peace",
      spiritual: "Spirituality & Dharma",
    },
    secNavagraha: "Planetary Positions & Dignities (Navagraha)",
    thPlanet: "Planet",
    thSign: "Sign",
    thDegree: "Degree",
    thHouse: "House",
    thNakshatra: "Nakshatra",
    thPada: "Pada",
    thNavamsa: "Navamsa",
    thDignity: "Dignity",
    thMotion: "Motion",
    secHouses: "House-wise Analysis (All 12 Bhavas)",
    thHouseNum: "House",
    thHouseSign: "Sign",
    thHouseSignifications: "Significations & Attributes",
    thHouseOccupants: "Occupants",
    secYogas: "Active Vedic Yogas",
    secDoshas: "Dosha Analysis & Vedic Guidance",
    noYogas: "No major classical yogas detected in primary placements.",
    neutralDoshasTitle: "✓ Neutral / Mitigated",
    neutralDoshasDesc: "Chart is free from severe unmitigated doshas.",
    secDasha: "Vimshottari Dasha Chronology",
    activeMahadasha: "Active Mahadasha:",
    activeAntardasha: "Active Antardasha:",
    balanceRemaining: "Balance Remaining:",
    antardashaSeq: "Antardasha Sequence:",
    years: "y",
    direct: "Direct",
    retrograde: "Retrograde",
    footer: (name: string) => `AstroLogic Vedic Platform · Detailed Kundali for <strong>${name}</strong> · Calculations via Lahiri Ayanamsa & Swiss Ephemeris · For personal guidance & contemplation`,
  },
  hi: {
    siteTitle: "✦ एस्ट्रोलॉजिक ✦",
    reportSubtitle: "वैदिक जन्म पत्रिका — प्रामाणिक जन्म कुंडली अहवाल",
    metaDetails: "लाहिड़ी अयनांश · स्विस एफेमेरिस सूक्ष्म गणना · विंशोत्तरी महादशा",
    printBtn: "🖨️ प्रिंट करें / PDF सुरक्षित करें",
    secBirth: "जन्म विवरण एवं पंचांग",
    nativeName: "जातक का नाम:",
    dob: "जन्म तिथि:",
    tob: "जन्म समय:",
    pob: "जन्म स्थान:",
    lagna: "लग्न (प्रथम भाव):",
    lagnaNakshatra: "लग्न नक्षत्र:",
    moonSign: "चंद्र राशि:",
    birthNakshatra: "जन्म नक्षत्र:",
    tithi: "जन्म तिथि:",
    yoga: "जन्म योग:",
    karana: "करण:",
    ayanamsa: "अयनांश:",
    activeDasha: "सक्रिय महादशा:",
    dashaBalance: "दशा शेष:",
    pada: "चरण",
    secD1: "डी-१ — लग्न कुंडली (जन्म राशि चक्र)",
    secD9: "डी-९ — नवमांश कुंडली (भाग्य एवं जीवनसाथी)",
    secStrength: "कुंडली सामर्थ्य विश्लेषण (षड्बल व भावाबलोकन)",
    scores: {
      overall: "समग्र सामर्थ्य",
      career: "कर्म व आजीविका",
      finance: "धन व ऐश्वर्य",
      marriage: "दांपत्य व सहजीवन",
      health: "आरोग्य व दीर्घायु",
      mental: "मानसिक शांति",
      spiritual: "धर्म व अध्यात्म",
    },
    secNavagraha: "नवग्रह स्थिति एवं गरिमा (ग्रह स्पष्ट)",
    thPlanet: "ग्रह",
    thSign: "राशि",
    thDegree: "अंश",
    thHouse: "भाव",
    thNakshatra: "नक्षत्र",
    thPada: "चरण",
    thNavamsa: "नवमांश",
    thDignity: "स्थिति/बल",
    thMotion: "गति",
    secHouses: "द्वादश भाव विश्लेषण (सम्पूर्ण १२ भाव)",
    thHouseNum: "भाव",
    thHouseSign: "राशि",
    thHouseSignifications: "कारकत्व एवं फलित विवरण",
    thHouseOccupants: "स्थित ग्रह",
    secYogas: "सक्रिय वैदिक शुभ योग",
    secDoshas: "दोष विश्लेषण एवं वैदिक उपाय",
    noYogas: "प्राथमिक ग्रह स्थितियों में कोई प्रमुख शास्त्रीय योग परिलक्षित नहीं हुआ।",
    neutralDoshasTitle: "✓ निर्दोष / शांत",
    neutralDoshasDesc: "कुंडली गंभीर अनिष्ट दोषों से मुक्त है।",
    secDasha: "विंशोत्तरी महादशा कालक्रम",
    activeMahadasha: "सक्रिय महादशा:",
    activeAntardasha: "सक्रिय अंतर्दशा:",
    balanceRemaining: "शेष अवधि:",
    antardashaSeq: "अंतर्दशा क्रम:",
    years: " वर्ष",
    direct: "मार्गी",
    retrograde: "वक्री",
    footer: (name: string) => `एस्ट्रोलॉजिक वैदिक मंच · जातक <strong>${name}</strong> हेतु विस्तृत जन्म पत्रिका · लाहिड़ी अयनांश एवं स्विस एफेमेरिस द्वारा गणना · व्यक्तिगत मार्गदर्शन एवं चिंतन हेतु`,
  },
  mr: {
    siteTitle: "✦ ॲस्ट्रोलॉजिक ✦",
    reportSubtitle: "वैदिक जन्म पत्रिका — सखोल जन्म कुंडली अहवाल",
    metaDetails: "लहिरी अयनांश · स्विस एफिमेरिस अचूक गणना · विंशोत्तरी महादशा",
    printBtn: "🖨️ प्रिंट करा / PDF सेव्ह करा",
    secBirth: "जन्म तपशील आणि पंचांग",
    nativeName: "जातकाचे नाव:",
    dob: "जन्म तारीख:",
    tob: "जन्म वेळ:",
    pob: "जन्म ठिकाण:",
    lagna: "लग्न (प्रथम स्थान):",
    lagnaNakshatra: "लग्न नक्षत्र:",
    moonSign: "चंद्र राशी:",
    birthNakshatra: "जन्म नक्षत्र:",
    tithi: "जन्म तिथी:",
    yoga: "जन्म योग:",
    karana: "करण:",
    ayanamsa: "अयनांश:",
    activeDasha: "चालू महादशा:",
    dashaBalance: "दशा शिल्लक:",
    pada: "चरण",
    secD1: "डी-१ — लग्न कुंडली (जन्म राशी चक्र)",
    secD9: "डी-९ — नवमांश कुंडली (भाग्य व जोडीदार)",
    secStrength: "कुंडली सामर्थ्य विश्लेषण (षड्बल व भावालोकन)",
    scores: {
      overall: "एकूण सामर्थ्य",
      career: "कारकीर्द व कर्म",
      finance: "वित्त आणि संपत्ती",
      marriage: "विवाह व सहजीवन",
      health: "आरोग्य व दीर्घायुष्य",
      mental: "मानसिक शांती",
      spiritual: "धर्म व अध्यात्म",
    },
    secNavagraha: "नवग्रह स्थिती आणि बल (ग्रह स्पष्ट)",
    thPlanet: "ग्रह",
    thSign: "राशी",
    thDegree: "अंश",
    thHouse: "स्थान/भाव",
    thNakshatra: "नक्षत्र",
    thPada: "चरण",
    thNavamsa: "नवमांश",
    thDignity: "बल/प्रतिष्ठा",
    thMotion: "गती",
    secHouses: "द्वादश भाव विश्लेषण (सर्व १२ भाव)",
    thHouseNum: "स्थान",
    thHouseSign: "राशी",
    thHouseSignifications: "कारकत्व आणि वैशिष्ट्ये",
    thHouseOccupants: "उपस्थित ग्रह",
    secYogas: "सक्रिय वैदिक शुभ योग",
    secDoshas: "दोष विश्लेषण आणि वैदिक उपाय",
    noYogas: "प्राथमिक ग्रहस्थितीमध्ये कोणतेही मोठे शास्त्रीय योग आढळले नाहीत.",
    neutralDoshasTitle: "✓ निर्दोष / सौम्य",
    neutralDoshasDesc: "पत्रिका गंभीर अनिष्ट दोषांपासून मुक्त आहे.",
    secDasha: "विंशोत्तरी महादशा कालक्रम",
    activeMahadasha: "चालू महादशा:",
    activeAntardasha: "चालू अंतर्दशा:",
    balanceRemaining: "शिल्लक कालावधी:",
    antardashaSeq: "अंतर्दशा क्रम:",
    years: " वर्षे",
    direct: "मार्गी",
    retrograde: "वक्री",
    footer: (name: string) => `ॲस्ट्रोलॉजिक वैदिक मंच · जातक <strong>${name}</strong> साठी सखोल जन्म कुंडली · लहिरी अयनांश व स्विस एफिमेरिस द्वारे अचूक गणना · वैयक्तिक मार्गदर्शन व चिंतनार्थ`,
  },
};

export function openPrintableKundaliReport({
  name,
  dob,
  tob,
  city,
  chartData,
  reportLanguage = 'en',
}: ReportInput) {
  if (!chartData) return;

  const lang: ReportLanguage = ['en', 'hi', 'mr'].includes(reportLanguage) ? reportLanguage : 'en';
  const txt = REPORT_TEXTS[lang];
  const d = chartData;
  const pName = name.trim() || (lang === 'en' ? "Native" : "जातक");
  const moon = (d.planets || []).find((pl: any) => pl.name === "Moon");

  const d1SVG = generateNorthIndianSvg(d.houses || {}, d.lagna || "Mesha", lang);
  const d9SVG = generateNorthIndianSvg(d.d9_houses || {}, d.d9_lagna || d.lagna || "Mesha", lang);

  // Date locale
  const dateLocales: Record<ReportLanguage, string> = { en: 'en-IN', hi: 'hi-IN', mr: 'mr-IN' };
  const formattedDate = new Date().toLocaleDateString(dateLocales[lang], { dateStyle: "long" });

  // Navagraha table rows
  const planetRows = (d.planets || []).map((pl: any) => {
    const strength = getStrength(pl.name, pl.sign, lang);
    const strengthColor = strength.includes("Exalted") || strength.includes("उच्च")
      ? "#15803d"
      : strength.includes("Debilitated") || strength.includes("नीच")
      ? "#b91c1c"
      : strength.includes("Own") || strength.includes("स्वक्षेत्री")
      ? "#b45309"
      : "#666666";

    const retroBadge = pl.retrograde
      ? ` <span style="color:#b91c1c;font-weight:bold;font-size:10px">(${txt.retrograde.slice(0, 1)} ℞)</span>`
      : "";

    const planetNameDisplay = getPlanetDisplayName(pl.name, lang);
    const signDisplay = getRashiDisplayName(pl.sign, lang);
    const navamsaSignDisplay = getRashiDisplayName(pl.navamsa, lang);
    const motionDisplay = pl.retrograde ? txt.retrograde : txt.direct;

    return `<tr>
      <td><strong>${planetNameDisplay}</strong>${retroBadge}</td>
      <td>${signDisplay}</td>
      <td style="font-family:monospace;font-size:11px">${pl.degree || "—"}</td>
      <td style="text-align:center;font-weight:bold">${pl.house || "—"}</td>
      <td>${pl.nakshatra || "—"}</td>
      <td style="text-align:center">${pl.pada || "—"}</td>
      <td>${navamsaSignDisplay}</td>
      <td style="color:${strengthColor};font-weight:600">${strength}</td>
      <td>${motionDisplay}</td>
    </tr>`;
  }).join("");

  // 12 Houses Analysis rows
  const allHouseRows = Array.from({ length: 12 }, (_, i) => {
    const h = i + 1;
    const rashiIdx = getRashiIndex(d.lagna, h);
    const sign = RASHI_FULL[rashiIdx] || "";
    const signDisplay = getRashiDisplayName(sign, lang);
    const hInfo = HOUSE_NAMES_DATA[h];
    const occupants = (d.houses?.[h] || []).filter((x: string) => x !== "Lagna");
    const occupantsDisplay = occupants.length
      ? occupants.map((x: string) => getPlanetDisplayName(x, lang)).join(", ")
      : '<span style="color:#aaa">—</span>';

    const desc = lang === 'mr' ? hInfo?.mrDesc : lang === 'hi' ? hInfo?.hiDesc : hInfo?.enDesc;
    const sName = hInfo?.sanskritName || "";

    return `<tr>
      <td style="text-align:center;font-weight:bold;color:#8b1a1a">${lang === 'en' ? `H${h}` : `${h}`}</td>
      <td style="font-weight:600">${signDisplay}</td>
      <td style="font-size:11px;color:#421a10"><strong>${sName}</strong> — ${desc || ""}</td>
      <td><strong>${occupantsDisplay}</strong></td>
    </tr>`;
  }).join("");

  // Scores bars
  const sc = d.scores || {};
  const scoreCategories = [
    [txt.scores.overall, sc.overall_strength, "#8b1a1a"],
    [txt.scores.career, sc.career_score, "#c46b1e"],
    [txt.scores.finance, sc.finance_score, "#15803d"],
    [txt.scores.marriage, sc.marriage_score, "#0284c7"],
    [txt.scores.health, sc.health_score, "#dc2626"],
    [txt.scores.mental, sc.mental_score, "#9333ea"],
    [txt.scores.spiritual, sc.spirituality_score, "#d97706"],
  ];

  const scoreHTML = scoreCategories.map(([lbl, val, color]) => `
    <div style="margin-bottom:8px">
      <div style="display:flex;justify-content:space-between;margin-bottom:2px;font-size:11.5px">
        <span style="color:#421a10;font-weight:500">${lbl}</span>
        <span style="font-weight:bold;color:${color}">${val ?? 60}%</span>
      </div>
      <div style="background:#fcebd2;border-radius:3px;height:6px;overflow:hidden">
        <div style="background:${color};height:6px;border-radius:3px;width:${Math.min(Number(val) || 0, 100)}%"></div>
      </div>
    </div>
  `).join("");

  const activeYogas = (d.yogas || []).filter((y: any) => y.present);
  const activeDoshas = (d.doshas || []).filter((ds: any) => ds.present);

  // Antardasha pills
  const antarList = (d.antardasha_list || []).map((a: any, i: number) => {
    const lordName = getPlanetDisplayName(a.lord, lang);
    return `<span style="display:inline-block;margin:2px 3px;padding:2px 8px;background:${i === 0 ? '#8b1a1a' : '#fcebd2'};color:${i === 0 ? '#fff' : '#421a10'};border-radius:4px;font-size:10.5px;font-weight:600">${lordName} (${a.years}${txt.years})</span>`;
  }).join("");

  // Panchang Values
  const lagnaDisplay = getRashiDisplayName(d.lagna || "Mesha", lang);
  const moonSignDisplay = moon ? getRashiDisplayName(moon.sign, lang) : "—";
  const mahadashaLord = getPlanetDisplayName(d.mahadasha || "", lang);
  const antardashaLord = getPlanetDisplayName(d.antardasha || "", lang);

  const win = window.open("", "_blank", "width=1050,height=850");
  if (!win) {
    alert("Please allow popups for this site to open the printable report.");
    return;
  }

  win.document.write(`<!DOCTYPE html>
<html lang="${lang}" translate="no" class="notranslate">
<head>
  <meta charset="utf-8">
  <meta name="google" content="notranslate" />
  <meta name="robots" content="notranslate" />
  <meta name="format-detection" content="telephone=no" />
  <title>${txt.siteTitle} — ${pName}</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Devanagari", "Noto Serif Devanagari", "Mangal", "Nirmala UI", Georgia, serif;
      background: #fff;
      color: #1a0a00;
      font-size: 12.5px;
      line-height: 1.45;
    }
    .page {
      max-width: 980px;
      margin: 0 auto;
      padding: 24px 30px;
    }
    .header {
      text-align: center;
      padding: 16px 0 14px;
      border-bottom: 3px double #8b1a1a;
      margin-bottom: 20px;
    }
    .header h1 {
      font-size: 28px;
      color: #8b1a1a;
      letter-spacing: 3px;
      font-weight: 700;
      margin-bottom: 4px;
    }
    .header h2 {
      font-size: 14px;
      color: #555;
      font-weight: 500;
    }
    .header .meta {
      font-size: 11px;
      color: #777;
      margin-top: 5px;
    }
    .sec {
      margin-bottom: 20px;
    }
    .sec-title {
      font-size: 11px;
      background: #8b1a1a;
      color: #fff;
      padding: 4px 10px;
      border-radius: 4px;
      margin-bottom: 10px;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      font-weight: 700;
    }
    .grid2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
      margin-bottom: 20px;
    }
    .dr {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      font-size: 12px;
      border-bottom: 1px dotted #edd6b8;
      padding-bottom: 2px;
    }
    .dl {
      color: #666;
      font-weight: 500;
    }
    .dv {
      color: #1a0a00;
      font-weight: 700;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11.5px;
      margin-top: 4px;
    }
    th {
      background: #fcebd2;
      color: #8b1a1a;
      padding: 6px 8px;
      text-align: left;
      font-weight: 700;
      font-size: 11px;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #e49d4b;
    }
    td {
      padding: 5px 8px;
      border-bottom: 1px solid #f2e6d6;
      vertical-align: middle;
    }
    tr:nth-child(even) td {
      background: #faf7f2;
    }
    .yoga-item {
      padding: 6px 10px;
      margin-bottom: 6px;
      border-left: 3px solid #15803d;
      background: #f0fdf4;
      border-radius: 4px;
    }
    .yoga-item h4 {
      font-size: 12px;
      color: #15803d;
      margin-bottom: 2px;
      font-weight: 700;
    }
    .yoga-item p {
      font-size: 11px;
      color: #444;
      margin: 0;
    }
    .dosha-item {
      padding: 6px 10px;
      margin-bottom: 6px;
      border-radius: 4px;
    }
    .dosha-high {
      border-left: 3px solid #dc2626;
      background: #fef2f2;
    }
    .dosha-med {
      border-left: 3px solid #c46b1e;
      background: #fffbeb;
    }
    .dosha-item h4 {
      font-size: 12px;
      margin-bottom: 2px;
      font-weight: 700;
    }
    .dosha-item p {
      font-size: 11px;
      color: #444;
      margin-bottom: 3px;
    }
    .dosha-item ul {
      margin: 0;
      padding-left: 16px;
    }
    .dosha-item li {
      font-size: 10.5px;
      color: #555;
    }
    .chart-box {
      text-align: center;
    }
    .footer {
      text-align: center;
      font-size: 10.5px;
      color: #777;
      border-top: 1px solid #edd6b8;
      padding-top: 10px;
      margin-top: 24px;
    }
    @media print {
      @page { margin: 1cm; size: A4 portrait; }
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .no-print { display: none !important; }
    }
  </style>
</head>
<body translate="no" class="notranslate">
  <div class="page">
    <!-- Action Bar -->
    <div class="no-print" style="margin-bottom:16px;display:flex;justify-content:space-between;align-items:center">
      <div style="font-size:12px;font-weight:bold;color:#8b1a1a">
        🌐 ${lang === 'mr' ? 'मराठी अहवाल' : lang === 'hi' ? 'हिन्दी रिपोर्ट' : 'English Report'}
      </div>
      <button onclick="window.print()" style="background:#8b1a1a;color:#fff;border:none;padding:8px 18px;border-radius:5px;font-size:12px;font-weight:bold;cursor:pointer">
        ${txt.printBtn}
      </button>
    </div>

    <!-- Header -->
    <div class="header">
      <h1>${txt.siteTitle}</h1>
      <h2>${txt.reportSubtitle}</h2>
      <div class="meta">
        ${formattedDate} &nbsp;·&nbsp; ${txt.metaDetails}
      </div>
    </div>

    <!-- Grid: Birth Details & D1 Chart -->
    <div class="grid2">
      <div class="sec">
        <div class="sec-title">${txt.secBirth}</div>
        <div class="dr"><span class="dl">${txt.nativeName}</span><span class="dv">${pName}</span></div>
        <div class="dr"><span class="dl">${txt.dob}</span><span class="dv">${dob}</span></div>
        <div class="dr"><span class="dl">${txt.tob}</span><span class="dv">${tob} IST</span></div>
        <div class="dr"><span class="dl">${txt.pob}</span><span class="dv">${city}</span></div>
        <div class="dr"><span class="dl">${txt.lagna}</span><span class="dv" style="color:#8b1a1a">${lagnaDisplay} (${d.lagna_degree || ""})</span></div>
        <div class="dr"><span class="dl">${txt.lagnaNakshatra}</span><span class="dv">${d.lagna_nakshatra || "—"} (${txt.pada} ${d.lagna_pada || 1})</span></div>
        <div class="dr"><span class="dl">${txt.moonSign}</span><span class="dv">${moonSignDisplay}</span></div>
        <div class="dr"><span class="dl">${txt.birthNakshatra}</span><span class="dv">${d.nakshatra || "—"} (${txt.pada} ${d.nakshatra_pada || 1})</span></div>
        <div class="dr"><span class="dl">${txt.tithi}</span><span class="dv">${d.paksha || ""} ${d.tithi_name || "—"}</span></div>
        <div class="dr"><span class="dl">${txt.yoga}</span><span class="dv">${d.yoga_name || "—"}</span></div>
        <div class="dr"><span class="dl">${txt.karana}</span><span class="dv">${d.karana_name || "—"}</span></div>
        <div class="dr"><span class="dl">${txt.ayanamsa}</span><span class="dv">${d.ayanamsa || "23.8"}° (Lahiri)</span></div>
        <div class="dr"><span class="dl">${txt.activeDasha}</span><span class="dv" style="color:#8b1a1a">${mahadashaLord}</span></div>
        <div class="dr"><span class="dl">${txt.dashaBalance}</span><span class="dv">${d.dasha_balance || "—"}</span></div>
      </div>
      <div class="sec chart-box">
        <div class="sec-title">${txt.secD1}</div>
        ${d1SVG}
      </div>
    </div>

    <!-- Grid: D9 Chart & Strength -->
    <div class="grid2">
      <div class="sec chart-box">
        <div class="sec-title">${txt.secD9}</div>
        ${d9SVG}
      </div>
      <div class="sec">
        <div class="sec-title">${txt.secStrength}</div>
        ${scoreHTML}
      </div>
    </div>

    <!-- Navagraha Table -->
    <div class="sec">
      <div class="sec-title">${txt.secNavagraha}</div>
      <table>
        <tr>
          <th>${txt.thPlanet}</th><th>${txt.thSign}</th><th>${txt.thDegree}</th><th>${txt.thHouse}</th>
          <th>${txt.thNakshatra}</th><th>${txt.thPada}</th><th>${txt.thNavamsa}</th><th>${txt.thDignity}</th><th>${txt.thMotion}</th>
        </tr>
        ${planetRows}
      </table>
    </div>

    <!-- 12 Bhavas -->
    <div class="sec">
      <div class="sec-title">${txt.secHouses}</div>
      <table>
        <tr>
          <th style="width:50px">${txt.thHouseNum}</th><th style="width:100px">${txt.thHouseSign}</th><th>${txt.thHouseSignifications}</th><th>${txt.thHouseOccupants}</th>
        </tr>
        ${allHouseRows}
      </table>
    </div>

    <!-- Yogas & Doshas -->
    <div class="grid2">
      <div class="sec">
        <div class="sec-title">${txt.secYogas} (${activeYogas.length})</div>
        ${activeYogas.length ? activeYogas.map((y: any) => `
          <div class="yoga-item">
            <h4>${y.name} <span style="float:right;font-size:10px;background:#dcfce7;color:#15803d;padding:1px 6px;border-radius:3px">${y.strength || (lang === 'en' ? "Active" : "सक्रिय")}</span></h4>
            <p>${y.description || ""}</p>
          </div>
        `).join("") : `<p style="color:#888;font-size:11.5px">${txt.noYogas}</p>`}
      </div>
      <div class="sec">
        <div class="sec-title">${txt.secDoshas}</div>
        ${activeDoshas.length ? activeDoshas.map((ds: any) => `
          <div class="dosha-item ${ds.severity === "High" ? "dosha-high" : "dosha-med"}">
            <h4 style="color:${ds.severity === "High" ? "#dc2626" : "#c46b1e"}">${ds.name} <span style="float:right;font-size:10px">${ds.severity}</span></h4>
            <p>${ds.description || ""}</p>
            ${ds.remedies && ds.remedies.length ? `<ul>${ds.remedies.slice(0, 3).map((r: string) => `<li>${r}</li>`).join("")}</ul>` : ""}
          </div>
        `).join("") : `
          <div class="yoga-item" style="border-left-color:#15803d;background:#f0fdf4">
            <h4 style="color:#15803d">${txt.neutralDoshasTitle}</h4>
            <p>${txt.neutralDoshasDesc}</p>
          </div>
        `}
      </div>
    </div>

    <!-- Vimshottari Dasha -->
    <div class="sec">
      <div class="sec-title">${txt.secDasha}</div>
      <div style="display:flex;gap:24px;margin-bottom:8px;font-size:12px">
        <div>${txt.activeMahadasha} <strong style="color:#8b1a1a">${mahadashaLord}</strong></div>
        <div>${txt.activeAntardasha} <strong>${antardashaLord}</strong></div>
        <div>${txt.balanceRemaining} <strong>${d.dasha_balance || "—"}</strong></div>
      </div>
      <div style="margin-top:6px;font-size:11px;color:#777">
        ${txt.antardashaSeq}
      </div>
      <div style="margin-top:4px">
        ${antarList}
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      ${txt.footer(pName)}
    </div>
  </div>

  <script>
    window.onload = function() {
      setTimeout(function() {
        window.print();
      }, 400);
    };
  <\/script>
</body>
</html>`);

  win.document.close();
}
