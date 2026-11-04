'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';
import {
  Briefcase,
  Heart,
  Coins,
  Activity,
  GraduationCap,
  Users,
  Home,
  ShieldAlert,
  Plane,
  Flame,
  ArrowRight,
} from 'lucide-react';

export default function PredictionsSection() {
  const t = useTranslations('predictions');

  const domains = [
    {
      id: 'career',
      title: t('d1'),
      house: t('d1House'),
      desc: t('d1Desc'),
      icon: Briefcase,
      color: 'text-[#821C17]',
    },
    {
      id: 'marriage',
      title: t('d2'),
      house: t('d2House'),
      desc: t('d2Desc'),
      icon: Heart,
      color: 'text-[#C46B1E]',
    },
    {
      id: 'wealth',
      title: t('d3'),
      house: t('d3House'),
      desc: t('d3Desc'),
      icon: Coins,
      color: 'text-[#E49D4B]',
    },
    {
      id: 'health',
      title: t('d4'),
      house: t('d4House'),
      desc: t('d4Desc'),
      icon: Activity,
      color: 'text-[#821C17]',
    },
    {
      id: 'education',
      title: t('d5'),
      house: t('d5House'),
      desc: t('d5Desc'),
      icon: GraduationCap,
      color: 'text-[#421A10]',
    },
    {
      id: 'children',
      title: t('d6'),
      house: t('d6House'),
      desc: t('d6Desc'),
      icon: Users,
      color: 'text-[#C46B1E]',
    },
    {
      id: 'property',
      title: t('d7'),
      house: t('d7House'),
      desc: t('d7Desc'),
      icon: Home,
      color: 'text-[#E49D4B]',
    },
    {
      id: 'obstacles',
      title: t('d8'),
      house: t('d8House'),
      desc: t('d8Desc'),
      icon: ShieldAlert,
      color: 'text-[#821C17]',
    },
    {
      id: 'travel',
      title: t('d9'),
      house: t('d9House'),
      desc: t('d9Desc'),
      icon: Plane,
      color: 'text-[#C46B1E]',
    },
    {
      id: 'spirituality',
      title: t('d10'),
      house: t('d10House'),
      desc: t('d10Desc'),
      icon: Flame,
      color: 'text-[#421A10]',
    },
  ];

  return (
    <section id="predictions" className="py-24 bg-[#FCEBD2]/35 relative scroll-mt-16 border-t border-[#F9DAB5]">
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

        {/* 10 Domains Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
          {domains.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.id}
                href="/predictions"
                className="bg-[#FDF5E6] rounded-xl p-6 border border-[#F9DAB5] hover:border-[#821C17] shadow-xs hover:shadow-lg transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between group cursor-pointer"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-lg bg-[#FCEBD2] border border-[#F9DAB5] flex items-center justify-center group-hover:bg-[#821C17] transition-colors duration-300">
                      <Icon className={`w-5 h-5 ${item.color} group-hover:text-[#FDF5E6] transition-colors`} />
                    </div>
                  </div>

                  <span className="text-[11px] font-mono text-[#C46B1E] font-semibold block mb-1">
                    {item.house}
                  </span>

                  <h3 className="font-serif text-lg font-bold text-[#421A10] mb-2 group-hover:text-[#821C17] transition-colors">
                    {item.title}
                  </h3>

                  <p className="text-xs text-[#421A10]/75 leading-relaxed">
                    {item.desc}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-[#F9DAB5] flex items-center justify-between text-[11px] text-[#C46B1E] group-hover:text-[#821C17] font-semibold">
                  <span>Explore Forecast</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
}
