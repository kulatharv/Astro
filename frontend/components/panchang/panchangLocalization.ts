/**
 * Panchang Localization & Astronomical Terminology System
 * Supports Marathi ('mr'), Hindi ('hi'), and English ('en')
 */

export interface PanchangUIText {
  eyebrow: string;
  title: string;
  subtitle: string;
  share: string;
  copied: string;
  exportIcs: string;
  astronomicalCalendar: string;
  lunarPhase: string;
  realTimeIst: string;
  configureAlmanac: string;
  selectLocation: string;
  selectDate: string;
  today: string;
  tomorrow: string;
  refresh: string;
  locationLabel: string;
  coordinatesLabel: string;
  sunrise: string;
  sunset: string;
  moonrise: string;
  moonset: string;
  sunriseSub: string;
  sunsetSub: string;
  moonriseSub: string;
  moonsetSub: string;
  panchaAngaTitle: string;
  suryaSiddhantaPrecision: string;
  tithiLabel: string;
  nakshatraLabel: string;
  yogaLabel: string;
  karanaLabel: string;
  varaLabel: string;
  endsAt: string;
  activeDaylight: string;
  elongation: string;
  pada: string;
  consciousness: string;
  relationship: string;
  practicalExecution: string;
  solarVitality: string;
  shubhMuhurat: string;
  idealVentures: string;
  abhijitMuhurat: string;
  mostVictorious: string;
  abhijitDesc: string;
  brahmaMuhurat: string;
  spiritualDawn: string;
  brahmaDesc: string;
  ashubhKaal: string;
  avoidUndertakings: string;
  rahuKaal: string;
  avoidInitiations: string;
  rahuDesc: string;
  yamaganda: string;
  yamagandaDesc: string;
  gulikaKaal: string;
  gulikaDesc: string;
  dishaShoolLabel: string;
  tabChoghadiya: string;
  tabHoras: string;
  tabPlanets: string;
  tabFestivals: string;
  activeChoghadiyaNow: string;
  duration: string;
  remaining: string;
  dayChoghadiya: string;
  nightChoghadiya: string;
  horasDesc: string;
  horaDuration: string;
  hora: string;
  colGraha: string;
  colRashi: string;
  colDegrees: string;
  colNakshatra: string;
  colGati: string;
  retrograde: string;
  direct: string;
  filterAll: string;
  filterMajor: string;
  filterEkadashi: string;
  filterVrat: string;
  filterPurnima: string;
  todaysCelebration: string;
  sattvicKarma: string;
  remedyLabel: string;
  upcoming: string;
  noFestivals: string;
  shlokaSanskrit: string;
  shlokaTranslation: string;
  shlokaSource: string;
}

