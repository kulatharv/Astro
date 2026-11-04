import type { Metadata } from 'next';
import { Cormorant_Garamond, Inter, Noto_Serif_Devanagari } from 'next/font/google';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages, setRequestLocale } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import '../globals.css';

const cormorant = Cormorant_Garamond({
  weight: ['400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-cormorant',
  display: 'swap',
});

const inter = Inter({
  weight: ['300', '400', '500', '600', '700'],
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const notoSerifDevanagari = Noto_Serif_Devanagari({
  weight: ['400', '500', '600', '700'],
  subsets: ['devanagari'],
  variable: '--font-devanagari',
  display: 'swap',
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const titles: Record<string, string> = {
    en: 'AstroLogic | Authentic Vedic Astrology & Planetary Intelligence',
    hi: 'एस्ट्रोलॉजिक | प्रामाणिक वैदिक ज्योतिष एवं खगोलीय प्रज्ञा',
    mr: 'ॲस्ट्रोलॉजिक | प्रामाणिक वैदिक ज्योतिष आणि खगोलीय विश्लेषण',
  };
  const descriptions: Record<string, string> = {
    en: 'Explore your Vedic birth chart, planetary cycles, and personalized astrological insights through traditional Jyotish principles and Swiss Ephemeris astronomical calculations.',
    hi: 'महर्षि पराशर परंपरा और स्विस एफेमेरिस की सूक्ष्म खगोलीय गणनाओं से अपनी जन्म कुंडली, ग्रह गोचर और 10 जीवन आयामों का प्रामाणिक विश्लेषण प्राप्त करें।',
    mr: 'महर्षी पराशर परंपरा आणि स्विस एफिमेरिसच्या अचूक खगोलीय गणनांवर आधारित जन्मकुंडली, गोचर आणि सखोल जीवन भविष्य.',
  };

  return {
    title: titles[locale] || titles.en,
    description: descriptions[locale] || descriptions.en,
    other: {
      google: 'notranslate',
    },
  };
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html
      lang={locale}
      translate="no"
      className={`${cormorant.variable} ${inter.variable} ${notoSerifDevanagari.variable} scroll-smooth notranslate`}
    >
      <head>
        <meta name="google" content="notranslate" />
        <meta name="robots" content="notranslate" />
        <meta name="msapplication-tap-highlight" content="no" />
        <meta httpEquiv="Content-Language" content={locale} />
        <meta name="format-detection" content="telephone=no" />
      </head>
      <body
        translate="no"
        className="min-h-screen flex flex-col bg-[#FAF6F0] text-[#24120B] font-sans antialiased selection:bg-[#7A1612] selection:text-[#FAF6F0] notranslate"
      >
        <NextIntlClientProvider messages={messages}>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
