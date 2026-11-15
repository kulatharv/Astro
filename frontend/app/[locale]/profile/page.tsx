import type { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import ProfileView from '@/components/profile/ProfileView';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;

  const titles: Record<string, string> = {
    en: 'Cosmic Profile & Family Vault | AstroLogic',
    hi: 'कॉस्मिक प्रोफाइल एवं परिवार कुंडली वॉल्ट | एस्ट्रोलॉजिक',
    mr: 'कॉस्मिक प्रोफाइल आणि कुटुंब पत्रिका वॉल्ट | ॲस्ट्रोलॉजिक',
  };

  const descriptions: Record<string, string> = {
    en: 'Manage your personal Vedic birth coordinates, auto-calculated Cosmic Badges (Lagna, Moon Sign, Nakshatra, Dasha), multi-chart family vault, and WhatsApp daily forecasts.',
    hi: 'अपनी जन्म तिथि, समय, कॉस्मिक बैज (लग्न, राशि, नक्षत्र, महादशा), परिवार कुंडली वॉल्ट एवं व्हाट्सएप दैनिक राशिफल सेटिंग्स प्रबंधित करें।',
    mr: 'तुमची जन्म माहिती, कॉस्मिक बॅजेस (लग्न, चंद्र राशी, नक्षत्र, महादशा), कौटुंबिक पत्रिका वॉल्ट आणि व्हॉट्सॲप दैनिक अंदाज व्यवस्थापित करा.',
  };

  return {
    title: titles[locale] || titles.en,
    description: descriptions[locale] || descriptions.en,
  };
}

export default async function ProfilePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <ProfileView />;
}

