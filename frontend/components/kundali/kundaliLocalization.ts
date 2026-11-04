export interface KundaliLocale {
  badge: string;
  title: string;
  subtitle: string;
  inputCardTitle: string;
  inputCardSubtitle: string;
  fullNameLabel: string;
  fullNamePlaceholder: string;
  dobLabel: string;
  tobLabel: string;
  cityLabel: string;
  cityPlaceholder: string;
  ayanamsaLabel: string;
  generateBtn: string;
  generatingBtn: string;
  sampleProfileBtn: string;
  downloadPdfBtn: string;
  generatePdfReportBtn: string;

  // Tabs
  tabOverview: string;
  tabCharts: string;
  tabPlanets: string;
  tabStrength: string;
  tabYogasDoshas: string;
  tabHouses: string;
  tabDasha: string;
  tabChat: string;

  // Birth Details
  birthDetailsTitle: string;
  name: string;
  dob: string;
  tob: string;
  birthPlace: string;
  lagna: string;
  lagnaDegree: string;
  moonSign: string;
  nakshatra: string;
  pada: string;
  tithi: string;
  yoga: string;
  karana: string;
  ayanamsa: string;
  dashaBalance: string;

  // Charts
  chartsTitle: string;
  chartStyle: string;
  northIndian: string;
  southIndian: string;
  d1Title: string;
  d1Subtitle: string;
  d9Title: string;
  d9Subtitle: string;

  // Planets
  planetsTitle: string;
  colPlanet: string;
  colSign: string;
  colDegree: string;
  colHouse: string;
  colNakshatra: string;
  colPada: string;
  colNavamsa: string;
  colDignity: string;
  colStatus: string;
  direct: string;
  retrograde: string;
  combust: string;

  // Strength
  strengthTitle: string;
  overall: string;
  career: string;
  finance: string;
  relationship: string;
  health: string;
  mental: string;
  spiritual: string;

  // Yogas & Doshas
  yogasTitle: string;
  yogasSubtitle: string;
  doshasTitle: string;
  doshasSubtitle: string;
  activeYogasCount: string;
  noYogas: string;
  severityHigh: string;
  severityModerate: string;
  severityNone: string;
  remediesTitle: string;

  // Houses
  housesTitle: string;
  housesSubtitle: string;
  houseSign: string;
  houseLord: string;
  houseOccupants: string;
  houseKaraka: string;
  houseSignifications: string;

  // Dasha
  dashaTitle: string;
  currentMahadasha: string;
  currentAntardasha: string;
  balanceRemaining: string;
  dashaTimelineTitle: string;
  dashaYears: string;

  // Chat
  chatTitle: string;
  chatSubtitle: string;
  chatPlaceholder: string;
  sendBtn: string;
  sampleQuestion1: string;
  sampleQuestion2: string;
  sampleQuestion3: string;
}

