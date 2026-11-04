import type { Metadata } from 'next';
import { setRequestLocale } from 'next-intl/server';
import BlogDetailModule from '@/components/blog/BlogDetailModule';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;

  return {
    title: `${slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())} | AstroLogic`,
    description: 'Explore in-depth Vedic astrology wisdom and classical planetary insights.',
  };
}

export default async function BlogDetailPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  return <BlogDetailModule slug={slug} locale={locale} />;
}