export const PANCHANG_UI_TEXT: Record<string, PanchangUIText> = {
  mr: {
    eyebrow: 'दैनिक पवित्र पंचांग',
    title: 'पंचांग आणि शुभ मुहूर्त',
    subtitle: 'काळाचे पाच महत्त्वाचे घटक (पंच-अंग) जे मानवी कर्मांना निसर्गाच्या तालाशी जोडतात.',
    share: 'शेअर करा',
    copied: 'कॉपी झाले!',
    exportIcs: 'कॅलेंडर डाऊनलोड (ICS)',
    astronomicalCalendar: 'वैदिक खगोलीय पंचांग',
    lunarPhase: 'चंद्राची कला',
    realTimeIst: 'थेट वेळ (IST)',
    configureAlmanac: 'पंचांग सेटिंग्ज',
    selectLocation: 'स्थान (शहर) निवडा',
    selectDate: 'तारीख निवडा',
    today: 'आज',
    tomorrow: 'उद्या',
    refresh: 'ताजे करा',
    locationLabel: 'स्थान:',
    coordinatesLabel: 'अक्षांश-रेखांश:',
    sunrise: 'सूर्योदय',
    sunset: 'सूर्यास्त',
    moonrise: 'चंद्रोदय',
    moonset: 'चंद्रास्त',
    sunriseSub: 'सुवर्ण पहाट · सूर्य होरा प्रारंभ',
    sunsetSub: 'संध्याकाळची संध्या · प्रदोष काळ',
    moonriseSub: 'चंद्र उदय · मनःशांती व अंतर्ज्ञान',
    moonsetSub: 'चंद्र अस्त · रात्र काळ',
    panchaAngaTitle: 'पंचांग — पाच पवित्र घटक',
    suryaSiddhantaPrecision: 'सूर्य सिद्धांत अचूकता',
    tithiLabel: '१. तिथी (चंद्र दिवस)',
    nakshatraLabel: '२. नक्षत्र (चंद्र नक्षत्र)',
    yogaLabel: '३. योग (सूर्य-चंद्र समन्वय)',
    karanaLabel: '४. करण (अर्धी तिथी)',
    varaLabel: '५. वार (सौर दिवस)',
    endsAt: 'समाप्ती',
    activeDaylight: 'दिवसभरात सक्रिय',
    elongation: 'चंद्र-सूर्य अंतर',
    pada: 'चरण',
    consciousness: 'चेतना आणि अंतर्ज्ञान',
    relationship: 'संबंध आणि सात्त्विकता',
    practicalExecution: 'कर्म सिद्धी आणि कार्यशक्ती',
    solarVitality: 'सौर तेज आणि दीर्घायुष्य',
    shubhMuhurat: 'शुभ मुहूर्त (सात्त्विक काल)',
    idealVentures: 'नवीन कार्यासाठी सर्वोत्तम',
    abhijitMuhurat: 'अभिजीत मुहूर्त',
    mostVictorious: 'सर्व विजयी मुहूर्त',
    abhijitDesc: 'सर्व दोष दूर करणारा सर्वोत्तम मुहूर्त. नवीन करार, व्यवसाय प्रारंभ, खरेदी आणि शुभ कार्यांसाठी अत्यंत फलदायी मानला जातो.',
    brahmaMuhurat: 'ब्राह्म मुहूर्त (अमृत वेला)',
    spiritualDawn: 'आध्यात्मिक उषाकाल',
    brahmaDesc: 'सूर्योदयापूर्वी १ तास ३६ मिनिटे सुरू होणारा काळ. ध्यान, मंत्र जप, प्राणायाम आणि ईश्वर चिंतनासाठी परम पवित्र.',
    ashubhKaal: 'अशुभ काळ (सावधगिरी आवश्यक)',
    avoidUndertakings: 'नवीन कार्ये टाळावीत',
    rahuKaal: 'राहु काळ (राहु वेला)',
    avoidInitiations: 'नवीन प्रारंभ वर्ज्य',
    rahuDesc: 'राहु ग्रहाचा प्रभाव असलेला काळ. या काळात नवीन करार, लांबचा प्रवास किंवा गृहप्रवेश करणे टाळावे.',
    yamaganda: 'यमगंड काळ',
    yamagandaDesc: 'यम देवांचे अधिपत्य · कार्यात निष्फळता टाळा',
    gulikaKaal: 'गुलिक काळ',
    gulikaDesc: 'शनीपुत्र गुलिक · कामात विलंब शक्य',
    dishaShoolLabel: 'दिशा शूल:',
    tabChoghadiya: 'दिवस व रात्र चौघडिया',
    tabHoras: '२४ तास ग्रहीय होरा',
    tabPlanets: 'ग्रह गोचर (सध्याची स्थिती)',
    tabFestivals: 'आगामी सण व उत्सव',
    activeChoghadiyaNow: 'सध्या सुरू असलेला चौघडिया',
    duration: 'कालावधी:',
    remaining: 'शिल्लक वेळ:',
    dayChoghadiya: 'दिवसाचा चौघडिया (सूर्योदय ते सूर्यास्त)',
    nightChoghadiya: 'रात्रीचा चौघडिया (सूर्यास्त ते पुढील सूर्योदय)',
    horasDesc: 'सूर्योदयापासून प्राचीन काळाच्या नियमांनुसार २४ ग्रहीय होरा क्रमवार सुरू राहतात.',
    horaDuration: '१ होरा ≈ ६० मिनिटे',
    hora: 'होरा',
    colGraha: 'ग्रह (Planet)',
    colRashi: 'रास (Sign)',
    colDegrees: 'अंश (Degrees)',
    colNakshatra: 'नक्षत्र',
    colGati: 'गती (Motion)',
    retrograde: '⟲ वक्री (Vakra)',
    direct: '▶ मार्गी (Margi)',
    filterAll: 'सर्व सण',
    filterMajor: 'प्रमुख सण',
    filterEkadashi: 'एकादशी व्रते',
    filterVrat: 'पवित्र व्रते',
    filterPurnima: 'पौर्णिमा / अमावास्या',
    todaysCelebration: 'आजचा उत्सव',
    sattvicKarma: 'सात्त्विक उपाय:',
    remedyLabel: 'उपाय:',
    upcoming: 'आगामी',
    noFestivals: 'या वर्गवारीत सध्या कोणतेही आगामी सण उपलब्ध नाहीत.',
    shlokaSanskrit: '“तिथेश्च श्रियमाप्नोति वारादायुष्यवर्धनम्। नक्षत्राद्धरते पापं योगाद्रोगनिवारणम्। करणात्कार्यसिद्धिः स्यात् पञ्चाङ्गफलमुत्तमम्॥”',
    shlokaTranslation: '“तिथीच्या ज्ञानाने ऐश्वर्य व समृद्धी मिळते, वाराने आयुष्य वाढते, नक्षत्राने पापांचा नाश होतो, योगाने रोगांचे निवारण होते आणि करणाने कार्य सिद्धीस जाते. असे हे पवित्र पंचांगाचे श्रेष्ठ फळ आहे.”',
    shlokaSource: 'सूर्य सिद्धांत आणि बृहत् पराशर होरा शास्त्र',
  },
  hi: {
    eyebrow: 'दैनिक पवित्र पंचांग',
    title: 'पंचांग एवं शुभ मुहूर्त',
    subtitle: 'समय के पांच अंग (पंच-अंग) जो मानवीय कर्मों को प्राकृतिक ब्रह्मांड के साथ सामंजस्य में लाते हैं।',
    share: 'साझा करें',
    copied: 'कॉपी किया गया!',
    exportIcs: 'कैलेंडर डाउनलोड (ICS)',
    astronomicalCalendar: 'वैदिक खगोलीय पंचांग',
    lunarPhase: 'चंद्र कला',
    realTimeIst: 'लाइव समय (IST)',
    configureAlmanac: 'पंचांग विन्यास',
    selectLocation: 'स्थान (शहर) चुनें',
    selectDate: 'दिनांक चुनें',
    today: 'आज',
    tomorrow: 'कल',
    refresh: 'रिफ्रेश करें',
    locationLabel: 'स्थान:',
    coordinatesLabel: 'निर्देशांक:',
    sunrise: 'सूर्योदय',
    sunset: 'सूर्यास्त',
    moonrise: 'चंद्रोदय',
    moonset: 'चंद्रास्त',
    sunriseSub: 'स्वर्णिम प्रभात · सूर्य होरा प्रारंभ',
    sunsetSub: 'सायं संध्या · प्रदोष काल',
    moonriseSub: 'चंद्र उदय · मानसिक शांति एवं अंतर्दृष्टि',
    moonsetSub: 'चंद्र अस्त · रात्रि काल',
    panchaAngaTitle: 'पंचांग — पाँच पवित्र अंग',
    suryaSiddhantaPrecision: 'सूर्य सिद्धांत परिशुद्धता',
    tithiLabel: '१. तिथि (चंद्र दिवस)',
    nakshatraLabel: '२. नक्षत्र (चंद्र नक्षत्र)',
    yogaLabel: '३. योग (सूर्य-चंद्र सामंजस्य)',
    karanaLabel: '४. करण (अर्ध-तिथि)',
    varaLabel: '५. वार (सौर दिवस)',
    endsAt: 'समाप्ति',
    activeDaylight: 'दिनभर सक्रिय',
    elongation: 'चंद्र-सूर्य अंतर',
    pada: 'चरण',
    consciousness: 'चेतना एवं अंतर्ज्ञान',
    relationship: 'संबंध एवं सात्विकता',
    practicalExecution: 'कर्म सिद्धि एवं कार्यशक्ति',
    solarVitality: 'सौर तेज एवं दीर्घायु',
    shubhMuhurat: 'शुभ मुहूर्त (सात्विक काल)',
    idealVentures: 'नवीन कार्यों हेतु सर्वोत्तम',
    abhijitMuhurat: 'अभिजीत मुहूर्त',
    mostVictorious: 'सर्व विजयी मुहूर्त',
    abhijitDesc: 'सर्व दोषों को शांत करने वाला उत्तम मुहूर्त। नवीन अनुबंध, व्यापार शुभारंभ और मांगलिक कार्यों हेतु सर्वश्रेष्ठ।',
    brahmaMuhurat: 'ब्राह्म मुहूर्त (अमृत वेला)',
    spiritualDawn: 'आध्यात्मिक उषाकाल',
    brahmaDesc: 'सूर्योदय से १ घंटा ३६ मिनट पूर्व का काल। ध्यान, जप, प्राणायाम और पवित्र विद्याध्ययन हेतु परम फलदायी।',
    ashubhKaal: 'अशुभ काल (सावधानी आवश्यक)',
    avoidUndertakings: 'नवीन कार्य आरंभ न करें',
    rahuKaal: 'राहु काल (राहु वेला)',
    avoidInitiations: 'नवीन प्रारंभ वर्जित',
    rahuDesc: 'राहु ग्रह के प्रभाव का समय। इसमें नए अनुबंध, यात्रा या गृह प्रवेश करने से बचें।',
    yamaganda: 'यमगंड काल',
    yamagandaDesc: 'यम का प्रभाव · कार्यों में निष्फलता से बचें',
    gulikaKaal: 'गुलिक काल',
    gulikaDesc: 'शनिपुत्र गुलिक · कार्यों में विलंब संभव',
    dishaShoolLabel: 'दिशा शूल:',
    tabChoghadiya: 'दिन एवं रात्रि चौघड़िया',
    tabHoras: '२४ घंटे ग्रहीय होरा',
    tabPlanets: 'ग्रह गोचर (वर्तमान स्थिति)',
    tabFestivals: 'आगामी व्रत एवं त्यौहार',
    activeChoghadiyaNow: 'वर्तमान में सक्रिय चौघड़िया',
    duration: 'अवधि:',
    remaining: 'शेष समय:',
    dayChoghadiya: 'दिन का चौघड़िया (सूर्योदय से सूर्यास्त)',
    nightChoghadiya: 'रात्रि का चौघड़िया (सूर्यास्त से सूर्योदय)',
    horasDesc: 'सूर्योदय से शास्त्रीय क्रम के अनुसार २४ ग्रहीय होरा निरंतर चलती हैं।',
    horaDuration: '१ होरा ≈ ६० मिनट',
    hora: 'होरा',
    colGraha: 'ग्रह (Planet)',
    colRashi: 'राशि (Sign)',
    colDegrees: 'अंश (Degrees)',
    colNakshatra: 'नक्षत्र',
    colGati: 'गति (Motion)',
    retrograde: '⟲ वक्री (Vakra)',
    direct: '▶ मार्गी (Margi)',
    filterAll: 'सभी त्यौहार',
    filterMajor: 'प्रमुख त्यौहार',
    filterEkadashi: 'एकादशी व्रत',
    filterVrat: 'पवित्र व्रत',
    filterPurnima: 'पूर्णिमा / अमावस्या',
    todaysCelebration: 'आज का उत्सव',
    sattvicKarma: 'सात्विक उपाय:',
    remedyLabel: 'उपाय:',
    upcoming: 'आगामी',
    noFestivals: 'इस श्रेणी में कोई आगामी त्यौहार उपलब्ध नहीं है।',
    shlokaSanskrit: '“तिथेश्च श्रियमाप्नोति वारादायुष्यवर्धनम्। नक्षत्राद्धरते पापं योगाद्रोगनिवारणम्। करणात्कार्यसिद्धिः स्यात् पञ्चाङ्गफलमुत्तमम्॥”',
    shlokaTranslation: '“तिथि के ज्ञान से ऐश्वर्य मिलता है, वार से आयु बढ़ती है, नक्षत्र से पापों का शमन होता है, योग से रोग दूर होते हैं, और करण से कार्य सिद्धि होती है। ऐसा पवित्र पंचांग का उत्तम फल है।”',
    shlokaSource: 'सूर्य सिद्धांत एवं बृहत् पराशर होरा शास्त्र',
  },
  en: {
    eyebrow: 'Daily Sacred Almanac',
    title: 'Panchang & Auspicious Muhurat',
    subtitle: 'The five limbs (Pancha-Anga) of celestial time synchronizing human endeavor with the natural cosmos.',
    share: 'Share',
    copied: 'Copied!',
    exportIcs: 'Export ICS',
    astronomicalCalendar: 'Vedic Astronomical Calendar',
    lunarPhase: 'Lunar Phase',
    realTimeIst: 'Real-time IST',
    configureAlmanac: 'Configure Almanac',
    selectLocation: 'Select Location (City)',
    selectDate: 'Select Gregorian Date',
    today: 'Today',
    tomorrow: 'Tomorrow',
    refresh: 'Refresh',
    locationLabel: 'Location:',
    coordinatesLabel: 'Coordinates:',
    sunrise: 'Sunrise',
    sunset: 'Sunset',
    moonrise: 'Moonrise',
    moonset: 'Moonset',
    sunriseSub: 'Golden dawn · Surya Hora begins',
    sunsetSub: 'Evening Sandhya · Pradosh window',
    moonriseSub: 'Chandra Udaya · Mind elevation',
    moonsetSub: 'Chandra Asta · Nocturnal descent',
    panchaAngaTitle: 'Pancha-Anga — Five Sacred Limbs',
    suryaSiddhantaPrecision: 'Surya Siddhanta Precision',
    tithiLabel: '1. Tithi (Lunar Phase)',
    nakshatraLabel: '2. Nakshatra (Lunar Mansion)',
    yogaLabel: '3. Yoga (Luni-Solar Harmony)',
    karanaLabel: '4. Karana (Half-Tithi)',
    varaLabel: '5. Vara (Solar Weekday)',
    endsAt: 'Ends at',
    activeDaylight: 'Active during daylight hours',
    elongation: 'Elongation',
    pada: 'Pada',
    consciousness: 'Consciousness & Intuition',
    relationship: 'Relationship & Purity',
    practicalExecution: 'Practical Execution',
    solarVitality: 'Solar Vitality & Longevity',
    shubhMuhurat: 'Shubh Muhurat (Auspicious)',
    idealVentures: 'Ideal for New Ventures',
    abhijitMuhurat: 'Abhijit Muhurat',
    mostVictorious: 'Most Victorious',
    abhijitDesc: 'Universal cleanser of minor astrological blemishes. Optimum for signing contracts, commercial launches, and celebrations.',
    brahmaMuhurat: 'Brahma Muhurat (Amrit Vela)',
    spiritualDawn: 'Spiritual Dawn',
    brahmaDesc: 'Occurs 1 hour 36 minutes prior to sunrise. Supreme clarity of mind for meditation, mantra japa, and sacred study.',
    ashubhKaal: 'Ashubh Kaal (Caution Recommended)',
    avoidUndertakings: 'Avoid Fresh Undertakings',
    rahuKaal: 'Rahu Kaal (Rahu\'s Window)',
    avoidInitiations: 'Avoid Initiations',
    rahuDesc: 'Governed by the shadow node Rahu. Do not sign agreements, initiate travels, or perform Griha Pravesh.',
    yamaganda: 'Yamaganda',
    yamagandaDesc: 'Ruled by Yama · Fruitless efforts',
    gulikaKaal: 'Gulika Kaal',
    gulikaDesc: 'Son of Saturn · Delays outcome',
    dishaShoolLabel: 'Disha Shool:',
    tabChoghadiya: 'Day & Night Choghadiya',
    tabHoras: '24-Hour Planetary Horas',
    tabPlanets: 'Planetary Transits (Gochar)',
    tabFestivals: 'Upcoming Festivals',
    activeChoghadiyaNow: 'Active Choghadiya Right Now',
    duration: 'Duration:',
    remaining: 'Remaining:',
    dayChoghadiya: 'Day Choghadiya (Sunrise to Sunset)',
    nightChoghadiya: 'Night Choghadiya (Sunset to Next Sunrise)',
    horasDesc: '24 Planetary Hours sequenced according to classical Chaldean order from sunrise.',
    horaDuration: '1 Hora ≈ 60 mins',
    hora: 'Hora',
    colGraha: 'Graha (Planet)',
    colRashi: 'Rashi (Sign)',
    colDegrees: 'Degrees',
    colNakshatra: 'Nakshatra',
    colGati: 'Gati (Motion)',
    retrograde: '⟲ Retrograde (Vakra)',
    direct: '▶ Direct (Margi)',
    filterAll: 'All Celebrations',
    filterMajor: 'Major Festivals',
    filterEkadashi: 'Ekadashi Vrats',
    filterVrat: 'Sacred Vrats',
    filterPurnima: 'Purnima / Amavasya',
    todaysCelebration: 'Today\'s Celebration',
    sattvicKarma: 'Sattvic Karma:',
    remedyLabel: 'Remedy:',
    upcoming: 'Upcoming',
    noFestivals: 'No matching upcoming festivals in this filter category.',
    shlokaSanskrit: '“तिथेश्च श्रियमाप्नोति वारादायुष्यवर्धनम्। नक्षत्राद्धरते पापं योगाद्रोगनिवारणम्। करणात्कार्यसिद्धिः स्यात् पञ्चाङ्गफलमुत्तमम्॥”',
    shlokaTranslation: '“By knowledge of Tithi comes prosperity; from Vara comes longevity; from Nakshatra sins are mitigated; from Yoga diseases are averted; and from Karana success in actions is achieved. Such are the fruits of the sacred Panchanga.”',
    shlokaSource: 'Surya Siddhanta & Brihat Parashara Hora Shastra',
  },
};

