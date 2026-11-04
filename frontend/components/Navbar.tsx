'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Menu, X, Sparkles } from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';
import { Link, usePathname } from '@/i18n/routing';

export default function Navbar() {
  const t = useTranslations('navigation');
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { href: '/' as const, label: t('home') },
    { href: '/panchang' as const, label: t('panchang') },
    { href: '/kundali' as const, label: t('kundali') },
    { href: '/predictions' as const, label: t('predictions') },
    { href: '/horoscope' as const, label: t('horoscope') },
    { href: '/blogs' as const, label: t('blogs') },
  ];

  return (
    <header suppressHydrationWarning className="sticky top-0 z-50 bg-[#FAF6F0]/92 backdrop-blur-md border-b border-[#C5A059]/25 transition-all shadow-[0_4px_20px_-4px_rgba(36,18,11,0.04)]">
      {/* Top ornamental luxury hairline */}
      <div className="h-0.5 w-full bg-linear-to-r from-transparent via-[#C5A059] to-transparent" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand */}
          <Link
            href="/"
            className="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-[#7A1612]/30 rounded-lg p-1"
          >
            <div className="w-10 h-10 rounded-full bg-linear-to-br from-[#7A1612] to-[#24120B] flex items-center justify-center text-[#F5E1BE] shadow-md border border-[#C5A059]/40 group-hover:scale-105 transition-transform duration-300">
              <Sparkles className="w-5 h-5 text-[#C5A059] group-hover:rotate-12 transition-transform duration-300" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-serif text-2xl font-bold tracking-tight text-[#7A1612] group-hover:text-[#24120B] transition-colors">
                  {t('brand')}
                </span>
                <span className="text-[10px] font-mono tracking-widest text-[#C5A059] uppercase px-1.5 py-0.5 rounded-sm bg-[#C5A059]/10 border border-[#C5A059]/30 font-semibold">
                  VEDIC
                </span>
              </div>
              <span className="text-[11px] font-medium tracking-wide text-[#A85A1E]">
                {t('brandSub')}
              </span>
            </div>
          </Link>

          {/* Desktop Nav */}
          <nav suppressHydrationWarning className="hidden lg:flex items-center gap-1">
            {navLinks.map((link) => {
              const isActive = link.href === '/'
                ? (pathname === '/' || pathname === '')
                : (pathname === link.href || pathname.startsWith(link.href + '/'));
              return (
                <Link
                  key={link.href}
                  href={link.href as any}
                  suppressHydrationWarning
                  className={`px-3 py-2 text-sm rounded-lg transition-all duration-150 relative group ${
                    isActive
                      ? 'text-[#7A1612] font-bold bg-[#F5EFE6] border border-[#C5A059]/30 shadow-2xs'
                      : 'text-[#24120B] font-medium hover:text-[#7A1612] hover:bg-[#F5EFE6]/70'
                  }`}
                >
                  <span suppressHydrationWarning>{link.label}</span>
                  <span
                    className={`absolute bottom-1 left-3 right-3 h-0.5 bg-[#7A1612] transition-transform duration-200 origin-center ${
                      isActive ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'
                    }`}
                  />
                </Link>
              );
            })}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden sm:flex items-center gap-3">
            <LanguageSwitcher />

            <Link
              href="/kundali"
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-lg text-[#FAF6F0] bg-linear-to-r from-[#7A1612] via-[#A85A1E] to-[#7A1612] hover:brightness-105 border border-[#C5A059]/40 shadow-xs hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#F5E1BE]" />
              <span>{t('generateKundali')}</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 sm:hidden">
            <LanguageSwitcher />
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-[#7A1612] hover:bg-[#F5EFE6] border border-[#C5A059]/30 focus:outline-none focus:ring-2 focus:ring-[#7A1612]/30 cursor-pointer"
              aria-label={mobileMenuOpen ? t('closeMenu') : t('openMenu')}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div suppressHydrationWarning className="lg:hidden border-t border-[#C5A059]/25 bg-[#FAF6F0] px-4 pt-3 pb-6 space-y-2 shadow-xl animate-in fade-in duration-200">
          <nav suppressHydrationWarning className="flex flex-col space-y-1">
            {navLinks.map((link) => {
              const isActive = link.href === '/'
                ? (pathname === '/' || pathname === '')
                : (pathname === link.href || pathname.startsWith(link.href + '/'));
              return (
                <Link
                  key={link.href}
                  href={link.href as any}
                  suppressHydrationWarning
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'text-[#7A1612] font-bold bg-[#F5EFE6] border border-[#C5A059]/30'
                      : 'text-[#24120B] font-medium hover:text-[#7A1612] hover:bg-[#F5EFE6]'
                  }`}
                >
                  <span suppressHydrationWarning>{link.label}</span>
                </Link>
              );
            })}
          </nav>
          <div className="pt-3 border-t border-[#C5A059]/20">
            <Link
              href="/kundali"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-semibold uppercase tracking-wider rounded-lg text-[#FAF6F0] bg-linear-to-r from-[#7A1612] to-[#A85A1E] border border-[#C5A059]/40 shadow-xs"
            >
              <Sparkles className="w-4 h-4 text-[#F5E1BE]" />
              <span>{t('generateKundali')}</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
