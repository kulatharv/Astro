'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Search, Compass, BookOpen, Clock, User, Tag, Sparkles, ArrowRight, Layers } from 'lucide-react';
import { Link } from '@/i18n/routing';
import { SupportedLocale, BLOG_CATEGORIES, BLOG_TRANSLATIONS } from './blogLocalization';

export interface BlogPostItem {
  id: number;
  title: string;
  slug: string;
  content: string;
  summary?: string;
  language: string;
  tags?: string[];
  author?: string;
  created_at?: string;
}

const FALLBACK_BLOGS: Record<SupportedLocale, BlogPostItem[]> = {
  en: [
    {
      id: 1,
      title: 'Understanding the 9 Planets (Navagrahas) in Vedic Astrology',
      slug: 'understanding-the-9-planets-in-vedic-astrology',
      summary: 'The nine celestial bodies govern every domain of human existence, shaping destiny, personality, and karmic lessons.',
      content: 'In classical Vedic Jyotish, the nine cosmic bodies are living archetypes of cosmic consciousness...',
      language: 'en',
      tags: ['Planets', 'Navagrahas', 'Philosophy'],
      author: 'Acharya Shastri',
      created_at: '2026-04-20T00:00:00Z',
    },
    {
      id: 2,
      title: 'What is Vimshottari Dasha and Why It Governs Life Timing',
      slug: 'vimshottari-dasha-complete-guide',
      summary: 'The 120-year Vimshottari cycle is the crown jewel of predictive Jyotish, explaining why events unfold precisely when they do.',
      content: 'Have you ever wondered why life moves in distinct chapters — periods of boundless expansion...',
      language: 'en',
      tags: ['Dasha', 'Timing', 'Vedic Wisdom'],
      author: 'Dr. Ramananda',
      created_at: '2026-04-15T00:00:00Z',
    },
    {
      id: 3,
      title: 'Raj Yoga: The Celestial Combinations for Power and Success',
      slug: 'raj-yoga-power-authority-success',
      summary: 'How kendra and trikona house lord unions elevate individuals to extraordinary leadership, respect, and influence.',
      content: 'In classical Jyotish, the term Raj Yoga denotes planetary combinations that bestow power...',
      language: 'en',
      tags: ['Yogas', 'Kundali', 'Success'],
      author: 'Pt. Devadatta',
      created_at: '2026-04-10T00:00:00Z',
    },
    {
      id: 4,
      title: 'Saturn Sade Sati: Dispelling Myths & Embracing Karmic Growth',
      slug: 'saturn-sade-sati-guide',
      summary: 'Why the 7.5-year transit of Saturn over your natal Moon is an alchemical forge for character and resilience.',
      content: 'Few concepts in Indian astrology evoke as much unwarranted anxiety as Sade Sati...',
      language: 'en',
      tags: ['Planets', 'Remedies', 'Shani'],
      author: 'Acharya Shastri',
      created_at: '2026-04-05T00:00:00Z',
    },
  ],
  hi: [
    {
      id: 5,
      title: 'वैदिक ज्योतिष में नौ ग्रहों (नवग्रह) का प्रभाव और महत्व',
      slug: 'navagraha-parichay-vedic-jyotish',
      summary: 'नवग्रह मानव जीवन के प्रत्येक अंग को प्रभावित करते हैं — जानिए उनके शास्त्रीय गुणधर्म और जीवन पर पड़ने वाले प्रभाव।',
      content: 'वैदिक ज्योतिष में नवग्रह केवल खगोलीय पिंड नहीं, बल्कि ईश्वरीय चेतना के संवाहक हैं...',
      language: 'hi',
      tags: ['ग्रह', 'नवग्रह', 'वैदिक ज्ञान'],
      author: 'पं. देवदत्त',
      created_at: '2026-04-18T00:00:00Z',
    },
    {
      id: 6,
      title: 'शनि की साढ़ेसाती: भय नहीं, आत्म-विकास और शास्त्रीय उपाय',
      slug: 'sade-sati-vastavikta-aur-upay',
      summary: 'साढ़ेसाती से डरने की नहीं, बल्कि जीवन में अनुशासन और सत्यनिष्ठा लाने की आवश्यकता है।',
      content: 'शनिदेव को कर्मफलदाता कहा गया है...',
      language: 'hi',
      tags: ['शनि', 'उपाय', 'साढ़ेसाती'],
      author: 'आचार्य शास्त्री',
      created_at: '2026-04-12T00:00:00Z',
    },
  ],
  mr: [
    {
      id: 7,
      title: 'वैदिक ज्योतिषशास्त्रातील नवग्रह आणि त्यांचे मानवी जीवनावरील प्रभाव',
      slug: 'vedic-jyotishatil-navagraha-mahatva',
      summary: 'सूर्य, चंद्र, मंगळ ते राहू-केतू या नवग्रहांची वैशिष्ट्ये आणि मानवी जीवनातील त्यांची भूमिका समजून घ्या.',
      content: 'भारतीय संस्कृतीत आणि वैदिक ज्योतिषशास्त्रात नवग्रहांना अत्यंत पूज्य स्थान आहे...',
      language: 'mr',
      tags: ['ग्रह', 'नवग्रह', 'ज्योतिष'],
      author: 'पंडित देवदत्त',
      created_at: '2026-04-18T00:00:00Z',
    },
    {
      id: 8,
      title: 'शनीची साडेसाती: भीती नव्हे, कर्मशुद्धी आणि प्रभावी वैदिक उपाय',
      slug: 'shani-sadesati-vastav-ani-upay',
      summary: 'साडेसाती हा कालावधी व्यक्तीला परिपक्व आणि स्वावलंबी बनवणारा ठरतो — शास्त्रीय दृष्टिकोन व उपाय.',
      content: 'शनीची साडेसाती म्हणजे चंद्र राशीच्या आधीच्या, त्याच आणि पुढच्या राशीतील साडेसात वर्षांचा प्रवास...',
      language: 'mr',
      tags: ['शनी', 'उपाय', 'साडेसाती'],
      author: 'आचार्य शास्त्री',
      created_at: '2026-04-12T00:00:00Z',
    },
  ],
};