export const CITIES_LOCALIZED: Record<string, { mr: string; hi: string; en: string }> = {
  Pune: { mr: 'पुणे', hi: 'पुणे', en: 'Pune' },
  Mumbai: { mr: 'मुंबई', hi: 'मुंबई', en: 'Mumbai' },
  'New Delhi': { mr: 'नवी दिल्ली', hi: 'नई दिल्ली', en: 'New Delhi' },
  Varanasi: { mr: 'वाराणसी (काशी)', hi: 'वाराणसी (काशी)', en: 'Varanasi' },
  Bengaluru: { mr: 'बेंगळुरू', hi: 'बेंगलुरु', en: 'Bengaluru' },
  Chennai: { mr: 'चेन्नई', hi: 'चेन्नई', en: 'Chennai' },
  Kolkata: { mr: 'कोलकाता', hi: 'कोलकाता', en: 'Kolkata' },
  Hyderabad: { mr: 'हैदराबाद', hi: 'हैदराबाद', en: 'Hyderabad' },
  Ahmedabad: { mr: 'अहमदाबाद', hi: 'अहमदाबाद', en: 'Ahmedabad' },
  Jaipur: { mr: 'जयपूर', hi: 'जयपुर', en: 'Jaipur' },
  Ujjain: { mr: 'उज्जैन (अवन्तिका)', hi: 'उज्जैन', en: 'Ujjain' },
  Haridwar: { mr: 'हरिद्वार', hi: 'हरिद्वार', en: 'Haridwar' },
};

