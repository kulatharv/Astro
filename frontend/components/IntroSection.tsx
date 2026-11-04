'use client';

import { useTranslations } from 'next-intl';
import { BookOpen, Compass, HeartHandshake } from 'lucide-react';

export default function IntroSection() {
  const t = useTranslations('intro');

  const pillars = [
    {
      icon: BookOpen,
      title: t('pillar1Title'),
      desc: t('pillar1Desc'),
      accent: 'from-[#821C17] to-[#E49D4B]',
    },
    {
      icon: Compass,
      title: t('pillar2Title'),
      desc: t('pillar2Desc'),
      accent: 'from-[#E49D4B] to-[#C46B1E]',
    },
    {
      icon: HeartHandshake,
      title: t('pillar3Title'),
      desc: t('pillar3Desc'),
      accent: 'from-[#C46B1E] to-[#821C17]',
    },
  ];

  return (
    <section className="py-24 bg-linear-to-b from-[#FDF5E6] via-[#FCEBD2] to-[#FDF5E6] relative border-b border-[#F9DAB5] text-[#421A10]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3.5 mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#FCEBD2] border border-[#F9DAB5] text-[#821C17] text-xs font-semibold tracking-widest uppercase shadow-xs">
            <span>{t('eyebrow')}</span>
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-normal text-[#421A10] tracking-tight">
            {t('title')}
          </h2>
          {/* Ornamental Divider */}
          <div className="flex items-center justify-center gap-3 py-1">
            <span className="h-px w-16 bg-linear-to-r from-transparent to-[#E49D4B]" />
            <span className="w-2 h-2 rotate-45 bg-[#821C17]" />
            <span className="h-px w-16 bg-linear-to-l from-transparent to-[#E49D4B]" />
          </div>
          <p className="text-base sm:text-lg text-[#421A10]/80 leading-relaxed font-normal">
            {t('description')}
          </p>
        </div>

        {/* 3 Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {pillars.map((pillar, idx) => {
            const Icon = pillar.icon;
            return (
              <div
                key={idx}
                className="bg-[#FCEBD2]/75 rounded-2xl p-8 border border-[#F9DAB5] hover:border-[#E49D4B] shadow-xs hover:shadow-[0_12px_28px_rgba(66,26,16,0.08)] transition-all duration-300 hover:-translate-y-1 relative group overflow-hidden"
              >
                {/* Top decorative accent hairline */}
                <div
                  className={`absolute top-0 left-0 right-0 h-1 bg-linear-to-r ${pillar.accent}`}
                />

                <div className="w-12 h-12 rounded-xl bg-[#FDF5E6] border border-[#F9DAB5] flex items-center justify-center text-[#821C17] mb-6 shadow-xs group-hover:scale-105 group-hover:border-[#E49D4B] transition-all duration-300">
                  <Icon className="w-6 h-6 text-[#821C17]" />
                </div>

                <h3 className="font-serif text-xl font-bold text-[#421A10] mb-3 group-hover:text-[#821C17] transition-colors">
                  {pillar.title}
                </h3>

                <p className="text-sm text-[#421A10]/80 leading-relaxed">
                  {pillar.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