interface BlogListModuleProps {
  locale: string;
}

export default function BlogListModule({ locale }: BlogListModuleProps) {
  const activeLocale = (['en', 'hi', 'mr'].includes(locale) ? locale : 'en') as SupportedLocale;
  const categories = BLOG_CATEGORIES[activeLocale];
  const t = BLOG_TRANSLATIONS[activeLocale];

  const [articles, setArticles] = useState<BlogPostItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    async function loadBlogs() {
      setLoading(true);
      try {
        const res = await fetch(`/api/blogs?lang=${activeLocale}&limit=50`);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setArticles(data);
            return;
          }
        }
        // Fallback to localized seeds
        setArticles(FALLBACK_BLOGS[activeLocale] || FALLBACK_BLOGS.en);
      } catch (err) {
        setArticles(FALLBACK_BLOGS[activeLocale] || FALLBACK_BLOGS.en);
      } finally {
        setLoading(false);
      }
    }
    loadBlogs();
  }, [activeLocale]);

  // Filter articles based on active category and search
  const filteredArticles = useMemo(() => {
    return articles.filter((post) => {
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !q ||
        post.title.toLowerCase().includes(q) ||
        (post.summary && post.summary.toLowerCase().includes(q)) ||
        (post.tags && post.tags.some((tg) => tg.toLowerCase().includes(q)));

      const matchesCat =
        activeCategory === 'all' ||
        (post.tags &&
          post.tags.some(
            (tg) =>
              tg.toLowerCase().includes(activeCategory.toLowerCase()) ||
              activeCategory.toLowerCase().includes(tg.toLowerCase())
          ));

      return matchesSearch && matchesCat;
    });
  }, [articles, searchQuery, activeCategory]);

  const featuredArticle = filteredArticles[0];
  const restArticles = filteredArticles.slice(1);

  return (
    <div className="space-y-8">
      {/* ── Page Hero ── */}
      <div className="text-center space-y-3 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#821C17]/10 border border-[#821C17]/25 text-[#821C17] text-xs font-semibold tracking-wider uppercase">
          <BookOpen className="w-3.5 h-3.5 text-[#C46B1E]" />
          <span>{t.badge}</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#421A10] tracking-tight">
          {t.title}
        </h1>
        {/* Centerline Ornament */}
        <div className="flex items-center justify-center gap-3 py-1">
          <span className="h-px w-14 bg-linear-to-r from-transparent to-[#E49D4B]" />
          <span className="w-2 h-2 rotate-45 bg-[#821C17]" />
          <span className="h-px w-14 bg-linear-to-l from-transparent to-[#E49D4B]" />
        </div>
        <p className="text-sm sm:text-base text-[#421A10]/75 leading-relaxed">
          {t.subtitle}
        </p>
      </div>

      {/* ── Search & Category Filter Ribbon ── */}
      <div className="space-y-4">
        {/* Search Bar */}
        <div className="max-w-2xl mx-auto relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#C46B1E]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t.searchPlaceholder}
            className="w-full pl-11 pr-4 py-3 text-sm rounded-2xl bg-[#FDF5E6] border border-[#F9DAB5] text-[#421A10] placeholder-[#421A10]/40 shadow-xs focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 transition-all"
          />
        </div>

        {/* Category Pills */}
        <div className="flex items-center justify-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
          {categories.map((cat) => {
            const isActive = activeCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap border ${
                  isActive
                    ? 'bg-[#7A1612] text-[#FAF6F0] border-[#C5A059] shadow-xs'
                    : 'bg-[#FFFFFF] text-[#24120B] border-[#EADBC8] hover:bg-[#F5EFE6]'
                }`}
              >
                <span>{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Main Articles Content Area ── */}
      {loading ? (
        <div className="p-12 text-center rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/30">
          <Compass className="w-6 h-6 animate-spin text-[#7A1612] mx-auto mb-2" />
          <p className="text-sm font-serif text-[#24120B]">{t.loading}</p>
        </div>
      ) : filteredArticles.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/30 space-y-3">
          <span className="text-3xl">📭</span>
          <p className="text-base font-serif font-bold text-[#7A1612]">
            {t.noArticlesFound}
          </p>
          <button
            onClick={() => {
              setActiveCategory('all');
              setSearchQuery('');
            }}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl bg-[#FAF6F0] border border-[#C5A059]/40 text-[#7A1612] hover:bg-[#FAF6F0]/80 transition-colors cursor-pointer"
          >
            <span>{t.clearFilters}</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ── Left Column: Articles List (2 Spans) ── */}
          <div className="lg:col-span-2 space-y-6">
            {/* Featured Article Hero Card */}
            {featuredArticle && (
              <Link
                href={`/blogs/${featuredArticle.slug || featuredArticle.id}`}
                className="group block p-7 sm:p-8 rounded-3xl bg-linear-to-br from-[#7A1612] via-[#5A0E0A] to-[#24120B] text-[#FAF6F0] shadow-md border border-[#C5A059]/40 hover:border-[#C5A059]/80 hover:shadow-xl transition-all duration-300 relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                  <Sparkles className="w-48 h-48 text-[#C5A059]" />
                </div>
                <div className="relative space-y-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#C5A059]/20 border border-[#C5A059]/40 text-[#C5A059] text-xs font-semibold uppercase tracking-wider">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{t.featuredTag}</span>
                  </div>
                  <h2 className="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-[#FAF6F0] group-hover:text-[#C5A059] transition-colors">
                    {featuredArticle.title}
                  </h2>
                  <p className="text-sm sm:text-base text-[#FAF6F0]/85 leading-relaxed line-clamp-3">
                    {featuredArticle.summary || featuredArticle.content.slice(0, 180)}…
                  </p>
                  <div className="flex flex-wrap items-center gap-4 text-xs text-[#FAF6F0]/75 pt-2 border-t border-[#FAF6F0]/15">
                    {featuredArticle.author && (
                      <span className="flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5 text-[#C5A059]" />
                        <span>{featuredArticle.author}</span>
                      </span>
                    )}
                    <span className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-[#C5A059]" />
                      <span>{Math.ceil((featuredArticle.content.length || 1000) / 900)} {t.minRead}</span>
                    </span>
                    <span className="ml-auto inline-flex items-center gap-1 text-[#C5A059] font-semibold group-hover:translate-x-1 transition-transform">
                      <span>{t.readArticleBtn}</span>
                    </span>
                  </div>
                </div>
              </Link>
            )}

            {/* Grid of Remaining Articles */}
            {restArticles.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {restArticles.map((post) => (
                  <Link
                    key={post.id || post.slug}
                    href={`/blogs/${post.slug || post.id}`}
                    className="group flex flex-col justify-between p-6 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 hover:border-[#7A1612]/60 shadow-xs hover:shadow-md transition-all duration-200"
                  >
                    <div className="space-y-2.5">
                      {post.tags && post.tags.length > 0 && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-wider text-[#C5A059]">
                          <Tag className="w-3 h-3" />
                          <span>{post.tags[0]}</span>
                        </span>
                      )}
                      <h3 className="font-serif text-lg font-bold text-[#24120B] group-hover:text-[#7A1612] transition-colors line-clamp-2">
                        {post.title}
                      </h3>
                      <p className="text-xs sm:text-sm text-[#24120B]/75 leading-relaxed line-clamp-3">
                        {post.summary || post.content.slice(0, 140)}…
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-xs text-[#24120B]/60 pt-4 mt-4 border-t border-[#C5A059]/20">
                      <span>{post.author || 'Astro AI'}</span>
                      <span className="text-[#7A1612] font-bold inline-flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                        <span>Read</span>
                        <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* ── Right Column: Topic Directory & Glossary Sidebar ── */}
          <div className="space-y-6">
            {/* Topic Navigation Card */}
            <div className="p-6 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-xs space-y-4">
              <div className="flex items-center gap-2 pb-3 border-b border-[#C5A059]/25">
                <Layers className="w-4 h-4 text-[#7A1612]" />
                <h3 className="font-serif text-base font-bold text-[#7A1612]">
                  {t.popularTopics}
                </h3>
              </div>
              <div className="space-y-1.5">
                {categories.slice(1).map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium text-[#24120B] hover:bg-[#FAF6F0] hover:text-[#7A1612] transition-colors cursor-pointer text-left"
                  >
                    <span className="flex items-center gap-2">
                      <span>{cat.icon}</span>
                      <span>{cat.label}</span>
                    </span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#C5A059]" />
                  </button>
                ))}
              </div>
            </div>

            {/* Cosmic Wisdom Note Card */}
            <div className="p-6 rounded-2xl bg-linear-to-br from-[#FAF6F0] to-[#FFFFFF] border border-[#C5A059]/35 shadow-xs space-y-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#7A1612]" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#7A1612]">
                  {t.glossaryTitle}
                </h4>
              </div>
              <p className="text-xs leading-relaxed text-[#24120B]/80 font-serif">
                {t.glossaryText}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