export const WEEKDAY_DEITIES_LOCALIZED: Record<number, { mr: string; hi: string; en: string }> = {
  0: { mr: 'सूर्य देव · रविवार (Ravi-vara)', hi: 'सूर्य देव · रविवार (Ravi-vara)', en: 'Surya Dev (Sun) · Ravi-vara' },
  1: { mr: 'चंद्र देव · सोमवार (Soma-vara)', hi: 'चंद्र देव · सोमवार (Soma-vara)', en: 'Chandra Dev (Moon) · Soma-vara' },
  2: { mr: 'मंगळ देव · मंगळवार (Mangala-vara)', hi: 'मंगल देव · मंगलवार (Mangala-vara)', en: 'Mangala Dev (Mars) · Mangala-vara' },
  3: { mr: 'बुध देव · बुधवार (Budha-vara)', hi: 'बुध देव · बुधवार (Budha-vara)', en: 'Budha Dev (Mercury) · Budha-vara' },
  4: { mr: 'बृहस्पती (गुरु) देव · गुरुवार (Guru-vara)', hi: 'बृहस्पति (गुरु) देव · गुरुवार (Guru-vara)', en: 'Brihaspati Dev (Jupiter) · Guru-vara' },
  5: { mr: 'शुक्र देव · शुक्रवार (Shukra-vara)', hi: 'शुक्र देव · शुक्रवार (Shukra-vara)', en: 'Shukra Dev (Venus) · Shukra-vara' },
  6: { mr: 'शनी देव · शनिवार (Shani-vara)', hi: 'शनि देव · शनिवार (Shani-vara)', en: 'Shani Dev (Saturn) · Shani-vara' },
};

export const TITHI_NAMES: Record<string, { mr: string; hi: string }> = {
  Pratipada: { mr: 'प्रतिपदा', hi: 'प्रतिपदा' },
  Dwitiya: { mr: 'द्वितीया', hi: 'द्वितीया' },
  Tritiya: { mr: 'तृतीया', hi: 'तृतीया' },
  Chaturthi: { mr: 'चतुर्थी', hi: 'चतुर्थी' },
  Panchami: { mr: 'पंचमी', hi: 'पंचमी' },
  Shashthi: { mr: 'षष्ठी', hi: 'षष्ठी' },
  Saptami: { mr: 'सप्तमी', hi: 'सप्तमी' },
  Ashtami: { mr: 'अष्टमी', hi: 'अष्टमी' },
  Navami: { mr: 'नवमी', hi: 'नवमी' },
  Dashami: { mr: 'दशमी', hi: 'दशमी' },
  Ekadashi: { mr: 'एकादशी', hi: 'एकादशी' },
  Dwadashi: { mr: 'द्वादशी', hi: 'द्वादशी' },
  Trayodashi: { mr: 'त्रयोदशी', hi: 'त्रयोदशी' },
  Chaturdashi: { mr: 'चतुर्दशी', hi: 'चतुर्दशी' },
  Purnima: { mr: 'पौर्णिमा', hi: 'पूर्णिमा' },
  Poornima: { mr: 'पौर्णिमा', hi: 'पूर्णिमा' },
  Amavasya: { mr: 'अमावास्या', hi: 'अमावस्या' },
};

export const NAKSHATRA_NAMES: Record<string, { mr: string; hi: string }> = {
  Ashwini: { mr: 'अश्विनी', hi: 'अश्विनी' },
  Bharani: { mr: 'भरणी', hi: 'भरणी' },
  Krittika: { mr: 'कृत्तिका', hi: 'कृत्तिका' },
  Rohini: { mr: 'रोहिणी', hi: 'रोहिणी' },
  Mrigashira: { mr: 'मृगशीर्ष', hi: 'मृगशीर्ष' },
  Ardra: { mr: 'आर्द्रा', hi: 'आर्द्रा' },
  Punarvasu: { mr: 'पुनर्वसु', hi: 'पुनर्वसु' },
  Pushya: { mr: 'पुष्य', hi: 'पुष्य' },
  Ashlesha: { mr: 'आश्लेषा', hi: 'आश्लेषा' },
  Magha: { mr: 'मघा', hi: 'मघा' },
  'Purva Phalguni': { mr: 'पूर्वा फाल्गुनी', hi: 'पूर्वा फाल्गुनी' },
  'Uttara Phalguni': { mr: 'उत्तरा फाल्गुनी', hi: 'उत्तरा फाल्गुनी' },
  Hasta: { mr: 'हस्त', hi: 'हस्त' },
  Chitra: { mr: 'चित्रा', hi: 'चित्रा' },
  Swati: { mr: 'स्वाती', hi: 'स्वाति' },
  Vishakha: { mr: 'विशाखा', hi: 'विशाखा' },
  Anuradha: { mr: 'अनुराधा', hi: 'अनुराधा' },
  Jyeshtha: { mr: 'ज्येष्ठा', hi: 'ज्येष्ठा' },
  Mula: { mr: 'मूळ (मूल)', hi: 'मूल' },
  'Purva Ashadha': { mr: 'पूर्वाषाढा', hi: 'पूर्वाषाढ़ा' },
  'Uttara Ashadha': { mr: 'उत्तराषाढा', hi: 'उत्तराषाढ़ा' },
  Shravana: { mr: 'श्रवण', hi: 'श्रवण' },
  Dhanishta: { mr: 'धनिष्ठा', hi: 'धनिष्ठा' },
  Shatabhisha: { mr: 'शतभिषा', hi: 'शतभिषा' },
  'Purva Bhadrapada': { mr: 'पूर्वाभाद्रपदा', hi: 'पूर्वाभाद्रपद' },
  'Uttara Bhadrapada': { mr: 'उत्तराभाद्रपदा', hi: 'उत्तराभाद्रपद' },
  Revati: { mr: 'रेवती', hi: 'रेवती' },
};

