import type { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import BlogListModule from '@/components/blog/BlogListModule';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;

  const titles: Record<string, string> = {
    en: 'Vedic Astrology Articles & Wisdom | AstroLogic',
    hi: 'वैदिक ज्योतिष लेख एवं ज्ञान सागर | एस्ट्रोलॉजिक',
    mr: 'वैदिक ज्योतिष लेख आणि ज्ञान भांडार | ॲस्ट्रोलॉजिक',
  };

  const descriptions: Record<string, string> = {
    en: 'In-depth articles on classical Vedic Jyotish, Navagrahas, 27 Nakshatras, Vimshottari Dasha timing, Raj Yogas, and remedial wisdom.',
    hi: 'वैदिक ज्योतिष, नवग्रह, २७ नक्षत्र, विंशोत्तरी महादशा, राजयोग एवं शास्त्रीय उपायों पर प्रमाणिक आलेख।',
    mr: 'वैदिक ज्योतिष, नवग्रह, २७ नक्षत्रे, दशा विचार, राजयोग आणि प्रभावी वैदिक उपायांवरील सखोल लेख.',
  };

  return {
    title: titles[locale] || titles.en,
    description: descriptions[locale] || descriptions.en,
  };
}

export default async function BlogsPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return <BlogListModule locale={locale} />;
}

