'use client';

import { useTranslations } from 'next-intl';
import { BookOpen, Scroll, Compass, Heart, ArrowUpRight, ArrowRight } from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function KnowledgeSection() {
  const t = useTranslations('knowledge');

  const articles = [
    {
      title: t('article1Title'),
      tag: t('article1Tag'),
      desc: t('article1Desc'),
      icon: Scroll,
      readTime: '6 min read',
    },
    {
      title: t('article2Title'),
      tag: t('article2Tag'),
      desc: t('article2Desc'),
      icon: Compass,
      readTime: '8 min read',
    },
    {
      title: t('article3Title'),
      tag: t('article3Tag'),
      desc: t('article3Desc'),
      icon: BookOpen,
      readTime: '5 min read',
    },
    {
      title: t('article4Title'),
      tag: t('article4Tag'),
      desc: t('article4Desc'),
      icon: Heart,
      readTime: '7 min read',
    },
  ];

  return (
    <section id="knowledge" className="py-24 bg-[#FAF6F0] relative scroll-mt-16 border-t border-[#C5A059]/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#7A1612]/10 border border-[#7A1612]/20 text-[#7A1612] text-xs font-semibold tracking-wider uppercase">
            <BookOpen className="w-3.5 h-3.5 text-[#C5A059]" />
            <span>{t('eyebrow')}</span>
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#24120B] tracking-tight">
            {t('title')}
          </h2>
          {/* Ornamental Divider */}
          <div className="flex items-center justify-center gap-3 py-1">
            <span className="h-px w-12 bg-linear-to-r from-transparent to-[#C5A059]" />
            <span className="w-2 h-2 rotate-45 bg-[#7A1612]" />
            <span className="h-px w-12 bg-linear-to-l from-transparent to-[#C5A059]" />
          </div>
          <p className="text-base text-[#24120B]/75 leading-relaxed">
            {t('subtitle')}
          </p>
        </div>

        {/* Articles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {articles.map((item, idx) => {
            const Icon = item.icon;
            return (
              <Link
                key={idx}
                href="/blogs"
                className="bg-[#FFFFFF] rounded-2xl p-8 border border-[#C5A059]/35 hover:border-[#7A1612]/60 shadow-xs hover:shadow-xl transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between group cursor-pointer"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-[11px] font-mono font-medium px-2.5 py-1 rounded-full bg-[#FAF6F0] border border-[#C5A059]/30 text-[#7A1612]">
                      {item.tag}
                    </span>
                    <span className="text-xs text-[#24120B]/70">{item.readTime}</span>
                  </div>

                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-[#FAF6F0] border border-[#C5A059]/30 flex items-center justify-center text-[#7A1612] shrink-0 group-hover:bg-[#7A1612] group-hover:text-[#FAF6F0] transition-colors">
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-serif text-xl font-bold text-[#24120B] group-hover:text-[#7A1612] transition-colors leading-snug">
                      {item.title}
                    </h3>
                  </div>

                  <p className="text-sm text-[#24120B]/75 leading-relaxed pl-14">
                    {item.desc}
                  </p>
                </div>

                <div className="pt-6 mt-6 border-t border-[#C5A059]/25 flex items-center justify-between text-xs font-bold uppercase tracking-wider text-[#7A1612] group-hover:text-[#24120B]">
                  <span>Read Treatise</span>
                  <ArrowUpRight className="w-4 h-4 text-[#C5A059] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </div>
              </Link>
            );
          })}
        </div>

        {/* View All Treatises CTA Banner */}
        <div className="mt-12 text-center">
          <Link
            href="/blogs"
            className="inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl text-xs font-bold uppercase tracking-wider text-[#FAF6F0] bg-linear-to-r from-[#7A1612] to-[#5A0E0A] hover:brightness-110 border border-[#C5A059]/40 shadow-md hover:shadow-lg transition-all group"
          >
            <BookOpen className="w-4 h-4 text-[#C5A059]" />
            <span>Browse Complete Vedic Treatises Library</span>
            <ArrowRight className="w-4 h-4 text-[#C5A059] group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
    </section>
  );
}
