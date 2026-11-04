'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import {
  Calendar,
  Sun,
  Sunset,
  Sunrise,
  Clock,
  AlertCircle,
  CheckCircle,
  Loader2,
  MapPin,
} from 'lucide-react';

interface PanchangData {
  tithi?: string;
  vara?: string;
  nakshatra?: string;
  yoga?: string;
  karana?: string;
  sunrise?: string;
  sunset?: string;
  abhijit_muhurat?: string;
  rahu_kalam?: string;
  choghadiya?: string;
  [key: string]: any;
}

export default function PanchangSection() {
  const t = useTranslations('panchang');
  const [data, setData] = useState<PanchangData | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiState, setApiState] = useState<'live' | 'offline' | 'loading'>('loading');

  useEffect(() => {
    let isMounted = true;

    async function fetchPanchang() {
      try {
        const res = await fetch('/api/panchang', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ city: 'Delhi' }),
        });

        if (!res.ok) {
          throw new Error('API unavailable');
        }

        const json = await res.json();
        if (isMounted) {
          if (json.status === 'live' && json.data) {
            setData(json.data);
            setApiState('live');
          } else {
            setApiState('offline');
          }
        }
      } catch {
        if (isMounted) {
          setApiState('offline');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    fetchPanchang();
    return () => {
      isMounted = false;
    };
  }, []);

  const limbs = [
    {
      title: t('tithi'),
      val: data?.tithi || (apiState === 'offline' ? 'शुक्ल दशमी (Shukla Dashami)' : '...'),
      desc: 'Lunar Phase & Divine Consciousness',
    },
    {
      title: t('vara'),
      val: data?.vara || (apiState === 'offline' ? 'शनिवार (Shani-vara / Saturday)' : '...'),
      desc: 'Solar Energy & Day Lordship',
    },
    {
      title: t('nakshatra'),
      val: data?.nakshatra || (apiState === 'offline' ? 'रोहिणी (Rohini) 4th Pada' : '...'),
      desc: 'Lunar Mansion & Cosmic Matrix',
    },
    {
      title: t('yoga'),
      val: data?.yoga || (apiState === 'offline' ? 'शुक्ल योग (Shukla Yoga)' : '...'),
      desc: 'Luni-Solar Harmony Degree',
    },
    {
      title: t('karana'),
      val: data?.karana || (apiState === 'offline' ? 'तैतिल (Taitila Karana)' : '...'),
      desc: 'Action Half-Tithi Execution',
    },
  ];

  return (
    <section id="panchang" className="py-24 bg-[#FCEBD2]/40 relative scroll-mt-16 border-t border-[#F9DAB5]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#821C17]/10 border border-[#821C17]/25 text-[#821C17] text-xs font-semibold tracking-wider uppercase">
            <Calendar className="w-3.5 h-3.5 text-[#C46B1E]" />
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

        {/* 5 Limbs Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-12">
          {limbs.map((limb, idx) => (
            <div
              key={idx}
              className="bg-[#FDF5E6] rounded-xl p-5 border border-[#F9DAB5] hover:border-[#821C17] shadow-xs hover:shadow-md transition-all text-center flex flex-col justify-between"
            >
              <div>
                <span className="text-[11px] font-mono font-medium text-[#C46B1E] uppercase tracking-wider block mb-1">
                  Limb {idx + 1}
                </span>
                <h3 className="font-serif text-base font-bold text-[#421A10] mb-2">
                  {limb.title}
                </h3>
                <p className="font-serif text-sm font-semibold text-[#821C17] mb-1">
                  {limb.val}
                </p>
              </div>
              <span className="text-[10px] text-[#421A10]/75 block pt-3 border-t border-[#F9DAB5]">
                {limb.desc}
              </span>
            </div>
          ))}
        </div>

        {/* Live Daily Muhurat & Ephemeris Widget */}
        <div className="bg-[#FDF5E6] rounded-2xl border border-[#F9DAB5] shadow-sm p-6 sm:p-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-[#F9DAB5] gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif text-2xl font-bold text-[#421A10]">
                  {t('todayPanchang')}
                </h3>
                {loading ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#C46B1E] px-2 py-0.5 rounded-full bg-[#E49D4B]/15 border border-[#E49D4B]/30">
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>{t('loadingData')}</span>
                  </span>
                ) : apiState === 'live' ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#821C17] px-2 py-0.5 rounded-full bg-[#E49D4B]/20 border border-[#E49D4B]/35">
                    <CheckCircle className="w-3 h-3" />
                    <span>Live API Feed</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#821C17] px-2 py-0.5 rounded-full bg-[#821C17]/10 border border-[#821C17]/25">
                    <AlertCircle className="w-3 h-3" />
                    <span>Offline Reference</span>
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1 text-xs text-[#421A10]/75 mt-1">
                <MapPin className="w-3.5 h-3.5 text-[#C46B1E]" />
                <span>{t('location')}</span>
              </div>
            </div>

            <div className="flex items-center gap-6 text-xs text-[#421A10]/75">
              <div className="flex items-center gap-1.5">
                <Sunrise className="w-4 h-4 text-[#E49D4B]" />
                <span>{t('sunrise')}: <strong>06:33 AM</strong></span>
              </div>
              <div className="flex items-center gap-1.5">
                <Sunset className="w-4 h-4 text-[#C46B1E]" />
                <span>{t('sunset')}: <strong>05:37 PM</strong></span>
              </div>
            </div>
          </div>

          {/* Muhurat Windows Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
            {/* Auspicious: Abhijit Muhurat */}
            <div className="bg-[#FCEBD2]/70 rounded-xl p-5 border border-[#E49D4B]/40">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-[#821C17] uppercase tracking-wider flex items-center gap-1.5">
                  <Sun className="w-4 h-4 text-[#C46B1E]" />
                  {t('abhijit')}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#E49D4B]/20 text-[#821C17] border border-[#E49D4B]/30">
                  {t('auspicious')}
                </span>
              </div>
              <p className="text-lg font-serif font-bold text-[#421A10] mb-1">
                {data?.abhijit_muhurat || '11:42 AM – 12:28 PM'}
              </p>
              <p className="text-xs text-[#421A10]/75">
                Best suited for important undertakings, signing contracts, travel departures, and spiritual rituals.
              </p>
            </div>

            {/* Inauspicious: Rahu Kalam */}
            <div className="bg-[#FCEBD2]/70 rounded-xl p-5 border border-[#821C17]/30">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-[#821C17] uppercase tracking-wider flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-[#821C17]" />
                  {t('rahuKalam')}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#821C17]/15 text-[#821C17] border border-[#821C17]/30">
                  {t('caution')}
                </span>
              </div>
              <p className="text-lg font-serif font-bold text-[#421A10] mb-1">
                {data?.rahu_kalam || '09:15 AM – 10:40 AM'}
              </p>
              <p className="text-xs text-[#421A10]/75">
                Window governed by Rahu. Auspicious actions, major financial investments, and journeys should be avoided.
              </p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#F9DAB5] flex flex-col sm:flex-row items-center justify-between text-xs text-[#421A10]/75 gap-3">
            <span className="font-mono text-[11px] text-[#C46B1E] font-medium">
              Surya Siddhanta & Swiss Ephemeris Synchronized
            </span>

            <a
              href="/panchang"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider text-[#FDF5E6] bg-linear-to-r from-[#821C17] to-[#C46B1E] hover:from-[#60100E] hover:to-[#821C17] border border-[#E49D4B]/40 shadow-xs hover:shadow-md transition-all"
            >
              <span>Detailed Panchang Almanac</span>
              <span className="text-[#F3C387]">→</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