export const KUNDALI_TRANSLATIONS: Record<string, KundaliLocale> = {
  en: {
    badge: 'Authoritative Vedic Kundali',
    title: 'Janma Kundali & Planetary Architecture',
    subtitle: 'High-precision Swiss Ephemeris natal calculations, D1 & D9 chart projections, Vimshottari Dasha chronology, and classical Vedic analysis.',
    inputCardTitle: 'Enter Birth Details',
    inputCardSubtitle: 'Provide accurate birth information to generate your Vedic Kundali',
    fullNameLabel: 'Full Name',
    fullNamePlaceholder: 'e.g. Arjun Sharma',
    dobLabel: 'Date of Birth',
    tobLabel: 'Time of Birth (IST)',
    cityLabel: 'Birth City',
    cityPlaceholder: 'Search city (e.g. Delhi, Mumbai)',
    ayanamsaLabel: 'Ayanamsa',
    generateBtn: 'Calculate Kundali',
    generatingBtn: 'Computing Cosmic Ephemeris...',
    sampleProfileBtn: 'Use Sample Chart',
    downloadPdfBtn: 'Generate PDF Report',
    generatePdfReportBtn: 'Generate PDF Report',

    tabOverview: 'Overview',
    tabCharts: 'Vedic Charts',
    tabPlanets: 'Navagraha Table',
    tabStrength: 'Bhava Bala',
    tabYogasDoshas: 'Yogas & Doshas',
    tabHouses: '12 Bhavas',
    tabDasha: 'Vimshottari Dasha',
    tabChat: 'Astro AI Assistant',

    birthDetailsTitle: 'Birth Panchang & Astronomical Pillars',
    name: 'Native Name',
    dob: 'Date of Birth',
    tob: 'Time of Birth',
    birthPlace: 'Birth Location',
    lagna: 'Lagna (Ascendant)',
    lagnaDegree: 'Lagna Degree',
    moonSign: 'Moon Sign (Chandra Rashi)',
    nakshatra: 'Birth Nakshatra',
    pada: 'Nakshatra Pada',
    tithi: 'Janma Tithi',
    yoga: 'Birth Yoga',
    karana: 'Karana',
    ayanamsa: 'Ayanamsa (Lahiri/Chitra)',
    dashaBalance: 'Dasha Balance at Birth',

    chartsTitle: 'Birth Horoscopes (Varga Projections)',
    chartStyle: 'Chart Style',
    northIndian: 'North Indian (Diamond)',
    southIndian: 'South Indian (Square)',
    d1Title: 'D1 — Rashi Chart',
    d1Subtitle: 'Physical existence, personality, and life path',
    d9Title: 'D9 — Navamsha Chart',
    d9Subtitle: 'Spiritual destiny, marriage, and inner potency',

    planetsTitle: 'Planetary Longitudes & Dignities (Navagraha)',
    colPlanet: 'Graha (Planet)',
    colSign: 'Rashi (Sign)',
    colDegree: 'Exact Degree',
    colHouse: 'Bhava (House)',
    colNakshatra: 'Nakshatra',
    colPada: 'Pada',
    colNavamsa: 'Navamsha',
    colDignity: 'Dignity',
    colStatus: 'Motion',
    direct: 'Direct',
    retrograde: 'Retrograde ℞',
    combust: 'Combust 🔥',

    strengthTitle: 'Chart Vitality & Domain Potency',
    overall: 'Overall Vitality',
    career: 'Career & Karma (10th)',
    finance: 'Wealth & Assets (2nd/11th)',
    relationship: 'Marriage & Partnerships (7th)',
    health: 'Physical Longevity (1st/6th/8th)',
    mental: 'Mental Equilibrium (Moon/5th)',
    spiritual: 'Dharma & Moksha (9th/12th)',

    yogasTitle: 'Auspicious Vedic Yogas',
    yogasSubtitle: 'Classical planetary combinations conferring wisdom, prosperity, and authority',
    doshasTitle: 'Karmic Patterns & Dosha Analysis',
    doshasSubtitle: 'Comprehensive evaluation of Manglik, Sade Sati, Kaal Sarp, and Gandmool influences',
    activeYogasCount: 'Active Yogas Detected',
    noYogas: 'No major classical yogas detected for this configuration.',
    severityHigh: 'High Severity',
    severityModerate: 'Moderate Influence',
    severityNone: 'Neutral / Mitigated',
    remediesTitle: 'Classical Vedic Remedies & Mitigations',

    housesTitle: 'Comprehensive 12 Bhava Analysis',
    housesSubtitle: 'In-depth breakdown of house lords, occupant grahas, and life dimensions',
    houseSign: 'Zodiac Sign',
    houseLord: 'Bhava Lord',
    houseOccupants: 'Occupant Grahas',
    houseKaraka: 'Significator (Karaka)',
    houseSignifications: 'Core Significations',

    dashaTitle: 'Vimshottari Dasha Chronology',
    currentMahadasha: 'Active Mahadasha',
    currentAntardasha: 'Active Antardasha',
    balanceRemaining: 'Balance Remaining',
    dashaTimelineTitle: '120-Year Vimshottari Mahadasha Cycle',
    dashaYears: 'Years',

    chatTitle: 'Consult Your Birth Chart',
    chatSubtitle: 'Ask specialized questions regarding career, marriage timing, or planetary strengths',
    chatPlaceholder: 'Ask a question about your kundali...',
    sendBtn: 'Ask AI',
    sampleQuestion1: 'What career fields are most favorable based on my 10th house?',
    sampleQuestion2: 'How does my current Mahadasha affect marriage & relationships?',
    sampleQuestion3: 'What Vedic remedies are recommended for my planetary placements?',
  },

  hi: {
    badge: 'प्रामाणिक वैदिक जन्म कुंडली',
    title: 'जन्म कुंडली एवं ग्रहीय विन्यास',
    subtitle: 'स्विस एफेमेरिस की सूक्ष्म गणनाओं पर आधारित जन्म चक्र, नवमांश (D9), विंशोत्तरी दशा चक्र एवं शास्त्रीय फलित विवेचना।',
    inputCardTitle: 'जन्म विवरण प्रविष्ट करें',
    inputCardSubtitle: 'वैदिक जन्म कुंडली हेतु प्रामाणिक जन्म विवरण प्रविष्ट करें',
    fullNameLabel: 'पूरा नाम',
    fullNamePlaceholder: 'उदा. अर्जुन शर्मा',
    dobLabel: 'जन्म तिथि',
    tobLabel: 'जन्म समय (IST)',
    cityLabel: 'जन्म स्थान / नगर',
    cityPlaceholder: 'नगर खोजें (उदा. दिल्ली, मुंबई, जयपुर)',
    ayanamsaLabel: 'अयनांश',
    generateBtn: 'कुंडली गणना करें',
    generatingBtn: 'खगोलीय गणना जारी है...',
    sampleProfileBtn: 'नमूना कुंडली प्रयोग करें',
    downloadPdfBtn: 'PDF रिपोर्ट डाउनलोड करें',
    generatePdfReportBtn: 'PDF रिपोर्ट बनाएं',

    tabOverview: 'सार संक्षेप',
    tabCharts: 'वैदिक चक्र',
    tabPlanets: 'नवग्रह सारणी',
    tabStrength: 'भाव बल',
    tabYogasDoshas: 'योग एवं दोष',
    tabHouses: 'द्वादश भाव',
    tabDasha: 'विंशोत्तरी दशा',
    tabChat: 'ज्योतिष AI सहायक',

    birthDetailsTitle: 'जन्म पंचांग एवं खगोलीय आधार स्तम्भ',
    name: 'जातक का नाम',
    dob: 'जन्म तिथि',
    tob: 'जन्म समय',
    birthPlace: 'जन्म स्थान',
    lagna: 'लग्न (प्रथम भाव)',
    lagnaDegree: 'लग्न अंश',
    moonSign: 'चंद्र राशि',
    nakshatra: 'जन्म नक्षत्र',
    pada: 'नक्षत्र चरण',
    tithi: 'जन्म तिथि',
    yoga: 'जन्म योग',
    karana: 'करण',
    ayanamsa: 'अयनांश (लाहिड़ी/चित्रा)',
    dashaBalance: 'जन्म समय दशा शेष',

    chartsTitle: 'जन्म चक्र (वर्ग कुंडलियां)',
    chartStyle: 'कुंडली शैली',
    northIndian: 'उत्तर भारतीय (हीरा चक्र)',
    southIndian: 'दक्षिण भारतीय (चौकोर चक्र)',
    d1Title: 'D1 — लग्न/राशि चक्र',
    d1Subtitle: 'भौतिक जीवन, व्यक्तित्व एवं संपूर्ण जीवन पथ',
    d9Title: 'D9 — नवमांश चक्र',
    d9Subtitle: 'आध्यात्मिक गंतव्य, वैवाहिक सुख एवं अंतःसामर्थ्य',

    planetsTitle: 'नवग्रह स्पष्ट स्थिति एवं बल',
    colPlanet: 'ग्रह',
    colSign: 'राशि',
    colDegree: 'अंश एवं कला',
    colHouse: 'भाव',
    colNakshatra: 'नक्षत्र',
    colPada: 'चरण',
    colNavamsa: 'नवमांश',
    colDignity: 'ग्रहीय अवस्था',
    colStatus: 'गति',
    direct: 'मार्गी',
    retrograde: 'वक्री ℞',
    combust: 'अस्त 🔥',

    strengthTitle: 'कुंडली बल एवं जीवन क्षेत्र प्रभाव',
    overall: 'समग्र शक्ति',
    career: 'आजीविका एवं कर्म (दशम भाव)',
    finance: 'धन एवं समृद्धि (द्वितीय/एकादश)',
    relationship: 'विवाह एवं साझेदारी (सप्तम भाव)',
    health: 'आरोग्य एवं दीर्घायु (लग्न/षष्ठ/अष्टम)',
    mental: 'मानसिक शांति (चंद्र/पंचम भाव)',
    spiritual: 'धर्म एवं मोक्ष (नवम/द्वादश भाव)',

    yogasTitle: 'सक्रिय शुभ वैदिक योग',
    yogasSubtitle: 'ऋषि पराशर प्रतिपादित राजयोग, धनयोग एवं महापुरुष योग',
    doshasTitle: 'ग्रह दोष एवं निवारण उपाय',
    doshasSubtitle: 'मांगलिक दोष, साढ़े साती, कालसर्प एवं गंडमूल का सूक्ष्म विश्लेषण',
    activeYogasCount: 'सक्रिय योग उपस्थित',
    noYogas: 'इस विन्यास में कोई प्रमुख शास्त्रीय योग नहीं पाया गया।',
    severityHigh: 'तीव्र प्रभाव',
    severityModerate: 'मध्यम प्रभाव',
    severityNone: 'दोष मुक्त / शमित',
    remediesTitle: 'शास्त्रीय वैदिक उपाय एवं शांति कर्म',

    housesTitle: 'द्वादश भाव विस्तृत विवेचना',
    housesSubtitle: 'प्रत्येक भाव के स्वामी, स्थित ग्रह एवं जीवन आयामों का विश्लेषण',
    houseSign: 'भाव राशि',
    houseLord: 'भावेश (स्वामी)',
    houseOccupants: 'स्थित ग्रह',
    houseKaraka: 'कारक ग्रह',
    houseSignifications: 'प्रमुख फल एवं कारकत्व',

    dashaTitle: 'विंशोत्तरी दशा चक्र',
    currentMahadasha: 'वर्तमान महादशा',
    currentAntardasha: 'वर्तमान अंतर्दशा',
    balanceRemaining: 'अवशिष्ट काल',
    dashaTimelineTitle: '120 वर्षीय विंशोत्तरी महादशा कालक्रम',
    dashaYears: 'वर्ष',

    chatTitle: 'अपनी जन्म कुंडली से प्रश्न पूछें',
    chatSubtitle: 'आजीविका, विवाह काल अथवा ग्रहीय उपायों से संबंधित जिज्ञासा का उत्तर प्राप्त करें',
    chatPlaceholder: 'अपनी कुंडली के संबंध में प्रश्न पूछें...',
    sendBtn: 'उत्तर प्राप्त करें',
    sampleQuestion1: 'मेरे दशम भाव के अनुसार कौन सा कार्यक्षेत्र सर्वाधिक अनुकूल रहेगा?',
    sampleQuestion2: 'वर्तमान महादशा मेरे वैवाहिक जीवन पर क्या प्रभाव डाल रही है?',
    sampleQuestion3: 'मेरी कुंडली के अनुसार कौन से वैदिक उपाय श्रेष्ठ फलदायक होंगे?',
  },

  mr: {
    badge: 'प्रमाणित वैदिक जन्म कुंडली',
    title: 'जन्म कुंडली आणि ग्रह स्थिती',
    subtitle: 'स्विस एफिमेरिसच्या अचूक गणितावर आधारित जन्म पत्रिका, नवमांश (D9), विंशोत्तरी महादशा आणि शास्त्रीय वैदिक फलादेश.',
    inputCardTitle: 'जन्म तपशील प्रविष्ट करा',
    inputCardSubtitle: 'वैदिक जन्म पत्रिका तयार करण्यासाठी अचूक माहिती प्रविष्ट करा',
    fullNameLabel: 'पूर्ण नाव',
    fullNamePlaceholder: 'उदा. अर्जुन शर्मा',
    dobLabel: 'जन्म तारीख',
    tobLabel: 'जन्म वेळ (IST)',
    cityLabel: 'जन्म शहर',
    cityPlaceholder: 'शहर शोधा (उदा. पुणे, मुंबई, नागपूर)',
    ayanamsaLabel: 'अयनांश',
    generateBtn: 'कुंडली तयार करा',
    generatingBtn: 'खगोलीय गणना सुरू आहे...',
    sampleProfileBtn: 'नमुना पत्रिका वापरा',
    downloadPdfBtn: 'PDF अहवाल डाउनलोड करा',
    generatePdfReportBtn: 'PDF अहवाल तयार करा',

    tabOverview: 'आढावा',
    tabCharts: 'वैदिक चक्रे',
    tabPlanets: 'नवग्रह सारणी',
    tabStrength: 'भाव सामर्थ्य',
    tabYogasDoshas: 'योग आणि दोष',
    tabHouses: 'बारा भाव',
    tabDasha: 'विंशोत्तरी दशा',
    tabChat: 'ज्योतिष AI सहाय्यक',

    birthDetailsTitle: 'जन्म पंचांग आणि खगोलीय पाया',
    name: 'जातकाचे नाव',
    dob: 'जन्म तारीख',
    tob: 'जन्म वेळ',
    birthPlace: 'जन्म स्थान',
    lagna: 'लग्न (प्रथम भाव)',
    lagnaDegree: 'लग्न अंश',
    moonSign: 'चंद्र राशी',
    nakshatra: 'जन्म नक्षत्र',
    pada: 'नक्षत्र चरण',
    tithi: 'जन्म तिथी',
    yoga: 'जन्म योग',
    karana: 'करण',
    ayanamsa: 'अयनांश (लाहिरी/चित्रा)',
    dashaBalance: 'जन्मावेळची दशा शिल्लक',

    chartsTitle: 'जन्म चक्रे (वर्ग पत्रिका)',
    chartStyle: 'पत्रिका शैली',
    northIndian: 'उत्तर भारतीय (हिरा चक्र)',
    southIndian: 'दक्षिण भारतीय (चौकोनी चक्र)',
    d1Title: 'D1 — लग्न/राशी चक्र',
    d1Subtitle: 'भौतिक अस्तित्व, व्यक्तिमत्त्व आणि जीवन मार्ग',
    d9Title: 'D9 — नवमांश चक्र',
    d9Subtitle: 'आध्यात्मिक गंतव्य, वैवाहिक जीवन आणि आत्मशक्ती',

    planetsTitle: 'नवग्रह स्पष्ट स्थिती आणि सामर्थ्य',
    colPlanet: 'ग्रह',
    colSign: 'राशी',
    colDegree: 'अंश आणि कला',
    colHouse: 'भाव',
    colNakshatra: 'नक्षत्र',
    colPada: 'चरण',
    colNavamsa: 'नवमांश',
    colDignity: 'ग्रहाची अवस्था',
    colStatus: 'गती',
    direct: 'मार्गी',
    retrograde: 'वक्री ℞',
    combust: 'अस्त 🔥',

    strengthTitle: 'पत्रिका सामर्थ्य आणि जीवन क्षेत्र प्रभाव',
    overall: 'एकूण सामर्थ्य',
    career: 'उद्योग आणि कर्म (दशम भाव)',
    finance: 'धन आणि समृद्धी (द्वितीय/एकादश)',
    relationship: 'विवाह आणि भागीदारी (सप्तम भाव)',
    health: 'आरोग्य आणि दीर्घायुष्य (लग्न/षष्ठ/अष्टम)',
    mental: 'मानसिक समतोल (चंद्र/पंचम भाव)',
    spiritual: 'धर्म आणि मोक्ष (नवम/द्वादश भाव)',

    yogasTitle: 'सक्रिय शुभ वैदिक योग',
    yogasSubtitle: 'ऋषी पराशर संमत राजयोग, धनयोग आणि महापुरुष योग',
    doshasTitle: 'ग्रह दोष आणि निवारण उपाय',
    doshasSubtitle: 'मांगलिक दोष, साडेसाती, कालसर्प आणि गंडमूळ यांचे सविस्तर विश्लेषण',
    activeYogasCount: 'सक्रिय योग आढळले',
    noYogas: 'या पत्रिकेत कोणतेही मोठे शास्त्रीय योग आढळले नाहीत.',
    severityHigh: 'तीव्र प्रभाव',
    severityModerate: 'मध्यम प्रभाव',
    severityNone: 'दोष मुक्त / सौम्य',
    remediesTitle: 'शास्त्रीय वैदिक उपाय आणि शांती विधी',

    housesTitle: 'बारा भाव सविस्तर विश्लेषण',
    housesSubtitle: 'प्रत्येक भावाचे अधिपती, स्थित ग्रह आणि जीवन पैलूंचे स्पष्टीकरण',
    houseSign: 'भाव राशी',
    houseLord: 'भावेश (स्वामी)',
    houseOccupants: 'स्थित ग्रह',
    houseKaraka: 'कारक ग्रह',
    houseSignifications: 'प्रमुख कारकत्व आणि फळे',

    dashaTitle: 'विंशोत्तरी दशा चक्र',
    currentMahadasha: 'सध्याची महादशा',
    currentAntardasha: 'सध्याची अंतर्दशा',
    balanceRemaining: 'उर्वरित कालावधी',
    dashaTimelineTitle: '१२० वर्षांचे विंशोत्तरी महादशा कालचक्र',
    dashaYears: 'वर्षे',

    chatTitle: 'आपल्या पत्रिकेविषयी थेट विचारा',
    chatSubtitle: 'कारकीर्द, विवाह काळ किंवा ग्रहीय उपायांविषयी मार्गदर्शक उत्तरे मिळवा',
    chatPlaceholder: 'आपल्या पत्रिकेविषयी प्रश्न विचारा...',
    sendBtn: 'उत्तर मिळवा',
    sampleQuestion1: 'माझ्या दशम भावानुसार कोणती कारकीर्द सर्वात यशदायी ठरेल?',
    sampleQuestion2: 'सध्याच्या महादशेचा वैवाहिक जीवनावर काय परिणाम होईल?',
    sampleQuestion3: 'माझ्या ग्रहस्थितीनुसार कोणते वैदिक उपाय करणे हितावह राहील?',
  },
};

