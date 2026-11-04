'use client';

import { useTranslations } from 'next-intl';
import {
  Compass,
  Sparkles,
  Calendar,
  Globe2,
  Clock,
  BookOpen,
  ArrowRight,
} from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function ServicesSection() {
  const t = useTranslations('services');

  const services = [
    {
      id: 'kundali',
      title: t('kundaliTitle'),
      desc: t('kundaliDesc'),
      icon: Compass,
      route: '/kundali' as const,
      tag: 'D-1 & D-9',
    },
    {
      id: 'predictions',
      title: t('predictionsTitle'),
      desc: t('predictionsDesc'),
      icon: Sparkles,
      route: '/predictions' as const,
      tag: '10 Domains',
    },
    {
      id: 'panchang',
      title: t('panchangTitle'),
      desc: t('panchangDesc'),
      icon: Calendar,
      route: '/panchang' as const,
      tag: 'Daily Timings',
    },
    {
      id: 'horoscope',
      title: 'Daily Horoscope (दैनिक राशिफल)',
      desc: 'Real-time transit calculations, dignity scores, and auspicious coordinates for all 12 zodiac signs.',
      icon: Globe2,
      route: '/horoscope' as const,
      tag: '12 Rashis',
    },
    {
      id: 'dasha',
      title: t('dashaTitle'),
      desc: t('dashaDesc'),
      icon: Clock,
      route: '/predictions' as const,
      tag: 'Vimshottari',
    },
    {
      id: 'knowledge',
      title: 'Vedic Treatises & Articles (वैदिक ज्ञान)',
      desc: 'Explore classical texts, Parashara principles, Navagrahas, and authentic karmic remedies.',
      icon: BookOpen,
      route: '/blogs' as const,
      tag: 'Scriptural Wisdom',
    },
  ];

  return (
    <section id="services" className="py-24 bg-[#FCEBD2]/40 relative scroll-mt-16 border-t border-[#F9DAB5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#821C17]/10 border border-[#821C17]/25 text-[#821C17] text-xs font-semibold tracking-wider uppercase">
            <span>{t('eyebrow')}</span>
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#421A10] tracking-tight">
            {t('title')}
          </h2>
          {/* Ornamental Divider */}
          <div className="flex items-center justify-center gap-3 py-1">
            <span className="h-px w-12 bg-linear-to-r from-transparent to-[#E49D4B]" />
            <span className="w-2 h-2 rotate-45 bg-[#821C17]" />
            <span className="h-px w-12 bg-linear-to-l from-transparent to-[#E49D4B]" />
          </div>
          <p className="text-base text-[#421A10]/75 leading-relaxed">
            {t('subtitle')}
          </p>
        </div>

        {/* 6 Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.id}
                className="bg-[#FDF5E6] rounded-xl p-8 border border-[#F9DAB5] hover:border-[#821C17] shadow-xs hover:shadow-xl transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <div className="w-12 h-12 rounded-lg bg-[#FCEBD2] border border-[#F9DAB5] flex items-center justify-center text-[#821C17] group-hover:bg-[#821C17] group-hover:text-[#FDF5E6] transition-colors duration-300 shadow-xs">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[11px] font-mono font-medium px-2.5 py-1 rounded-full bg-[#E49D4B]/15 border border-[#E49D4B]/30 text-[#821C17]">
                      {item.tag}
                    </span>
                  </div>

                  <h3 className="font-serif text-xl font-bold text-[#421A10] mb-3 group-hover:text-[#821C17] transition-colors">
                    {item.title}
                  </h3>

                  <p className="text-sm text-[#421A10]/75 leading-relaxed mb-6">
                    {item.desc}
                  </p>
                </div>

                <Link
                  href={item.route}
                  className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#821C17] hover:text-[#421A10] pt-4 border-t border-[#F9DAB5] group-hover:translate-x-1 transition-transform"
                >
                  <span>{t('exploreService')}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-[#C46B1E]" />
                </Link>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
