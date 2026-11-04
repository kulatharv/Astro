import type { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import KundaliModule from '@/components/kundali/KundaliModule';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;

  const titles: Record<string, string> = {
    en: 'Vedic Kundali & Birth Chart Calculator | AstroLogic',
    hi: 'वैदिक जन्म कुंडली एवं फलित ज्योतिष | एस्ट्रोलॉजिक',
    mr: 'वैदिक जन्म पत्रिका आणि कुंडली विश्लेषण | ॲस्ट्रोलॉजिक',
  };

  const descriptions: Record<string, string> = {
    en: 'Generate precise Vedic Janma Kundali with D1 & D9 Navamsha SVG charts, Navagraha longitudes, Vimshottari Dasha, Yogas, Doshas, and AI chart consultations.',
    hi: 'स्विस एफेमेरिस आधारित सूक्ष्म वैदिक जन्म चक्र, D1 एवं D9 नवमांश, नवग्रह स्थिति, विंशोत्तरी महादशा, सक्रिय योग एवं ग्रह दोष उपाय।',
    mr: 'स्विस एफिमेरिसवर आधारित अचूक वैदिक जन्म पत्रिका, D1 आणि D9 नवमांश चक्र, नवग्रह स्पष्ट स्थिती, विंशोत्तरी दशा आणि ज्योतिष AI सल्ला.',
  };

  return {
    title: titles[locale] || titles.en,
    description: descriptions[locale] || descriptions.en,
  };
}

export default async function KundaliPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <KundaliModule />;
}

