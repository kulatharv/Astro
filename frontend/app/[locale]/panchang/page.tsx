import type { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import PanchangModule from '@/components/panchang/PanchangModule';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;

  const titles: Record<string, string> = {
    en: 'Daily Panchang & Auspicious Muhurat | AstroLogic',
    hi: 'दैनिक पंचांग एवं शुभ मुहूर्त | एस्ट्रोलॉजिक',
    mr: 'दैनिक पंचांग आणि शुभ मुहूर्त | ॲस्ट्रोलॉजिक',
  };

  const descriptions: Record<string, string> = {
    en: 'Accurate daily Vedic Panchang with Tithi, Nakshatra, Yoga, Karana, Rahu Kaal, Abhijit Muhurat, Choghadiya, Horas, and Planetary Transits.',
    hi: 'स्विस एफेमेरिस एवं सूर्य सिद्धांत की शुद्ध गणनाओं पर आधारित दैनिक पंचांग, तिथि, नक्षत्र, योग, करण, राहुकाल, अभिजीत मुहूर्त, चौघड़िया एवं ग्रह गोचर।',
    mr: 'स्विस एफिमेरिस आणि सूर्य सिद्धांतावर आधारित दैनिक पंचांग, तिथी, नक्षत्र, योग, करण, राहुकाळ, अभिजीत मुहूर्त, चौघडिया आणि ग्रह गोचर.',
  };

  return {
    title: titles[locale] || titles.en,
    description: descriptions[locale] || descriptions.en,
  };
}

export default async function PanchangPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <PanchangModule />;
}
