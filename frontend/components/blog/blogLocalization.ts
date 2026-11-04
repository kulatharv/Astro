export type SupportedLocale = 'en' | 'hi' | 'mr';

export interface BlogCategory {
  id: string;
  label: string;
  icon: string;
}

export const BLOG_CATEGORIES: Record<SupportedLocale, BlogCategory[]> = {
  en: [
    { id: 'all', label: 'All Articles', icon: '✦' },
    { id: 'planets', label: 'Planets & Grahas', icon: '🪐' },
    { id: 'yogas', label: 'Yogas & Doshas', icon: '✨' },
    { id: 'dasha', label: 'Dasha & Timing', icon: '⏱' },
    { id: 'nakshatra', label: '27 Nakshatras', icon: '⭐' },
    { id: 'remedies', label: 'Vedic Remedies', icon: '🙏' },
    { id: 'philosophy', label: 'Jyotish Philosophy', icon: '📜' },
  ],
  hi: [
    { id: 'all', label: 'सभी लेख', icon: '✦' },
    { id: 'planets', label: 'ग्रह एवं नवग्रह', icon: '🪐' },
    { id: 'yogas', label: 'योग एवं दोष', icon: '✨' },
    { id: 'dasha', label: 'दशा एवं काल गणना', icon: '⏱' },
    { id: 'nakshatra', label: '२७ नक्षत्र', icon: '⭐' },
    { id: 'remedies', label: 'शास्त्रीय उपाय', icon: '🙏' },
    { id: 'philosophy', label: 'वैदिक दर्शन', icon: '📜' },
  ],
  mr: [
    { id: 'all', label: 'सर्व लेख', icon: '✦' },
    { id: 'planets', label: 'ग्रह आणि नवग्रह', icon: '🪐' },
    { id: 'yogas', label: 'योग आणि दोष', icon: '✨' },
    { id: 'dasha', label: 'दशा आणि कालनिर्णय', icon: '⏱' },
    { id: 'nakshatra', label: '२७ नक्षत्रे', icon: '⭐' },
    { id: 'remedies', label: 'वैदिक उपाय', icon: '🙏' },
    { id: 'philosophy', label: 'ज्योतिष तत्त्वज्ञान', icon: '📜' },
  ],
};

export const BLOG_TRANSLATIONS = {
  en: {
    badge: 'Vedic Knowledge & Jyotish Articles',
    title: 'Astrology Articles & Cosmic Insights',
    subtitle: 'Timeless principles of classical Indian astronomy, predictive timing, planetary archetypes, and remedial practices.',
    searchPlaceholder: 'Search articles by planet, yoga, dasha, or topic…',
    featuredTag: 'Featured Cosmic Dossier',
    readArticleBtn: 'Read Article →',
    minRead: 'min read',
    publishedOn: 'Published on',
    writtenBy: 'By',
    noArticlesFound: 'No articles match your search or selected filter.',
    clearFilters: 'Reset filters',
    backToArticles: '← Back to All Articles',
    relatedArticles: 'Related Vedic Articles',
    popularTopics: 'Explore Jyotish Topics',
    glossaryTitle: 'Cosmic Wisdom Note',
    glossaryText: 'Classical Jyotish treats planets as indicators (Karaka) of karmic fruition, guiding human consciousness toward self-mastery and inner peace.',
    loading: 'Loading Vedic articles…',
  },
  hi: {
    badge: 'वैदिक ज्ञान एवं ज्योतिषीय आलेख',
    title: 'ज्योतिष लेख एवं आकाशीय रहस्य',
    subtitle: 'भारतीय ज्योतिष के मूलभूत सिद्धांत, काल गणना, नवग्रहों का प्रभाव और जीवनोपयोगी शास्त्रीय उपाय।',
    searchPlaceholder: 'ग्रह, योग, दशा या विषय से लेख खोजें…',
    featuredTag: 'प्रमुख वैदिक आलेख',
    readArticleBtn: 'पूरा लेख पढ़ें →',
    minRead: 'मिनट पठन',
    publishedOn: 'प्रकाशित',
    writtenBy: 'लेखक',
    noArticlesFound: 'आपकी खोज या चुने गए विषय से संबंधित कोई लेख नहीं मिला।',
    clearFilters: 'फ़िल्टर हटाएं',
    backToArticles: '← सभी लेखों पर वापस जाएं',
    relatedArticles: 'संबंधित वैदिक लेख',
    popularTopics: 'प्रमुख ज्योतिष विषय',
    glossaryTitle: 'वैदिक ज्ञान सार',
    glossaryText: 'वैदिक ज्योतिष में ग्रह पूर्वजन्म के संचित कर्मों के निर्देशक (कारक) हैं। शास्त्र का उद्देश्य भय नहीं, बल्कि विवेक और आत्म-कल्याण है।',
    loading: 'लेख लोड हो रहे हैं…',
  },
  mr: {
    badge: 'वैदिक ज्ञान आणि ज्योतिषीय लेख',
    title: 'ज्योतिष शास्त्र लेख आणि खगोलीय रहस्ये',
    subtitle: 'प्राचीन भारतीय खगोलशास्त्र, दशा विचार, नवग्रहांचे प्रभाव आणि शास्त्रीय वैदिक उपायांचे सखोल मार्गदर्शन.',
    searchPlaceholder: 'ग्रह, योग, दशा किंवा विषयानुसार शोधा…',
    featuredTag: 'विशेष वैदिक आलेख',
    readArticleBtn: 'संपूर्ण लेख वाचा →',
    minRead: 'मिनिट वाचन',
    publishedOn: 'दिनांक',
    writtenBy: 'लेखक',
    noArticlesFound: 'आपल्या शोधाशी किंवा निवडलेल्या विषयाशी जुळणारे लेख उपलब्ध नाहीत.',
    clearFilters: 'फिल्टर काढा',
    backToArticles: '← सर्व लेखांकडे परत या',
    relatedArticles: 'संबंधित वैदिक लेख',
    popularTopics: 'प्रमुख ज्योतिष विषय',
    glossaryTitle: 'वैदिक ज्ञान संदेश',
    glossaryText: 'ज्योतिषशास्त्र हे कर्म आणि काळाचे शास्त्र आहे. ग्रह हे केवळ सूचना देतात, पुरुषार्थ आणि संयमाने आपण आपल्या जीवनाला योग्य दिशा देऊ शकतो.',
    loading: 'लेख लोड होत आहेत…',
  },
};