export const RASHI_NAMES_MAP: Record<string, { en: string; hi: string; mr: string; num: number }> = {
  Mesha: { en: 'Aries', hi: 'मेष', mr: 'मेष', num: 1 },
  Vrishabha: { en: 'Taurus', hi: 'वृषभ', mr: 'वृषभ', num: 2 },
  Mithuna: { en: 'Gemini', hi: 'मिथुन', mr: 'मिथुन', num: 3 },
  Karka: { en: 'Cancer', hi: 'कर्क', mr: 'कर्क', num: 4 },
  Simha: { en: 'Leo', hi: 'सिंह', mr: 'सिंह', num: 5 },
  Kanya: { en: 'Virgo', hi: 'कन्या', mr: 'कन्या', num: 6 },
  Tula: { en: 'Libra', hi: 'तुला', mr: 'तुला', num: 7 },
  Vrischika: { en: 'Scorpio', hi: 'वृश्चिक', mr: 'वृश्चिक', num: 8 },
  Dhanu: { en: 'Sagittarius', hi: 'धनु', mr: 'धनु', num: 9 },
  Makara: { en: 'Capricorn', hi: 'मकर', mr: 'मकर', num: 10 },
  Kumbha: { en: 'Aquarius', hi: 'कुंभ', mr: 'कुंभ', num: 11 },
  Meena: { en: 'Pisces', hi: 'मीन', mr: 'मीन', num: 12 },
};