export const YOGA_NAMES: Record<string, { mr: string; hi: string }> = {
  Vishkambha: { mr: 'विष्कंभ', hi: 'विष्कम्भ' },
  Priti: { mr: 'प्रीती', hi: 'प्रीति' },
  Ayushman: { mr: 'आयुष्मान', hi: 'आयुष्मान' },
  Saubhagya: { mr: 'सौभाग्य', hi: 'सौभाग्य' },
  Shobhana: { mr: 'शोभन', hi: 'शोभन' },
  Atiganda: { mr: 'अतिगंड', hi: 'अतिगण्ड' },
  Sukarma: { mr: 'सुकर्मा', hi: 'सुकर्मा' },
  Dhriti: { mr: 'धृती', hi: 'धृति' },
  Shula: { mr: 'शूल', hi: 'शूल' },
  Ganda: { mr: 'गंड', hi: 'गण्ड' },
  Vriddhi: { mr: 'वृद्धी', hi: 'वृद्धि' },
  Dhruva: { mr: 'ध्रुव', hi: 'ध्रुव' },
  Vyaghata: { mr: 'व्याघात', hi: 'व्याघात' },
  Harshana: { mr: 'हर्षण', hi: 'हर्षण' },
  Vajra: { mr: 'वज्र', hi: 'वज्र' },
  Siddhi: { mr: 'सिद्धी', hi: 'सिद्धि' },
  Vyatipata: { mr: 'व्यतीपात', hi: 'व्यतीपात' },
  Variyan: { mr: 'वरीयान', hi: 'वरीयान' },
  Parigha: { mr: 'परिघ', hi: 'परिघ' },
  Shiva: { mr: 'शिव', hi: 'शिव' },
  Siddha: { mr: 'सिद्ध', hi: 'सिद्ध' },
  Sadhya: { mr: 'साध्य', hi: 'साध्य' },
  Shubha: { mr: 'शुभ', hi: 'शुभ' },
  Shukla: { mr: 'शुक्ल', hi: 'शुक्ल' },
  Brahma: { mr: 'ब्रह्म', hi: 'ब्रह्म' },
  Indra: { mr: 'इंद्र', hi: 'इन्द्र' },
  Vaidhriti: { mr: 'वैधृती', hi: 'वैधृति' },
};

export const KARANA_NAMES: Record<string, { mr: string; hi: string }> = {
  Bava: { mr: 'बव', hi: 'बव' },
  Balava: { mr: 'बालव', hi: 'बालव' },
  Kaulava: { mr: 'कौलव', hi: 'कौलव' },
  Taitila: { mr: 'तैतिल', hi: 'तैतिल' },
  Gara: { mr: 'गर', hi: 'गर' },
  Vanija: { mr: 'वणिज', hi: 'वणिज' },
  Vishti: { mr: 'विष्टी (भद्रा)', hi: 'विष्टि (भद्रा)' },
  Bhadra: { mr: 'भद्रा (विष्टी)', hi: 'भद्रा (विष्टि)' },
  Shakuni: { mr: 'शकुनी', hi: 'शकुनि' },
  Chatushpada: { mr: 'चतुष्पाद', hi: 'चतुष्पाद' },
  Naga: { mr: 'नाग', hi: 'नाग' },
  Kimstughna: { mr: 'किम्स्तुघ्न', hi: 'किंस्तुघ्न' },
};

export const RASHI_NAMES: Record<string, { mr: string; hi: string }> = {
  Mesha: { mr: 'मेष', hi: 'मेष' },
  Vrishabha: { mr: 'वृषभ', hi: 'वृषभ' },
  Mithuna: { mr: 'मिथुन', hi: 'मिथुन' },
  Karka: { mr: 'कर्क', hi: 'कर्क' },
  Simha: { mr: 'सिंह', hi: 'सिंह' },
  Kanya: { mr: 'कन्या', hi: 'कन्या' },
  Tula: { mr: 'तूळ (तुला)', hi: 'तुला' },
  Vrishchika: { mr: 'वृश्चिक', hi: 'वृश्चिक' },
  Dhanu: { mr: 'धनु', hi: 'धनु' },
  Makara: { mr: 'मकर', hi: 'मकर' },
  Kumbha: { mr: 'कुंभ', hi: 'कुंभ' },
  Meena: { mr: 'मीन', hi: 'मीन' },
  Aries: { mr: 'मेष', hi: 'मेष' },
  Taurus: { mr: 'वृषभ', hi: 'वृषभ' },
  Gemini: { mr: 'मिथुन', hi: 'मिथुन' },
  Cancer: { mr: 'कर्क', hi: 'कर्क' },
  Leo: { mr: 'सिंह', hi: 'सिंह' },
  Virgo: { mr: 'कन्या', hi: 'कन्या' },
  Libra: { mr: 'तूळ (तुला)', hi: 'तुला' },
  Scorpio: { mr: 'वृश्चिक', hi: 'वृश्चिक' },
  Sagittarius: { mr: 'धनु', hi: 'धनु' },
  Capricorn: { mr: 'मकर', hi: 'मकर' },
  Aquarius: { mr: 'कुंभ', hi: 'कुंभ' },
  Pisces: { mr: 'मीन', hi: 'मीन' },
};

export const PLANET_NAMES: Record<string, { mr: string; hi: string }> = {
  Sun: { mr: 'सूर्य (Surya)', hi: 'सूर्य (Surya)' },
  Surya: { mr: 'सूर्य (Surya)', hi: 'सूर्य (Surya)' },
  Moon: { mr: 'चंद्र (Chandra)', hi: 'चंद्र (Chandra)' },
  Chandra: { mr: 'चंद्र (Chandra)', hi: 'चंद्र (Chandra)' },
  Mars: { mr: 'मंगळ (Mangala)', hi: 'मंगल (Mangala)' },
  Mangala: { mr: 'मंगळ (Mangala)', hi: 'मंगल (Mangala)' },
  Mercury: { mr: 'बुध (Budha)', hi: 'बुध (Budha)' },
  Budha: { mr: 'बुध (Budha)', hi: 'बुध (Budha)' },
  Jupiter: { mr: 'गुरु (बृहस्पती)', hi: 'गुरु (बृहस्पति)' },
  Guru: { mr: 'गुरु (बृहस्पती)', hi: 'गुरु (बृहस्पति)' },
  Venus: { mr: 'शुक्र (Shukra)', hi: 'शुक्र (Shukra)' },
  Shukra: { mr: 'शुक्र (Shukra)', hi: 'शुक्र (Shukra)' },
  Saturn: { mr: 'शनी (Shani)', hi: 'शनि (Shani)' },
  Shani: { mr: 'शनी (Shani)', hi: 'शनि (Shani)' },
  Rahu: { mr: 'राहू (Rahu)', hi: 'राहु (Rahu)' },
  Ketu: { mr: 'केतू (Ketu)', hi: 'केतु (Ketu)' },
};

export const CHOGHADIYA_NAMES: Record<string, { mr: { name: string; label: string }; hi: { name: string; label: string } }> = {
  Shubh: {
    mr: { name: 'शुभ', label: 'शुभ (उत्तम)' },
    hi: { name: 'शुभ', label: 'शुभ (उत्तम)' },
  },
  Labh: {
    mr: { name: 'लाभ', label: 'शुभ (लाभ)' },
    hi: { name: 'लाभ', label: 'शुभ (लाभ)' },
  },
  Amrit: {
    mr: { name: 'अमृत', label: 'सर्वोत्तम अमृत' },
    hi: { name: 'अमृत', label: 'सर्वोत्तम अमृत' },
  },
  Char: {
    mr: { name: 'चर', label: 'सामान्य / प्रवास' },
    hi: { name: 'चर', label: 'सामान्य / यात्रा' },
  },
  Rog: {
    mr: { name: 'रोग', label: 'अशुभ (रोग)' },
    hi: { name: 'रोग', label: 'अशुभ (रोग)' },
  },
  Kaal: {
    mr: { name: 'काळ', label: 'अशुभ (हानी)' },
    hi: { name: 'काल', label: 'अशुभ (हानि)' },
  },
  Udveg: {
    mr: { name: 'उद्वेग', label: 'अशुभ (चिंता)' },
    hi: { name: 'उद्वेग', label: 'अशुभ (चिंता)' },
  },
};

