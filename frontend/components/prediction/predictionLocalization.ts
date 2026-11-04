export interface DomainMeta {
  key: string;
  icon: string;
  house: string;
  color: string;
  enName: string;
  hiName: string;
  mrName: string;
  enSub: string;
  hiSub: string;
  mrSub: string;
}

export const DOMAINS_LIST: DomainMeta[] = [
  {
    key: 'marriage',
    icon: 'Heart',
    house: '7th House · सप्तम भाव',
    color: '#E11D48',
    enName: 'Marriage & Partnership',
    hiName: 'विवाह एवं सहजीवन',
    mrName: 'विवाह आणि भागीदारी',
    enSub: 'Union, partner traits, harmony, and relationship timing',
    hiSub: 'विवाह योग, जीवनसाथी स्वभाव, मांगलिक विचार एवं दांपत्य सुख',
    mrSub: 'विवाह योग, जोडीदाराचा स्वभाव, मांगलिक विचार आणि वैवाहिक सौख्य',
  },
  {
    key: 'career',
    icon: 'Briefcase',
    house: '10th House · दशम भाव',
    color: '#C46B1E',
    enName: 'Career & Profession',
    hiName: 'आजीविका एवं कर्म',
    mrName: 'कारकीर्द आणि व्यवसाय',
    enSub: 'Vocation, executive leadership, business vs employment',
    hiSub: 'कार्यक्षेत्र, पद-प्रतिष्ठा, व्यवसाय बनाम नौकरी एवं राजयोग',
    mrSub: 'उद्योग क्षेत्र, पद-प्रतिष्ठा, नोकरी की व्यवसाय आणि राजयोग',
  },
  {
    key: 'wealth',
    icon: 'Coins',
    house: '2nd & 11th · द्वितीय/एकादश',
    color: '#15803D',
    enName: 'Wealth & Finance',
    hiName: 'धन एवं समृद्धि',
    mrName: 'धन आणि समृद्धी',
    enSub: 'Liquid savings, sudden gains, investment, and debt risk',
    hiSub: 'संचित धन, आकस्मिक लाभ, धनयोग एवं ऋण स्थिति',
    mrSub: 'संचित संपत्ती, अचानक धनलाभ, धनयोग आणि कर्ज निवारण',
  },
  {
    key: 'health',
    icon: 'Activity',
    house: '1st & 6th · लग्न/षष्ठ',
    color: '#DC2626',
    enName: 'Health & Longevity',
    hiName: 'स्वास्थ्य एवं दीर्घायु',
    mrName: 'आरोग्य आणि दीर्घायुष्य',
    enSub: 'Vitality, Ayurvedic dosha, sensitive periods, and recovery',
    hiSub: 'शारीरिक ओज, त्रिदोष प्रकृति, शल्यक्रिया विचार एवं आरोग्य काल',
    mrSub: 'शारीरिक ऊर्जा, आयुर्वेदिक प्रकृती, संवेदनशील काळ आणि आरोग्य',
  },
  {
    key: 'children',
    icon: 'Users',
    house: '5th House · पंचम भाव',
    color: '#9333EA',
    enName: 'Children & Progeny',
    hiName: 'संतान सुख एवं कुल',
    mrName: 'संतती आणि कुटुंब',
    enSub: 'Lineage blessings, nature of children, and Jupiter karaka',
    hiSub: 'संतान कारक गुरु, संतति योग, स्वभाव एवं पुत्र विचार',
    mrSub: 'संतती सुख, मुलांचा स्वभाव, गुरु कृपा आणि पूर्वपुण्याई',
  },
  {
    key: 'education',
    icon: 'GraduationCap',
    house: '4th & 5th · चतुर्थ/पंचम',
    color: '#0284C7',
    enName: 'Education & Intellect',
    hiName: 'विद्या एवं ज्ञान',
    mrName: 'उच्च शिक्षण आणि ज्ञान',
    enSub: 'Academic aptitude, competitive exams, Saraswati yogas',
    hiSub: 'उच्च शिक्षा, प्रतियोगी परीक्षा, सरस्वती योग एवं बुद्धिमत्ता',
    mrSub: 'उच्च शिक्षण, स्पर्धा परीक्षा, सरस्वती योग आणि बौद्धिक कौशल्य',
  },
  {
    key: 'property',
    icon: 'Home',
    house: '4th House · सुख भाव',
    color: '#EA580C',
    enName: 'Property & Vehicles',
    hiName: 'भूमि, भवन एवं वाहन',
    mrName: 'स्थावर संपत्ती व वास्तू',
    enSub: 'Real estate, vehicular comfort, domestic peace, and Vastu',
    hiSub: 'गृह संपत्ति, भूमि लाभ, वाहन सुख, वास्तु एवं मानसिक शांति',
    mrSub: 'घर, जमीन खरेदी, वाहन सौख्य, वास्तू आणि कौटुंबिक समाधान',
  },
  {
    key: 'challenges',
    icon: 'ShieldAlert',
    house: '6th, 8th & 12th · त्रिक भाव',
    color: '#D97706',
    enName: 'Challenges & Doshas',
    hiName: 'ग्रह दोष एवं बाधाएं',
    mrName: 'दोष आणि संकटे',
    enSub: 'Sade Sati, Kaal Sarp, Mangal, Pitru doshas, and mitigation',
    hiSub: 'साढ़ेसाती, कालसर्प, मांगलिक, पितृ दोष एवं निवारण',
    mrSub: 'साडेसाती, कालसर्प, मांगलिक, पितृ दोष आणि शांती उपाय',
  },
  {
    key: 'travel',
    icon: 'Plane',
    house: '9th & 12th · नवम/द्वादश',
    color: '#0D9488',
    enName: 'Travel & Relocation',
    hiName: 'विदेश यात्रा एवं प्रवास',
    mrName: 'परदेश गमन आणि प्रवास',
    enSub: 'Foreign settlement, visas, overseas career, and pilgrimages',
    hiSub: 'विदेश गमन, नागरिकता योग, तीर्थाटन एवं सुदूर प्रवास',
    mrSub: 'परदेशात स्थायिक होणे, व्हिसा, परदेशी नोकरी आणि तीर्थयात्रा',
  },
  {
    key: 'spirituality',
    icon: 'Flame',
    house: '9th & 12th · धर्म/मोक्ष',
    color: '#7C3AED',
    enName: 'Spirituality & Dharma',
    hiName: 'धर्म, मोक्ष एवं कर्म',
    mrName: 'धर्म आणि अध्यात्म',
    enSub: 'Spiritual evolution, Ishta Devata, Moksha yogas, and past karma',
    hiSub: 'इष्ट देव, मोक्ष योग, पूर्वजन्म संचित कर्म एवं साधना पथ',
    mrSub: 'इष्ट देवता, मोक्ष योग, पूर्वजन्मीचे कर्म आणि अध्यात्मिक प्रगती',
  },
];

