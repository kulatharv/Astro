import { redirect } from '@/i18n/routing';

export default async function BlogAliasPage({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}) {
  const { locale, slug } = await params;
  redirect({ href: `/blogs/${slug}` as any, locale });
}

