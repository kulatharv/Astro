'use client';

import { useTranslations } from 'next-intl';
import { Sparkles, Shield } from 'lucide-react';
import { Link } from '@/i18n/routing';
import LanguageSwitcher from './LanguageSwitcher';

export default function Footer() {
  const t = useTranslations('footer');
  const navT = useTranslations('navigation');

  return (
    <footer className="bg-[#421A10] text-[#FDF5E6] pt-16 pb-12 border-t border-[#821C17]/40 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-10 pb-12 border-b border-[#821C17]/30">
          {/* Brand & Sacred Motto */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-linear-to-br from-[#821C17] to-[#421A10] flex items-center justify-center text-[#E49D4B] shadow-sm border border-[#E49D4B]/40">
                <Sparkles className="w-5 h-5 text-[#E49D4B]" />
              </div>
              <div>
                <span className="font-serif text-2xl font-bold tracking-tight text-[#FDF5E6]">
                  {t('brand')}
                </span>
                <span className="text-[11px] block font-medium tracking-wide text-[#F3C387]">
                  {t('slogan')}
                </span>
              </div>
            </div>

            {/* Atharva Veda Motto */}
            <div className="p-4 rounded-xl bg-[#421A10]/90 border border-[#821C17]/40 space-y-1.5 shadow-sm">
              <p className="font-serif text-sm font-semibold text-[#F3C387] tracking-wide leading-relaxed">
                &ldquo;{t('motto')}&rdquo;
              </p>
              <p className="text-[11px] text-[#FCEBD2]/75 italic leading-relaxed">
                {t('mottoTrans')}
              </p>
            </div>

            <div className="pt-2 flex items-center gap-3">
              <span className="text-xs text-[#F3C387]">{navT('language')}:</span>
              <LanguageSwitcher />
            </div>
          </div>

          {/* Nav Links Column 1: Services */}
          <div className="lg:col-span-3 space-y-3">
            <h4 className="font-serif text-sm font-bold uppercase tracking-wider text-[#E49D4B]">
              {t('colServices')}
            </h4>
            <ul className="space-y-2 text-xs text-[#FCEBD2]/75">
              <li>
                <Link href="/kundali" className="hover:text-[#F3C387] transition-colors">
                  Janam Kundali (Lagna & Navamsha)
                </Link>
              </li>
              <li>
                <Link href="/predictions" className="hover:text-[#F3C387] transition-colors">
                  10 Life Predictions Domains
                </Link>
              </li>
              <li>
                <Link href="/panchang" className="hover:text-[#F3C387] transition-colors">
                  Daily Panchang & Muhurat
                </Link>
              </li>
              <li>
                <Link href="/horoscope" className="hover:text-[#F3C387] transition-colors">
                  Daily Horoscope & Transits
                </Link>
              </li>
              <li>
                <Link href="/predictions" className="hover:text-[#F3C387] transition-colors">
                  Vimshottari Dasha Timelines
                </Link>
              </li>
            </ul>
          </div>

          {/* Nav Links Column 2: Wisdom */}
          <div className="lg:col-span-4 space-y-3">
            <h4 className="font-serif text-sm font-bold uppercase tracking-wider text-[#E49D4B]">
              {t('colKnowledge')}
            </h4>
            <ul className="space-y-2 text-xs text-[#FCEBD2]/75">
              <li>
                <Link href="/blogs" className="hover:text-[#F3C387] transition-colors">
                  Brihat Parashara Hora Shastra
                </Link>
              </li>
              <li>
                <Link href="/blogs" className="hover:text-[#F3C387] transition-colors">
                  Swiss Ephemeris Precision Standards
                </Link>
              </li>
              <li>
                <Link href="/blogs" className="hover:text-[#F3C387] transition-colors">
                  Ayanamsha & Sidereal Mechanics
                </Link>
              </li>
              <li>
                <Link href="/blogs" className="hover:text-[#F3C387] transition-colors">
                  Sattvic Remedies & Karma Philosophy
                </Link>
              </li>
            </ul>

            <div className="pt-2">
              <div className="flex items-start gap-2 p-3 rounded-xl bg-[#821C17]/20 border border-[#821C17]/40 text-[11px] text-[#FCEBD2]/80">
                <Shield className="w-4 h-4 text-[#E49D4B] shrink-0 mt-0.5" />
                <span>Micro-arcsecond astronomical veracity calculated without fatalistic superstitions.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer Note */}
        <div className="py-6 border-b border-[#821C17]/30 space-y-1 text-center">
          <h5 className="text-xs font-semibold text-[#E49D4B] uppercase tracking-wider">
            {t('disclaimerTitle')}
          </h5>
          <p className="text-[11px] text-[#FCEBD2]/65 max-w-4xl mx-auto leading-relaxed">
            {t('disclaimerText')}
          </p>
        </div>

        {/* Copyright Bar */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-[#FCEBD2]/65 gap-4">
          <div className="flex items-center gap-1">
            <span>© {new Date().getFullYear()} AstroLogic. {t('rights')}</span>
          </div>

          <div className="flex items-center gap-6">
            <span className="hover:text-[#F3C387] cursor-pointer transition-colors">{t('privacy')}</span>
            <span className="hover:text-[#F3C387] cursor-pointer transition-colors">{t('terms')}</span>
            <span className="hover:text-[#F3C387] cursor-pointer transition-colors">{t('contact')}</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