export interface PredictionLocale {
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
  generateBtn: string;
  generatingBtn: string;
  sampleProfileBtn: string;
  generatePdfReportBtn: string;

  // Overview & Tabs
  overviewTitle: string;
  overviewSubtitle: string;
  allDomainsTitle: string;
  domainScoreLabel: string;
  dashaActiveBadge: string;
  dashaInactiveBadge: string;

  // Section Headers inside Domain Detail
  analysisTitle: string;
  keyIndicatorsTitle: string;
  timingTitle: string;
  timingSubtitle: string;
  bestWindowLabel: string;
  confidenceLabel: string;
  remediesTitle: string;
  gemstoneLabel: string;
  mantraLabel: string;
  fastLabel: string;
  donateLabel: string;
  ritualLabel: string;
  doshasFoundTitle: string;
  noDoshasTitle: string;
  summaryTitle: string;

  // Chat
  chatTitle: string;
  chatSubtitle: string;
  chatPlaceholder: string;
  sendBtn: string;
}

export const PREDICTION_TRANSLATIONS: Record<string, PredictionLocale> = {
  en: {
    badge: 'Authentic Vedic Life Assessment',
    title: '10 Life Domain Predictions & Planetary Guidance',
    subtitle: 'Comprehensive Parashari synthesis evaluating house lords, Vimshottari dasha triggers, planetary transits (Gochara), and time-tested remedies across all 10 life dimensions.',
    inputCardTitle: 'Enter Birth Details',
    inputCardSubtitle: 'Provide accurate birth information to analyze all 10 Vedic life domains',
    fullNameLabel: 'Full Name',
    fullNamePlaceholder: 'e.g. Arjun Sharma',
    dobLabel: 'Date of Birth',
    tobLabel: 'Time of Birth (IST)',
    cityLabel: 'Birth City',
    cityPlaceholder: 'Search city (e.g. Delhi, Pune)',
    generateBtn: 'Analyze All 10 Domains',
    generatingBtn: 'Computing Cosmic Transits & Periods...',
    sampleProfileBtn: 'Use Sample Chart',
    generatePdfReportBtn: 'Generate PDF Report',

    overviewTitle: 'Cosmic Life Dimensions Matrix',
    overviewSubtitle: 'Click on any life domain card to reveal detailed astrological evaluations, timing windows, and specific Vedic remedies.',
    allDomainsTitle: 'All 10 Life Domains',
    domainScoreLabel: 'Domain Strength',
    dashaActiveBadge: 'Dasha Active',
    dashaInactiveBadge: 'Baseline',

    analysisTitle: 'Classical Astrological Assessment',
    keyIndicatorsTitle: 'Astrological Pillars & Indicators',
    timingTitle: 'Event Timing Windows & Gochara',
    timingSubtitle: 'Parashari dasha alignments cross-referenced with Jupiter & Saturn transits',
    bestWindowLabel: 'Peak Timing Window',
    confidenceLabel: 'Confidence Level',
    remediesTitle: 'Classical Vedic Remedies',
    gemstoneLabel: 'Prescribed Gemstone',
    mantraLabel: 'Beej Mantra',
    fastLabel: 'Fasting Day',
    donateLabel: 'Sacred Charity',
    ritualLabel: 'Remedial Ritual',
    doshasFoundTitle: 'Active Doshas & Mitigations',
    noDoshasTitle: 'No critical afflictions detected in this domain',
    summaryTitle: 'Domain Summary',

    chatTitle: 'Consult AstroLogic on Life Domains',
    chatSubtitle: 'Ask specialized questions about career promotions, marriage periods, or health cycles',
    chatPlaceholder: 'Ask about career timing, marriage prospects, or remedies...',
    sendBtn: 'Ask AI',
  },
  hi: {
    badge: 'प्रामाणिक वैदिक जीवन विश्लेषण',
    title: '१० जीवन आयाम फलादेश एवं ग्रहीय मार्गदर्शन',
    subtitle: 'महर्षि पराशर परंपरा के अनुसार भाव स्वामियों, विंशोत्तरी दशा काल, ग्रह गोचर एवं शास्त्रीय उपायों का सम्पूर्ण १० जीवन क्षेत्रों में गहन विवेचन।',
    inputCardTitle: 'जन्म विवरण प्रविष्ट करें',
    inputCardSubtitle: 'समस्त १० जीवन क्षेत्रों के फलित विश्लेषण हेतु जन्म विवरण दर्ज करें',
    fullNameLabel: 'पूरा नाम',
    fullNamePlaceholder: 'उदा. अर्जुन शर्मा',
    dobLabel: 'जन्म तिथि',
    tobLabel: 'जन्म समय (IST)',
    cityLabel: 'जन्म स्थान / नगर',
    cityPlaceholder: 'नगर खोजें (उदा. दिल्ली, मुंबई, जयपुर)',
    generateBtn: '१० जीवन क्षेत्रों का विश्लेषण करें',
    generatingBtn: 'दशा एवं गोचर की खगोलीय गणना जारी है...',
    sampleProfileBtn: 'नमूना पत्रिका प्रयोग करें',
    generatePdfReportBtn: 'PDF रिपोर्ट बनाएं',

    overviewTitle: 'जीवन क्षेत्र सामर्थ्य चक्र',
    overviewSubtitle: 'विस्तृत शास्त्रीय फलित, फलित समय (गोचर) एवं वैदिक उपाय जानने के लिए किसी भी जीवन क्षेत्र पर क्लिक करें।',
    allDomainsTitle: 'सम्पूर्ण १० जीवन क्षेत्र',
    domainScoreLabel: 'क्षेत्र सामर्थ्य',
    dashaActiveBadge: 'सक्रिय दशा',
    dashaInactiveBadge: 'सामान्य',

    analysisTitle: 'शास्त्रीय फलित विवेचना',
    keyIndicatorsTitle: 'ग्रहीय आधार एवं कारकत्व',
    timingTitle: 'गोचर एवं अनुकूल समय चक्र',
    timingSubtitle: 'विंशोत्तरी दशा एवं गुरु-शनि गोचर पर आधारित शुभ समय',
    bestWindowLabel: 'श्रेष्ठ फलदायक समय',
    confidenceLabel: 'विश्वास स्तर',
    remediesTitle: 'शास्त्रीय वैदिक उपाय',
    gemstoneLabel: 'उपयुक्त रत्न',
    mantraLabel: 'बीज मंत्र',
    fastLabel: 'व्रत दिन',
    donateLabel: 'दान संकल्प',
    ritualLabel: 'शांति विधान',
    doshasFoundTitle: 'सक्रिय दोष एवं निवारण',
    noDoshasTitle: 'इस जीवन क्षेत्र में कोई गंभीर दोष नहीं है',
    summaryTitle: 'क्षेत्र सारांश',

    chatTitle: 'जीवन फलादेश संबंधी प्रश्न पूछें',
    chatSubtitle: 'विवाह मुहूर्त, पदोन्नति समय या ग्रहीय शांति उपायों के विषय में मार्गदर्शन पाएं',
    chatPlaceholder: 'करियर, विवाह समय या उपायों के विषय में पूछें...',
    sendBtn: 'उत्तर पाएं',
  },
  mr: {
    badge: 'प्रमाणित वैदिक जीवन विश्लेषण',
    title: '१० जीवन पैलू भविष्य आणि ग्रहीय मार्गदर्शन',
    subtitle: 'महर्षी पराशर परंपरेवर आधारित भावेश स्थिती, विंशोत्तरी महादशा, चालू ग्रह गोचर आणि शास्त्रीय उपायांचे सर्व १० जीवन अंगांमधील सखोल फलादेश.',
    inputCardTitle: 'जन्म तपशील प्रविष्ट करा',
    inputCardSubtitle: 'सर्व १० जीवन पैलूंचे सखोल विश्लेषण करण्यासाठी अचूक माहिती प्रविष्ट करा',
    fullNameLabel: 'पूर्ण नाव',
    fullNamePlaceholder: 'उदा. अर्जुन शर्मा',
    dobLabel: 'जन्म तारीख',
    tobLabel: 'जन्म वेळ (IST)',
    cityLabel: 'जन्म शहर',
    cityPlaceholder: 'शहर शोधा (उदा. पुणे, मुंबई, नागपूर)',
    generateBtn: 'सर्व १० जीवन पैलूंचे विश्लेषण करा',
    generatingBtn: 'दशा आणि गोचर चक्राची अचूक गणना सुरू आहे...',
    sampleProfileBtn: 'नमुना पत्रिका वापरा',
    generatePdfReportBtn: 'PDF अहवाल तयार करा',

    overviewTitle: 'जीवन पैलू सामर्थ्य चक्र',
    overviewSubtitle: 'सविस्तर शास्त्रीय विश्लेषण, अनुकूल काळ (गोचर) आणि वैदिक उपाय पाहण्यासाठी कोणत्याही घटकावर क्लिक करा.',
    allDomainsTitle: 'सर्व १० जीवन पैलू',
    domainScoreLabel: 'पैलू सामर्थ्य',
    dashaActiveBadge: 'दशा सक्रिय',
    dashaInactiveBadge: 'साधारण',

    analysisTitle: 'शास्त्रीय वैदिक फलादेश',
    keyIndicatorsTitle: 'ग्रहीय आधार आणि कारकत्व',
    timingTitle: 'गोचर आणि अनुकूल कालखंड',
    timingSubtitle: 'विंशोत्तरी दशा आणि गुरू-शनी गोचरावर आधारित शुभ काळ',
    bestWindowLabel: 'सर्वात अनुकूल काळ',
    confidenceLabel: 'अचूकता पातळी',
    remediesTitle: 'शास्त्रीय वैदिक उपाय',
    gemstoneLabel: 'शिफारस केलेले रत्न',
    mantraLabel: 'बीज मंत्र',
    fastLabel: 'उपवासाचा वार',
    donateLabel: 'दान वस्तू',
    ritualLabel: 'शांती विधी',
    doshasFoundTitle: 'सक्रिय ग्रह दोष आणि निवारण',
    noDoshasTitle: 'या घटकात कोणताही गंभीर दोष आढळला नाही',
    summaryTitle: 'पैलू सारांश',

    chatTitle: 'जीवन भविष्य संदर्भात थेट विचारा',
    chatSubtitle: 'नोकरीतील प्रगती, विवाह काळ किंवा ग्रहीय उपायांविषयी मार्गदर्शक उत्तरे मिळवा',
    chatPlaceholder: 'कारकीर्द, विवाह काळ किंवा वैदिक उपायांविषयी विचारा...',
    sendBtn: 'उत्तर मिळवा',
  },
};

