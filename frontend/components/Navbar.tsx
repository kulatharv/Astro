'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  Menu,
  X,
  Sparkles,
  User,
  Compass,
  Calendar,
  Layers,
  Sparkle,
  BookOpen,
  SunMedium,
} from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';
import { Link, usePathname } from '@/i18n/routing';
import { useAuth } from './auth/AuthContext';

export default function Navbar() {
  const t = useTranslations('navigation');
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, isAuthenticated, openAuthModal } = useAuth();

  // 6 primary destinations (Profile has its own dedicated button in actions & top drawer card)
  const navLinks = [
    { href: '/' as const, label: t('home'), icon: Compass },
    { href: '/panchang' as const, label: t('panchang'), icon: Calendar },
    { href: '/kundali' as const, label: t('kundali'), icon: Layers },
    { href: '/predictions' as const, label: t('predictions'), icon: Sparkle },
    { href: '/horoscope' as const, label: t('horoscope'), icon: SunMedium },
    { href: '/blogs' as const, label: t('blogs'), icon: BookOpen },
  ];

  return (
    <header
      suppressHydrationWarning
      className="sticky top-0 z-50 bg-[#FAF6F0]/96 backdrop-blur-md border-b border-[#C5A059]/30 transition-all shadow-[0_2px_15px_-3px_rgba(36,18,11,0.06)]"
    >
      {/* Top ornamental luxury hairline */}
      <div className="h-0.5 sm:h-1 w-full bg-linear-to-r from-[#7A1612] via-[#C5A059] to-[#7A1612]" />

      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20 gap-2 sm:gap-4">
          {/* Brand */}
          <Link
            href="/"
            className="flex items-center gap-2.5 sm:gap-3 group focus:outline-none focus:ring-2 focus:ring-[#7A1612]/30 rounded-lg p-1 shrink-0"
          >
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-linear-to-br from-[#7A1612] to-[#24120B] flex items-center justify-center text-[#F5E1BE] shadow-md border border-[#C5A059]/40 group-hover:scale-105 transition-transform duration-300 shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-[#C5A059] group-hover:rotate-12 transition-transform duration-300" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-serif text-xl sm:text-2xl font-bold tracking-tight text-[#7A1612] group-hover:text-[#24120B] transition-colors leading-tight">
                  {t('brand')}
                </span>
                <span className="text-[9px] sm:text-[10px] font-mono tracking-widest text-[#C5A059] uppercase px-1 sm:px-1.5 py-0.5 rounded-sm bg-[#C5A059]/10 border border-[#C5A059]/30 font-semibold leading-none">
                  VEDIC
                </span>
              </div>
              <span className="hidden sm:inline-block text-[10px] sm:text-[11px] font-medium tracking-wide text-[#A85A1E] truncate max-w-[200px] md:max-w-none mt-0.5">
                {t('brandSub')}
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav
            suppressHydrationWarning
            className="hidden lg:flex items-center gap-0.5 xl:gap-1"
          >
            {navLinks.map((link) => {
              const isActive =
                link.href === '/'
                  ? pathname === '/' || pathname === ''
                  : pathname === link.href || pathname.startsWith(link.href + '/');
              return (
                <Link
                  key={link.href}
                  href={link.href as any}
                  suppressHydrationWarning
                  className={`px-2 xl:px-3 py-1.5 xl:py-2 text-xs xl:text-sm rounded-lg transition-all duration-150 relative group whitespace-nowrap ${
                    isActive
                      ? 'text-[#7A1612] font-bold bg-[#F5EFE6] border border-[#C5A059]/30 shadow-2xs'
                      : 'text-[#24120B] font-medium hover:text-[#7A1612] hover:bg-[#F5EFE6]/70'
                  }`}
                >
                  <span suppressHydrationWarning>{link.label}</span>
                  <span
                    className={`absolute bottom-1 left-2 right-2 xl:left-3 xl:right-3 h-0.5 bg-[#7A1612] transition-transform duration-200 origin-center ${
                      isActive ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'
                    }`}
                  />
                </Link>
              );
            })}
          </nav>

          {/* Desktop Actions */}
          <div className="hidden lg:flex items-center gap-2 xl:gap-3 shrink-0">
            <LanguageSwitcher />

            {isAuthenticated ? (
              <Link
                href="/profile"
                className="h-9 w-9 xl:h-10 xl:w-10 flex items-center justify-center rounded-lg text-[#7A1612] bg-[#F5EFE6] hover:bg-[#FAF6F0] border border-[#C5A059]/40 transition-colors shadow-2xs group relative"
                title={`${user?.name || 'User'} (Cosmic Vault)`}
                aria-label={t('profile')}
              >
                <span className="font-serif font-bold text-xs text-[#7A1612]">
                  {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
                </span>
                <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-600 border border-white" />
              </Link>
            ) : (
              <button
                type="button"
                onClick={() => openAuthModal({ reason: 'login' })}
                className="h-9 w-9 xl:h-10 xl:w-10 flex items-center justify-center rounded-lg text-[#7A1612] hover:bg-[#F5EFE6] border border-[#C5A059]/30 transition-colors shadow-2xs group relative cursor-pointer"
                title={t('profile')}
                aria-label={t('profile')}
              >
                <User className="w-4 h-4 text-[#7A1612] group-hover:scale-110 transition-transform" />
              </button>
            )}

            <Link
              href="/kundali"
              className="inline-flex items-center gap-1.5 xl:gap-2 px-3 xl:px-4 py-2 xl:py-2.5 text-[11px] xl:text-xs font-semibold uppercase tracking-wider rounded-lg text-[#FAF6F0] bg-linear-to-r from-[#7A1612] via-[#A85A1E] to-[#7A1612] hover:brightness-105 border border-[#C5A059]/40 shadow-xs hover:shadow-md transition-all duration-200 hover:-translate-y-0.5 cursor-pointer whitespace-nowrap"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#F5E1BE] shrink-0" />
              <span>{t('generateKundali')}</span>
            </Link>
          </div>

          {/* Mobile & Tablet Actions */}
          <div className="flex lg:hidden items-center gap-1.5 sm:gap-2 shrink-0">
            <LanguageSwitcher />

            <Link
              href="/profile"
              className="hidden sm:flex min-w-[40px] min-h-[40px] items-center justify-center rounded-lg text-[#7A1612] hover:bg-[#F5EFE6] border border-[#C5A059]/30 transition-colors shadow-2xs"
              title={t('profile')}
              aria-label={t('profile')}
            >
              <User className="w-4 h-4 sm:w-5 sm:h-5 text-[#7A1612]" />
            </Link>

            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="min-w-[40px] min-h-[40px] sm:min-w-[44px] sm:min-h-[44px] flex items-center justify-center rounded-lg text-[#7A1612] hover:bg-[#F5EFE6] border border-[#C5A059]/30 focus:outline-none focus:ring-2 focus:ring-[#7A1612]/30 cursor-pointer shadow-2xs"
              aria-label={mobileMenuOpen ? t('closeMenu') : t('openMenu')}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5 sm:w-6 sm:h-6" />
              ) : (
                <Menu className="w-5 h-5 sm:w-6 sm:h-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile & Tablet Drawer */}
      {mobileMenuOpen && (
        <div
          suppressHydrationWarning
          className="lg:hidden border-t border-[#C5A059]/30 bg-[#FAF6F0] px-4 pt-3 pb-6 space-y-3 shadow-2xl animate-in fade-in duration-200 max-h-[85vh] overflow-y-auto"
        >
          {/* Quick Cosmic Profile Card (prominent on mobile) */}
          {isAuthenticated ? (
            <Link
              href="/profile"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center justify-between p-3 rounded-xl bg-linear-to-r from-[#7A1612]/10 via-[#C5A059]/15 to-[#7A1612]/10 border border-[#C5A059]/40 hover:border-[#7A1612]/50 transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-[#7A1612] flex items-center justify-center text-[#F5E1BE] shadow-xs">
                  <User className="w-4 h-4 text-[#C5A059]" />
                </div>
                <div>
                  <div className="text-xs font-serif font-bold text-[#7A1612] group-hover:text-[#24120B]">
                    {user?.name || t('profile')}
                  </div>
                  <div className="text-[10px] text-[#A85A1E] font-medium">
                    {user?.cosmic_badges?.lagna_sign
                      ? `${user.cosmic_badges.lagna_sign} Lagna · ${user.cosmic_badges.moon_sign || ''} Moon`
                      : 'Cosmic Badges · Family Vault · WhatsApp Alerts'}
                  </div>
                </div>
              </div>
              <span className="text-xs text-[#7A1612] font-semibold group-hover:translate-x-0.5 transition-transform">
                →
              </span>
            </Link>
          ) : (
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                openAuthModal({ reason: 'login' });
              }}
              className="w-full text-left flex items-center justify-between p-3 rounded-xl bg-linear-to-r from-[#7A1612]/10 via-[#C5A059]/15 to-[#7A1612]/10 border border-[#C5A059]/40 hover:border-[#7A1612]/50 transition-all group cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-[#7A1612] flex items-center justify-center text-[#F5E1BE] shadow-xs">
                  <Sparkles className="w-4 h-4 text-[#C5A059]" />
                </div>
                <div>
                  <div className="text-xs font-serif font-bold text-[#7A1612] group-hover:text-[#24120B]">
                    Claim Your Cosmic Vault
                  </div>
                  <div className="text-[10px] text-[#A85A1E] font-medium">
                    1-Tap Google / WhatsApp · Never Re-enter Data
                  </div>
                </div>
              </div>
              <span className="text-xs text-[#7A1612] font-semibold group-hover:translate-x-0.5 transition-transform">
                →
              </span>
            </button>
          )}

          {/* Navigation Links */}
          <nav suppressHydrationWarning className="flex flex-col space-y-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive =
                link.href === '/'
                  ? pathname === '/' || pathname === ''
                  : pathname === link.href || pathname.startsWith(link.href + '/');
              return (
                <Link
                  key={link.href}
                  href={link.href as any}
                  suppressHydrationWarning
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-3 py-2.5 rounded-lg text-sm flex items-center gap-3 transition-colors ${
                    isActive
                      ? 'text-[#7A1612] font-bold bg-[#F5EFE6] border border-[#C5A059]/30'
                      : 'text-[#24120B] font-medium hover:text-[#7A1612] hover:bg-[#F5EFE6]'
                  }`}
                >
                  <Icon className="w-4 h-4 text-[#C5A059] shrink-0" />
                  <span suppressHydrationWarning>{link.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Bottom Action CTA */}
          <div className="pt-2 border-t border-[#C5A059]/20">
            <Link
              href="/kundali"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 text-xs font-semibold uppercase tracking-wider rounded-xl text-[#FAF6F0] bg-linear-to-r from-[#7A1612] via-[#A85A1E] to-[#7A1612] border border-[#C5A059]/40 shadow-sm"
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