export const FESTIVAL_TRANSLATIONS: Record<
  string,
  {
    mr: { name: string; desc: string; remedies?: string };
    hi: { name: string; desc: string; remedies?: string };
  }
> = {
  'Ahoi Ashtami': {
    mr: {
      name: 'अहोई अष्टमी',
      desc: 'संतानाचे उत्तम आरोग्य, दीर्घायुष्य आणि सौख्यासाठी मातांचा निर्जला उपवास.',
      remedies: 'संध्याकाळी तारे पाहिल्यानंतर अहोई मातेचे पूजन व अर्घ्य द्यावे.',
    },
    hi: {
      name: 'अहोई अष्टमी',
      desc: 'संतान के दीर्घायु, स्वास्थ्य और सुख-समृद्धि हेतु माताओं का निर्जला व्रत।',
      remedies: 'सायंकाल तारों के दर्शन पश्चात अहोई माता का विधिवत पूजन करें।',
    },
  },
  'Rama Ekadashi': {
    mr: {
      name: 'रमा एकादशी',
      desc: 'दिवाळीपूर्वी भगवान विष्णू आणि माता महालक्ष्मीला समर्पित पवित्र एकादशी.',
      remedies: 'विष्णू सहस्रनाम पठण करा आणि तुळशीजवळ सायंकाळी दिवा लावा.',
    },
    hi: {
      name: 'रमा एकादशी',
      desc: 'दीपावली पूर्व भगवान श्रीहरि विष्णु एवं महालक्ष्मी को समर्पित पावन एकादशी।',
      remedies: 'विष्णु सहस्रनाम का पाठ करें तथा तुलसी जी के समक्ष दीप प्रज्वलित करें।',
    },
  },
  'Dhanteras (Dhanvantari Jayanti)': {
    mr: {
      name: 'धनत्रयोदशी (धन्वंतरी जयंती)',
      desc: 'आरोग्याचे दैवत भगवान धन्वंतरी जयंती व कुबेर-लक्ष्मी पूजन.',
      remedies: 'तांबे, चांदी किंवा पितळेची भांडी खरेदी करावीत; घराबाहेर १३ यमदीप प्रज्वलित करावेत.',
    },
    hi: {
      name: 'धनतेरस (धन्वंतरि जयंती)',
      desc: 'आरोग्य प्रदाता भगवान धन्वंतरि प्राकट्योत्सव एवं धन-समृद्धि की साधना।',
      remedies: 'तांबे, चांदी अथवा नए पात्र खरीदें; मुख्य द्वार पर १३ यमदीप प्रज्वलित करें।',
    },
  },
  'Naraka Chaturdashi (Kali Chaudas / Choti Diwali)': {
    mr: {
      name: 'नरक चतुर्दशी (अभ्यंगस्नान / छोटी दिवाळी)',
      desc: 'अपमृत्यू निवारणासाठी अभ्यंगस्नान, यम तर्पण आणि नरकासुर वध विजयोत्सव.',
      remedies: 'सूर्योदयापूर्वी उटणे लावून अभ्यंगस्नान करा व चार मुखी दिवा लावा.',
    },
    hi: {
      name: 'नरक चतुर्दशी (काली चौदस / छोटी दिवाली)',
      desc: 'अपमृत्यु निवारण, यम तर्पण एवं भगवान श्रीकृष्ण द्वारा भौमासुर मर्दन विजय।',
      remedies: 'सूर्योदय से पूर्व उबटन युक्त स्नान करें तथा चतुर्मुखी दीप जलाएं।',
    },
  },
  'Lakshmi Puja (Diwali)': {
    mr: {
      name: 'लक्ष्मी पूजन (दीपावली महापूजा)',
      desc: 'ऐश्वर्य, बुद्धी आणि मांगल्याचे प्रतीक असलेली दीपावली महापूजा.',
      remedies: 'प्रदोष काळात श्री सूक्त व कनकधारा स्तोत्रासह महालक्ष्मी व गणेशाचे पूजन.',
    },
    hi: {
      name: 'लक्ष्मी पूजन (दीपावली)',
      desc: 'सर्व ऐश्वर्य, सद्बुद्धि एवं कल्याणकारी महालक्ष्मी-गणेश की महापूजा।',
      remedies: 'प्रदोष काल में श्री सूक्त एवं कनकधारा स्तोत्र से पूजन कर दीपदान करें।',
    },
  },
  'Govardhan Puja (Annakut)': {
    mr: {
      name: 'गोवर्धन पूजा (अन्नकूट उत्सव)',
      desc: 'निसर्ग, गोमाता आणि गोवर्धन पर्वताची कृतज्ञतापूर्वक आराधना.',
      remedies: 'गोमातेला चारा द्या आणि ५६ भोगाचा अन्नकूट नैवेद्य अर्पण करा.',
    },
    hi: {
      name: 'गोवर्धन पूजा (अन्नकूट)',
      desc: 'प्रकृति, गौ-माता एवं भगवान श्रीकृष्ण द्वारा रक्षित गोवर्धन की कृतज्ञ पूजा।',
      remedies: 'गौमाता को ग्रास दें एवं भगवान को विविध मिष्ठान्न अन्नकूट अर्पित करें।',
    },
  },
  'Bhai Dooj (Bhau Beej)': {
    mr: {
      name: 'भाऊबीज (यम द्वितीया)',
      desc: 'भाऊ-बहिणीच्या पवित्र प्रेमाचे प्रतीक आणि यमराज-यमुना मिलन दिन.',
      remedies: 'बहिणीने भावाला ओवाळावे आणि यमराजाच्या कृपेसाठी प्रार्थना करावी.',
    },
    hi: {
      name: 'भाई दूज (यम द्वितीया)',
      desc: 'भाई-बहन के अगाध स्नेह का पावन पर्व एवं यमराज-यमुना मिलन स्मृति।',
      remedies: 'बहनें भाई का तिलक कर आरती करें तथा दीर्घायु की प्रार्थना करें।',
    },
  },
  'Devutthana Ekadashi': {
    mr: {
      name: 'प्रबोधिनी / देवउठणी एकादशी (तुळशी विवाह प्रारंभ)',
      desc: 'चातुर्मास समाप्ती, भगवान विष्णूंची योगनिद्रा समाप्ती व मांगलिक कार्यांचा प्रारंभ.',
      remedies: 'उपवास ठेवावा आणि ऊस, आवळा, बोरे अर्पण करून तुळशी विवाह साजरा करावा.',
    },
    hi: {
      name: 'देवउठनी एकादशी (प्रबोधिनी एकादशी)',
      desc: 'चातुर्मास समाप्ति, श्रीहरि का जागरण एवं समस्त शुभ-मांगलिक कार्यों का प्रारंभ।',
      remedies: 'एकादशी व्रत रखें तथा तुलसी-शालिग्राम विवाह उत्सव मनाएं।',
    },
  },
  'Dev Deepawali (Kartik Purnima)': {
    mr: {
      name: 'देव दीपावली (त्रिपुरारी पौर्णिमा)',
      desc: 'काशीमध्ये देवांनी साजरा केलेला दीपोत्सव आणि त्रिपुरासुर वध विजय.',
      remedies: 'नदीकाठी किंवा मंदिरात दिवे लावावेत व शिव स्तोत्रांचे पठण करावे.',
    },
    hi: {
      name: 'देव दीपावली (कार्तिक पूर्णिमा)',
      desc: 'काशी के पावन तटों पर देवताओं द्वारा मनाया जाने वाला दिव्य प्रकाश पर्व।',
      remedies: 'सरोवरों व मंदिरों में दीपदान करें एवं शिव महिम्न स्तोत्र का पाठ करें।',
    },
  },
  'Shukla Pradosh Vrat': {
    mr: {
      name: 'शुक्ल प्रदोष व्रत',
      desc: 'मनोकामना पूर्तीसाठी प्रदोष वेळेत भगवान शिव आणि माता पार्वतीचे पूजन.',
      remedies: 'प्रदोष काळात शंकराला बेलाची पाने व दुधाचा अभिषेक अर्पण करावा.',
    },
    hi: {
      name: 'शुक्ल प्रदोष व्रत',
      desc: 'समस्त मनोरथ सिद्धि हेतु सांध्यवेला में भगवान शिव-पार्वती का अभिषेक।',
      remedies: 'प्रदोष काल में शिवलिंग पर कच्चा दूध व बिल्वपत्र अर्पित करें।',
    },
  },
  'Sankashti Chaturthi': {
    mr: {
      name: 'संकष्ट चतुर्थी',
      desc: 'संकटनाशक श्री गणेश व्रत; चंद्रोदयानंतर नैवेद्य दाखवून उपवास सोडतात.',
      remedies: 'चंद्रोदयापर्यंत उपवास ठेवा, २१ दुर्वा व मोदक गणेशाला अर्पण करा.',
    },
    hi: {
      name: 'संकष्टी चतुर्थी',
      desc: 'संकटों के हरण हेतु श्री गणेश का पावन व्रत; चंद्रोदय दर्शनोपरांत पारण।',
      remedies: 'चंद्रोदय तक उपवास रखें तथा भगवान गणेश को २१ दूर्वा व मोदक अर्पित करें।',
    },
  },
};

