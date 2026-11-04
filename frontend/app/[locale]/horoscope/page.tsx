import type { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import HoroscopeModule from '@/components/horoscope/HoroscopeModule';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;

  const titles: Record<string, string> = {
    en: 'Daily Horoscope & Planetary Transits | AstroLogic',
    hi: 'दैनिक राशिफल एवं ग्रह गोचर | एस्ट्रोलॉजिक',
    mr: 'दैनिक राशीभविष्य आणि ग्रह गोचर | ॲस्ट्रोलॉजिक',
  };

  const descriptions: Record<string, string> = {
    en: 'Dynamic transit-driven daily horoscope computed from live Swiss Ephemeris celestial positions, Lahiri Ayanamsha, and classical Vedic Jyotish principles.',
    hi: 'स्विस एफिमेरिस के सूक्ष्म खगोलीय गोचर पर आधारित वास्तविक दैनिक राशिफल, शुभ अंक, शुभ रंग और शास्त्रीय उपाय।',
    mr: 'स्विस एफिमेरिसवर आधारित अचूक दैनिक राशीभविष्य, ग्रह गोचर प्रभाव, शुभ अंक, शुभ रंग आणि वैदिक मार्गदर्शन.',
  };

  return {
    title: titles[locale] || titles.en,
    description: descriptions[locale] || descriptions.en,
  };
}

export default async function HoroscopePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <HoroscopeModule locale={locale} />;
}

