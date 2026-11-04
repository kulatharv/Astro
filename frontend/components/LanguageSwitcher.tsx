'use client';

import { useLocale } from 'next-intl';
import { useState } from 'react';
import { Globe, Check, ChevronDown } from 'lucide-react';
import { useRouter, usePathname } from '@/i18n/routing';

const languages = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
];

export default function LanguageSwitcher() {
  const currentLocale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const handleLanguageChange = (nextLocale: string) => {
    if (nextLocale === currentLocale) {
      setIsOpen(false);
      return;
    }
    setIsOpen(false);
    // Smooth client-side transition without full page teardown / dev rebuild
    router.replace(pathname, { locale: nextLocale });
  };

  const currentLang = languages.find((l) => l.code === currentLocale) || languages[0];

  return (
    <div className="relative inline-block text-left">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded-lg bg-[#FDF5E6] border border-[#F9DAB5] text-[#821C17] hover:bg-[#FCEBD2] hover:border-[#821C17] transition-colors focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 shadow-xs cursor-pointer"
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="Select Language"
      >
        <Globe className="w-3.5 h-3.5 text-[#E49D4B]" />
        <span className="font-serif tracking-wide">{currentLang.nativeName}</span>
        <ChevronDown className={`w-3 h-3 text-[#C46B1E] transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          <div
            className="absolute right-0 mt-2 w-38 rounded-xl bg-[#FDF5E6] border border-[#F9DAB5] shadow-xl z-50 py-1.5 ring-1 ring-black/5"
            role="menu"
            aria-orientation="vertical"
          >
            <div className="px-3 py-1 text-[10px] font-semibold tracking-wider text-[#C46B1E] uppercase border-b border-[#F9DAB5] mb-1">
              Language / भाषा
            </div>
            {languages.map((lang) => {
              const isSelected = lang.code === currentLocale;
              return (
                <button
                  key={lang.code}
                  type="button"
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between transition-colors cursor-pointer ${
                    isSelected
                      ? 'bg-[#821C17]/10 text-[#821C17] font-bold'
                      : 'text-[#421A10] hover:bg-[#FCEBD2] hover:text-[#821C17]'
                  }`}
                  role="menuitem"
                >
                  <span className="font-serif">{lang.nativeName}</span>
                  {isSelected && <Check className="w-3.5 h-3.5 text-[#821C17]" />}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