/** Helper to format Gregorian Date into beautiful localized string */
export function formatLocalizedDate(dateString: string, locale: string): string {
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;

    if (locale === 'mr') {
      const options: Intl.DateTimeFormatOptions = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      };
      return d.toLocaleDateString('mr-IN', options);
    }
    if (locale === 'hi') {
      const options: Intl.DateTimeFormatOptions = {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      };
      return d.toLocaleDateString('hi-IN', options);
    }
    return d.toLocaleDateString('en-IN', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return dateString;
  }
}

/** Helper to localize Tithi string (e.g. "Krishna Saptami" -> "कृष्ण सप्तमी") */
export function localizeTithi(tithiStr: string | undefined, paksha: string | undefined, locale: string): string {
  if (!tithiStr) return locale === 'mr' ? 'शुक्ल दशमी' : locale === 'hi' ? 'शुक्ल दशमी' : 'Shukla Dashami';
  if (locale === 'en') return tithiStr;

  let localized = tithiStr;
  const isMr = locale === 'mr';

  // Replace Paksha names
  localized = localized.replace(/Krishna/gi, isMr ? 'कृष्ण' : 'कृष्ण');
  localized = localized.replace(/Shukla/gi, isMr ? 'शुक्ल' : 'शुक्ल');

  // Replace Tithi names
  for (const [enName, trans] of Object.entries(TITHI_NAMES)) {
    const reg = new RegExp(`\\b${enName}\\b`, 'gi');
    if (reg.test(localized)) {
      localized = localized.replace(reg, isMr ? trans.mr : trans.hi);
    }
  }

  return localized;
}

/** Helper to localize Paksha (e.g. "Krishna" -> "कृष्ण") */
export function localizePaksha(paksha: string | undefined, locale: string): string {
  if (!paksha) return locale === 'en' ? 'Shukla' : 'शुक्ल';
  if (locale === 'en') return paksha;
  if (/krishna/i.test(paksha)) return 'कृष्ण';
  if (/shukla/i.test(paksha)) return 'शुक्ल';
  return paksha;
}

/** Helper to localize Nakshatra string (e.g. "Pushya" -> "पुष्य") */
export function localizeNakshatra(nakshatra: string | undefined, locale: string): string {
  if (!nakshatra) return locale === 'mr' ? 'रोहिणी' : locale === 'hi' ? 'रोहिणी' : 'Rohini';
  if (locale === 'en') return nakshatra;

  const isMr = locale === 'mr';
  for (const [enName, trans] of Object.entries(NAKSHATRA_NAMES)) {
    if (nakshatra.toLowerCase().includes(enName.toLowerCase())) {
      return nakshatra.replace(new RegExp(enName, 'gi'), isMr ? trans.mr : trans.hi);
    }
  }
  return nakshatra;
}

/** Helper to localize Yoga string (e.g. "Sadhya" -> "साध्य") */
export function localizeYoga(yoga: string | undefined, locale: string): string {
  if (!yoga) return locale === 'mr' ? 'शुक्ल' : locale === 'hi' ? 'शुक्ल' : 'Shukla';
  if (locale === 'en') return yoga;

  const isMr = locale === 'mr';
  for (const [enName, trans] of Object.entries(YOGA_NAMES)) {
    if (yoga.toLowerCase().includes(enName.toLowerCase())) {
      return yoga.replace(new RegExp(enName, 'gi'), isMr ? trans.mr : trans.hi);
    }
  }
  return yoga;
}

/** Helper to localize Karana string (e.g. "Bava" -> "बव") */
export function localizeKarana(karana: string | undefined, locale: string): string {
  if (!karana) return locale === 'mr' ? 'तैतिल' : locale === 'hi' ? 'तैतिल' : 'Taitila';
  if (locale === 'en') return karana;

  const isMr = locale === 'mr';
  for (const [enName, trans] of Object.entries(KARANA_NAMES)) {
    if (karana.toLowerCase().includes(enName.toLowerCase())) {
      return karana.replace(new RegExp(enName, 'gi'), isMr ? trans.mr : trans.hi);
    }
  }
  return karana;
}

/** Helper to localize Vara string */
export function localizeVara(vara: string | undefined, dayIdx: number, locale: string): string {
  if (locale === 'en') return vara || 'Sunday';
  const deity = WEEKDAY_DEITIES_LOCALIZED[dayIdx];
  if (deity) {
    return locale === 'mr' ? deity.mr.split(' · ')[1] || 'रविवार' : deity.hi.split(' · ')[1] || 'रविवार';
  }
  return locale === 'mr' ? 'रविवार' : 'रविवार';
}

