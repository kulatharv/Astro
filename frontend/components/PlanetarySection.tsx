'use client';

import { useTranslations } from 'next-intl';
import { Sun, Moon, Flame, Zap, Award, Sparkles, Hourglass, Orbit, Compass } from 'lucide-react';

export default function PlanetarySection() {
  const t = useTranslations('planetary');

  const grahas = [
    {
      name: t('sun'),
      symbol: '☉',
      role: t('sunRole'),
      gem: 'Ruby (माणिक्य)',
      metal: 'Gold / Copper',
      icon: Sun,
      color: 'from-[#821C17] to-[#E49D4B]',
    },
    {
      name: t('moon'),
      symbol: '☽',
      role: t('moonRole'),
      gem: 'Pearl (मोती)',
      metal: 'Silver',
      icon: Moon,
      color: 'from-[#E49D4B] to-[#FCEBD2]',
    },
    {
      name: t('mars'),
      symbol: '♂',
      role: t('marsRole'),
      gem: 'Coral (मूंगा)',
      metal: 'Copper',
      icon: Flame,
      color: 'from-[#821C17] to-[#C46B1E]',
    },
    {
      name: t('mercury'),
      symbol: '☿',
      role: t('mercuryRole'),
      gem: 'Emerald (पन्ना)',
      metal: 'Brass / Bronze',
      icon: Zap,
      color: 'from-[#C46B1E] to-[#E49D4B]',
    },
    {
      name: t('jupiter'),
      symbol: '♃',
      role: t('jupiterRole'),
      gem: 'Yellow Sapphire (पुखराज)',
      metal: 'Gold',
      icon: Award,
      color: 'from-[#E49D4B] to-[#821C17]',
    },
    {
      name: t('venus'),
      symbol: '♀',
      role: t('venusRole'),
      gem: 'Diamond (हीरा)',
      metal: 'Silver / Platinum',
      icon: Sparkles,
      color: 'from-[#F3C387] to-[#E49D4B]',
    },
    {
      name: t('saturn'),
      symbol: '♄',
      role: t('saturnRole'),
      gem: 'Blue Sapphire (नीलम)',
      metal: 'Iron',
      icon: Hourglass,
      color: 'from-[#421A10] to-[#821C17]',
    },
    {
      name: t('rahu'),
      symbol: '☊',
      role: t('rahuRole'),
      gem: 'Hessonite (गोमेद)',
      metal: 'Mixed Alloys',
      icon: Orbit,
      color: 'from-[#821C17] to-[#421A10]',
    },
    {
      name: t('ketu'),
      symbol: '☋',
      role: t('ketuRole'),
      gem: 'Cat’s Eye (लहसुनिया)',
      metal: 'Lead',
      icon: Compass,
      color: 'from-[#C46B1E] to-[#421A10]',
    },
  ];

  return (
    <section className="py-24 bg-[#FDF5E6] relative border-t border-[#F9DAB5]">
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

        {/* 9 Navagrahas Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {grahas.map((graha, idx) => {
            const Icon = graha.icon;
            return (
              <div
                key={idx}
                className="bg-[#FCEBD2] rounded-xl p-6 border border-[#F9DAB5] hover:border-[#821C17] shadow-xs hover:shadow-lg transition-all duration-300 hover:-translate-y-1 relative group overflow-hidden"
              >
                <div className="flex items-start gap-4">
                  {/* Planet Icon & Symbol */}
                  <div className="w-12 h-12 rounded-xl bg-linear-to-br from-[#FDF5E6] to-[#FCEBD2] border border-[#F9DAB5] flex items-center justify-center shrink-0 shadow-xs group-hover:scale-105 transition-transform">
                    <Icon className="w-6 h-6 text-[#821C17]" />
                  </div>

                  {/* Planet Info */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-serif text-xl font-bold text-[#421A10] group-hover:text-[#821C17] transition-colors">
                        {graha.name}
                      </h3>
                      <span className="text-sm font-mono text-[#C46B1E] font-bold">
                        {graha.symbol}
                      </span>
                    </div>
                    <p className="text-xs text-[#421A10]/75 font-medium leading-relaxed">
                      {graha.role}
                    </p>
                    <div className="pt-2 flex flex-wrap gap-2 text-[10px] text-[#821C17]">
                      <span className="px-2 py-0.5 rounded bg-[#FDF5E6] border border-[#F9DAB5]">
                        {graha.gem}
                      </span>
                      <span className="px-2 py-0.5 rounded bg-[#FDF5E6] border border-[#F9DAB5]">
                        {graha.metal}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
