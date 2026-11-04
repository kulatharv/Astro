import { setRequestLocale } from 'next-intl/server';
import HeroSection from '@/components/HeroSection';
import IntroSection from '@/components/IntroSection';
import ServicesSection from '@/components/ServicesSection';
import KundaliSection from '@/components/KundaliSection';
import PredictionsSection from '@/components/PredictionsSection';
import PlanetarySection from '@/components/PlanetarySection';
import PanchangSection from '@/components/PanchangSection';
import KnowledgeSection from '@/components/KnowledgeSection';
import ClosingCTA from '@/components/ClosingCTA';

export default async function HomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="flex flex-col w-full">
      {/* 1. Hero Section with 3D Orrery & Celestial Metrics */}
      <HeroSection />

      {/* 2. Daily Panchang & Muhurat Almanac (Dynamic Daily Time) */}
      <PanchangSection />

      {/* 3. Kundali Birth Chart Observatory (Personal Natal Matrix) */}
      <KundaliSection />

      {/* 4. 10-Domain Life Predictions (Destiny & Dasha Insights) */}
      <PredictionsSection />

      {/* 5. Complete Services Directory (All 6 Interactive Modules) */}
      <ServicesSection />

      {/* 6. Navagraha Planetary Archetypes & Dignities */}
      <PlanetarySection />

      {/* 7. Vedic Knowledge Treatises & Articles */}
      <KnowledgeSection />

      {/* 8. AstroLogic Astronomical Foundation & Pillars */}
      <IntroSection />

      {/* 9. Closing Auspicious CTA */}
      <ClosingCTA />
    </div>
  );
}