/** Helper to localize Samvat */
export function localizeSamvat(samvat: any, locale: string): string {
  if (!samvat) {
    return locale === 'mr'
      ? 'विक्रम संवत २०८३ · आनंद'
      : locale === 'hi'
      ? 'विक्रम संवत २०८३ · आनंद'
      : 'Vikram Samvat 2083 · Ananda';
  }

  let text = '';
  if (typeof samvat === 'string') {
    text = samvat;
  } else if (typeof samvat === 'object') {
    const parts: string[] = [];
    if (samvat.vikram_samvat) parts.push(`Vikram Samvat ${samvat.vikram_samvat}`);
    if (samvat.shaka_samvat) parts.push(`Shaka ${samvat.shaka_samvat}`);
    if (samvat.month_amanta) parts.push(samvat.month_amanta);
    text = parts.join(' · ') || 'Vikram Samvat 2083 · Ananda';
  }

  if (locale === 'en') return text;

  const isMr = locale === 'mr';
  let localized = text
    .replace(/Vikram Samvat/gi, isMr ? 'विक्रम संवत' : 'विक्रम संवत')
    .replace(/Shaka/gi, isMr ? 'शक' : 'शक')
    .replace(/Chaitra/gi, isMr ? 'चैत्र' : 'चैत्र')
    .replace(/Vaishakha/gi, isMr ? 'वैशाख' : 'वैशाख')
    .replace(/Jyeshtha/gi, isMr ? 'ज्येष्ठ' : 'ज्येष्ठ')
    .replace(/Ashadha/gi, isMr ? 'आषाढ' : 'आषाढ़')
    .replace(/Shravana/gi, isMr ? 'श्रावण' : 'श्रावण')
    .replace(/Bhadrapada/gi, isMr ? 'भाद्रपद' : 'भाद्रपद')
    .replace(/Ashwin/gi, isMr ? 'अश्विन' : 'अश्विन')
    .replace(/Kartika/gi, isMr ? 'कार्तिक' : 'कार्तिक')
    .replace(/Margashirsha/gi, isMr ? 'मार्गशीर्ष' : 'मार्गशीर्ष')
    .replace(/Pausha/gi, isMr ? 'पौष' : 'पौष')
    .replace(/Magha/gi, isMr ? 'माघ' : 'माघ')
    .replace(/Phalguna/gi, isMr ? 'फाल्गुन' : 'फाल्गुन');

  return localized;
}

/** Helper to localize Disha Shool */
export function localizeDishaShool(dishaShool: any, locale: string): string {
  if (!dishaShool) {
    if (locale === 'mr') return 'पूर्व (Purva) — प्रवासापूर्वी आले किंवा मोहरी खाऊन निघावे.';
    if (locale === 'hi') return 'पूर्व (Purva) — यात्रा से पूर्व अदरक अथवा राई ग्रहण करें।';
    return 'East (Purva) — Chew ginger or mustard seeds before undertaking unavoidable travels.';
  }

  let raw = '';
  if (typeof dishaShool === 'string') {
    raw = dishaShool;
  } else if (typeof dishaShool === 'object') {
    const dir = dishaShool.direction ? `${dishaShool.direction}${dishaShool.sanskrit ? ` (${dishaShool.sanskrit})` : ''}` : '';
    const avoid = dishaShool.avoid_msg || '';
    const remedy = dishaShool.remedy ? `Remedy: ${dishaShool.remedy}` : '';
    raw = [dir, avoid, remedy].filter(Boolean).join(' — ');
  }

  if (locale === 'en') return raw;

  const isMr = locale === 'mr';
  return raw
    .replace(/Disha Shool:\s*/gi, '')
    .replace(/West\s*\(Pashchim\)/gi, isMr ? 'पश्चिम (Pashchim)' : 'पश्चिम (Pashchim)')
    .replace(/East\s*\(Purva\)/gi, isMr ? 'पूर्व (Purva)' : 'पूर्व (Purva)')
    .replace(/North\s*\(Uttar\)/gi, isMr ? 'उत्तर (Uttar)' : 'उत्तर (Uttar)')
    .replace(/South\s*\(Dakshin\)/gi, isMr ? 'दक्षिण (Dakshin)' : 'दक्षिण (Dakshin)')
    .replace(/Avoid long-distance travel towards West on Sundays/gi, isMr ? 'रविवारी पश्चिम दिशेला लांबचा प्रवास टाळावा' : 'रविवार को पश्चिम दिशा में दूरस्थ यात्रा से बचें')
    .replace(/Avoid long-distance travel towards East on Mondays/gi, isMr ? 'सोमवारी पूर्व दिशेला लांबचा प्रवास टाळावा' : 'सोमवार को पूर्व दिशा में दूरस्थ यात्रा से बचें')
    .replace(/Avoid long-distance travel towards North on Tuesdays/gi, isMr ? 'मंगळवारी उत्तर दिशेला लांबचा प्रवास टाळावा' : 'मंगलवार को उत्तर दिशा में दूरस्थ यात्रा से बचें')
    .replace(/Chew ginger or mustard seeds before travel/gi, isMr ? 'उपाय: प्रवासापूर्वी आले किंवा मोहरी खाऊन निघावे' : 'उपाय: यात्रा से पूर्व अदरक या सरसों का सेवन करें')
    .replace(/Chew betel leaf before travel/gi, isMr ? 'उपाय: प्रवासापूर्वी विड्याचे पान खावे' : 'उपाय: यात्रा से पूर्व पान का सेवन करें')
    .replace(/Eat curd before travel/gi, isMr ? 'उपाय: प्रवासापूर्वी थोडे दही खावे' : 'उपाय: यात्रा से पूर्व दही का सेवन करें')
    .replace(/Eat jaggery before travel/gi, isMr ? 'उपाय: प्रवासापूर्वी गूळ खाऊन निघावे' : 'उपाय: यात्रा से पूर्व गुड़ खाकर निकलें')
    .replace(/Remedy:/gi, isMr ? 'उपाय:' : 'उपाय:');
}

/** Helper to localize Choghadiya item */
export function localizeChoghadiyaItem(
  item: { name: string; label: string; is_auspicious: boolean; ruling_planet?: string; start: string; end: string },
  locale: string
) {
  if (locale === 'en') return item;
  const match = CHOGHADIYA_NAMES[item.name];
  if (match) {
    const localized = locale === 'mr' ? match.mr : match.hi;
    return {
      ...item,
      name: localized.name,
      label: localized.label,
    };
  }
  return item;
}

/** Helper to localize Hora planet */
export function localizePlanetName(planetName: string, locale: string): string {
  if (locale === 'en') return planetName;
  const isMr = locale === 'mr';
  for (const [key, val] of Object.entries(PLANET_NAMES)) {
    if (planetName.toLowerCase().includes(key.toLowerCase())) {
      return isMr ? val.mr : val.hi;
    }
  }
  return planetName;
}

/** Helper to localize Rashi */
export function localizeRashiName(rashiName: string, locale: string): string {
  if (locale === 'en') return rashiName;
  const isMr = locale === 'mr';
  for (const [key, val] of Object.entries(RASHI_NAMES)) {
    if (rashiName.toLowerCase().includes(key.toLowerCase())) {
      return rashiName.replace(new RegExp(key, 'gi'), isMr ? val.mr : val.hi);
    }
  }
  return rashiName;
}

/** Helper to localize an upcoming festival item */
export function localizeFestivalItem(fest: any, locale: string): any {
  if (locale === 'en') return fest;

  const isMr = locale === 'mr';
  const custom = FESTIVAL_TRANSLATIONS[fest.name];

  const locTithi = localizeTithi(fest.tithi, fest.paksha, locale);
  const locPaksha = localizePaksha(fest.paksha, locale);
  const locNakshatra = localizeNakshatra(fest.nakshatra, locale);

  if (custom) {
    const tr = isMr ? custom.mr : custom.hi;
    return {
      ...fest,
      name: tr.name,
      desc: tr.desc,
      remedies: tr.remedies || fest.remedies,
      tithi: locTithi,
      paksha: locPaksha,
      nakshatra: locNakshatra,
    };
  }

  return {
    ...fest,
    tithi: locTithi,
    paksha: locPaksha,
    nakshatra: locNakshatra,
  };
}