export const PLANET_NAMES_MAP: Record<string, { en: string; hi: string; mr: string; symbol: string; short: string }> = {
  Sun: { en: 'Sun', hi: 'सूर्य', mr: 'सूर्य', symbol: '☉', short: 'Su' },
  Moon: { en: 'Moon', hi: 'चन्द्र', mr: 'चंद्र', symbol: '☽', short: 'Mo' },
  Mars: { en: 'Mars', hi: 'मंगल', mr: 'मंगळ', symbol: '♂', short: 'Ma' },
  Mercury: { en: 'Mercury', hi: 'बुध', mr: 'बुध', symbol: '☿', short: 'Me' },
  Jupiter: { en: 'Jupiter', hi: 'बृहस्पति (गुरु)', mr: 'गुरू', symbol: '♃', short: 'Ju' },
  Venus: { en: 'Venus', hi: 'शुक्र', mr: 'शुक्र', symbol: '♀', short: 'Ve' },
  Saturn: { en: 'Saturn', hi: 'शनि', mr: 'शनी', symbol: '♄', short: 'Sa' },
  Rahu: { en: 'Rahu', hi: 'राहु', mr: 'राहू', symbol: '☊', short: 'Ra' },
  Ketu: { en: 'Ketu', hi: 'केतु', mr: 'केतू', symbol: '☋', short: 'Ke' },
  Lagna: { en: 'Ascendant', hi: 'लग्न', mr: 'लग्न', symbol: 'Asc', short: 'La' },
};

export const HOUSE_NAMES_DATA: Record<number, { enName: string; sanskritName: string; enDesc: string; hiDesc: string; mrDesc: string; karaka: string }> = {
  1: {
    enName: '1st House (Tanu Bhava)',
    sanskritName: 'तनु भाव',
    enDesc: 'Physical body, vitality, innate persona, appearance, self-expression, and general life vitality.',
    hiDesc: 'शारीरिक सौष्ठव, तेज, व्यक्तित्व, स्वभाव, रूप-रंग एवं संपूर्ण जीवन की प्राणशक्ति।',
    mrDesc: 'शारीरिक रचना, व्यक्तिमत्त्व, स्वभाव, रूप-रंग आणि संपूर्ण जीवनाची मूलभूत ऊर्जा.',
    karaka: 'Sun (सूर्य)',
  },
  2: {
    enName: '2nd House (Dhana Bhava)',
    sanskritName: 'धन भाव',
    enDesc: 'Accumulated wealth, liquid savings, speech eloquence, family heritage, and dietary habits.',
    hiDesc: 'संचित धन, पैतृक संपत्ति, वाणी, कुल-परिवार, खानपान एवं मुख सौंदर्य।',
    mrDesc: 'संचित धन, कौटुंबिक वारसा, वाणी, कुटुंब आणि खाण्यापिण्याच्या सवयी.',
    karaka: 'Jupiter (गुरु)',
  },
  3: {
    enName: '3rd House (Sahaja Bhava)',
    sanskritName: 'सहज भाव',
    enDesc: 'Courage, valor, initiative, younger siblings, writing, communication, and short journeys.',
    hiDesc: 'साहस, पराक्रम, छोटे भाई-बहन, संप्रेषण, लेखन कौशल एवं लघु यात्राएं।',
    mrDesc: 'धैर्य, पराक्रम, लहान भावंडे, लेखन, संवाद कौशल्य आणि लहान प्रवास.',
    karaka: 'Mars (मंगल)',
  },
  4: {
    enName: '4th House (Sukha Bhava)',
    sanskritName: 'सुख भाव',
    enDesc: 'Mother, home sanctum, fixed properties, real estate, vehicles, and inner emotional contentment.',
    hiDesc: 'माता, गृहसुख, भूमि, भवन, वाहन, पैतृक सुख एवं आंतरिक मानसिक शांति।',
    mrDesc: 'आई, घराचे सुख, स्थावर मालमत्ता, वाहने आणि अंतःकरणातील समाधान.',
    karaka: 'Moon (चन्द्र)',
  },
  5: {
    enName: '5th House (Putra Bhava)',
    sanskritName: 'पुत्र भाव',
    enDesc: 'Intellect, progeny, past-life merits (Purva Punya), creative genius, and higher spiritual intuition.',
    hiDesc: 'बुद्धि, संतान सुख, पूर्वजन्म संचित पुण्य, रचनात्मकता, मंत्र सिद्धि एवं विद्या।',
    mrDesc: 'बुद्धिमत्ता, संतती, पूर्वपुण्याई, सर्जनशीलता आणि मंत्र ज्ञान.',
    karaka: 'Jupiter (गुरु)',
  },
  6: {
    enName: '6th House (Ari / Roga Bhava)',
    sanskritName: 'अरि / रोग भाव',
    enDesc: 'Health challenges, disease overcoming, competitive victories, daily service, debts, and litigation.',
    hiDesc: 'रोग, ऋण, शत्रु, प्रतिस्पर्धा विजय, नित्य सेवा, संघर्ष एवं विवाद निवृत्ति।',
    mrDesc: 'रोग, शत्रू, कर्ज, स्पर्धा विजय, दैनंदिन सेवा आणि वाद निवारण.',
    karaka: 'Mars / Saturn (मंगल / शनि)',
  },
  7: {
    enName: '7th House (Yuvati Bhava)',
    sanskritName: 'युवति भाव',
    enDesc: 'Spouse, marriage union, business partnerships, public interactions, and legal contracts.',
    hiDesc: 'जीवनसाथी, वैवाहिक सौख्य, व्यावसायिक साझेदारी, जनसंपर्क एवं अनुबंध।',
    mrDesc: 'जोडीदार, वैवाहिक सुख, व्यवसाय भागीदारी आणि सार्वजनिक संबंध.',
    karaka: 'Venus (शुक्र)',
  },
  8: {
    enName: '8th House (Randhra Bhava)',
    sanskritName: 'रन्ध्र भाव',
    enDesc: 'Longevity (Ayur), deep transformations, occult wisdom, unearned inheritance, and hidden truths.',
    hiDesc: 'आयु, गूढ़ विद्या, आकस्मिक धनलाभ, गुप्त शोध, परिवर्तन एवं मोक्ष मार्ग।',
    mrDesc: 'दीर्घायुष्य, गूढ ज्ञान, अचानक धनलाभ, गुप्त गोष्टी आणि आत्मिक परिवर्तन.',
    karaka: 'Saturn (शनि)',
  },
  9: {
    enName: '9th House (Dharma Bhava)',
    sanskritName: 'धर्म भाव',
    enDesc: 'Fortune (Bhagya), ethical righteousness, father, spiritual Guru, and higher pilgrimages.',
    hiDesc: 'भाग्य, धर्म, पिता, गुरु कृपा, उच्च शिक्षा, तीर्थाटन एवं सदगुण।',
    mrDesc: 'भाग्य, धर्म, वडील, गुरूंची कृपा, उच्च शिक्षण आणि तीर्थयात्रा.',
    karaka: 'Jupiter (गुरु)',
  },
  10: {
    enName: '10th House (Karma Bhava)',
    sanskritName: 'कर्म भाव',
    enDesc: 'Profession, executive career, public leadership, social status, dignity, and father\'s legacy.',
    hiDesc: 'आजीविका, पद-प्रतिष्ठा, राज्य सम्मान, सामाजिक प्रभाव, कर्म सिद्धि एवं अधिकार।',
    mrDesc: 'व्यवसाय, पद-प्रतिष्ठा, सामाजिक प्रभाव, कर्तृत्व आणि अधिकार योग.',
    karaka: 'Sun / Mercury / Saturn (सूर्य / बुध / शनि)',
  },
  11: {
    enName: '11th House (Labha Bhava)',
    sanskritName: 'लाभ भाव',
    enDesc: 'Financial gains, fulfillment of ambitions, elder siblings, influential networks, and honors.',
    hiDesc: 'सर्वविध लाभ, मनोकामना पूर्ति, बड़े भाई-बहन, मित्र मण्डली एवं आय के स्रोत।',
    mrDesc: 'सर्व प्रकारचे लाभ, इच्छापूर्ती, मोठे बंधू-भगिनी, मित्रपरिवार आणि उत्पन्न.',
    karaka: 'Jupiter (गुरु)',
  },
  12: {
    enName: '12th House (Vyaya Bhava)',
    sanskritName: 'व्यय / मोक्ष भाव',
    enDesc: 'Expenditure, foreign journeys, subconscious dreams, meditation, seclusion, and final liberation (Moksha).',
    hiDesc: 'व्यय, विदेश प्रवास, ध्यान, निद्रा सुख, दान-पुण्य एवं मोक्ष प्राप्ति।',
    mrDesc: 'खर्च, परदेश प्रवास, ध्यान, दानधर्म आणि अंतिम मुक्ती (मोक्ष).',
    karaka: 'Saturn / Ketu (शनि / केतु)',
  },
};

